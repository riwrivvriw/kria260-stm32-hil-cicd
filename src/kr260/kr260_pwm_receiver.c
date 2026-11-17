/**
 * @file kr260_pwm_receiver.c
 * @brief ไดรเวอร์ตรวจวัดสัญญาณ PWM จากบอร์ด Kria KR260 (Airpump Output)
 * @details ใช้สถาปัตยกรรม GPIO Dual-Edge Interrupt ร่วมกับ Zephyr Hardware Cycle Counter (DWT)
 *          เพื่อให้วัด Duty Cycle และ Frequency ได้ความแม่นยำระดับนาโนวินาทีบน Cortex-M33
 */

#include "kr260_pwm_receiver.h"
#include <zephyr/drivers/gpio.h>
#include <zephyr/logging/log.h>
#include <zephyr/sys/util.h>

LOG_MODULE_REGISTER(kr260_pwm, LOG_LEVEL_INF);

/* -------------------------------------------------------------------------- */
/* การตั้งค่าพินรับสัญญาณ PWM จาก KR260 ผ่าน DeviceTree Alias                */
/* -------------------------------------------------------------------------- */
#if DT_NODE_EXISTS(DT_ALIAS(kr260_pwm))
static const struct gpio_dt_spec pwm_gpio = GPIO_DT_SPEC_GET(DT_ALIAS(kr260_pwm), gpios);
#else
#error "DeviceTree alias 'kr260-pwm' is not defined in app.overlay!"
#endif

static struct gpio_callback pwm_cb_data;

/* ตัวแปรเก็บสถานะการวัดสัญญาณ PWM */
static volatile uint32_t g_last_rising_cycle = 0;
static volatile uint32_t g_high_time_cycles = 0;
static volatile uint32_t g_period_cycles = 0;
static volatile uint32_t g_last_edge_uptime_ms = 0;

static volatile float    g_current_duty_cycle = 0.0f;
static volatile uint32_t g_current_frequency_hz = 0;
static volatile bool     g_signal_active = false;

static struct k_spinlock g_pwm_lock;

/* -------------------------------------------------------------------------- */
/* Interrupt Service Routine (ISR): ดักจับทั้ง Rising Edge และ Falling Edge    */
/* -------------------------------------------------------------------------- */
static void pwm_gpio_callback(const struct device *dev, struct gpio_callback *cb, uint32_t pins)
{
    ARG_UNUSED(dev);
    ARG_UNUSED(cb);
    ARG_UNUSED(pins);

    uint32_t now_cycles = k_cycle_get_32();
    int pin_val = gpio_pin_get_dt(&pwm_gpio);

    k_spinlock_key_t key = k_spin_lock(&g_pwm_lock);

    g_last_edge_uptime_ms = k_uptime_get_32();
    g_signal_active = true;

    if (pin_val > 0) {
        // --- 1. ตรวจพบ Rising Edge (ขาขึ้น) ---
        if (g_last_rising_cycle != 0) {
            uint32_t period = now_cycles - g_last_rising_cycle;
            // กรอง Noise/Glitch สัญญาณที่มีความถี่ผิดปกติ (> 100 kHz)
            if (period > (sys_clock_hw_cycles_per_sec() / 100000)) {
                g_period_cycles = period;
                
                // คำนวณ Duty Cycle = High Time / Period
                if (g_period_cycles > 0 && g_high_time_cycles <= g_period_cycles) {
                    g_current_duty_cycle = (float)g_high_time_cycles / (float)g_period_cycles;
                    g_current_frequency_hz = sys_clock_hw_cycles_per_sec() / g_period_cycles;
                }
            }
        }
        g_last_rising_cycle = now_cycles;

    } else {
        // --- 2. ตรวจพบ Falling Edge (ขาลง) ---
        if (g_last_rising_cycle != 0) {
            uint32_t high_time = now_cycles - g_last_rising_cycle;
            g_high_time_cycles = high_time;
        }
    }

    k_spin_unlock(&g_pwm_lock, key);
}

/* -------------------------------------------------------------------------- */
/* Watchdog Thread: ตรวจสอบกรณีสัญญาณหยุดนิ่ง (ค้างที่ 0% หรือ 100%)            */
/* -------------------------------------------------------------------------- */
#define WATCHDOG_STACK_SIZE 512
#define WATCHDOG_PRIORITY   9

static void pwm_watchdog_thread_entry(void *p1, void *p2, void *p3)
{
    ARG_UNUSED(p1);
    ARG_UNUSED(p2);
    ARG_UNUSED(p3);

    while (1) {
        k_msleep(50); // ตรวจสอบทุกๆ 50ms

        uint32_t now_ms = k_uptime_get_32();
        k_spinlock_key_t key = k_spin_lock(&g_pwm_lock);

        // หากไม่มี Edge เกิดขึ้นนานเกิน 100ms แปลว่าสัญญาณหยุดนิ่ง
        if ((now_ms - g_last_edge_uptime_ms) > 100) {
            g_signal_active = false;
            g_current_frequency_hz = 0;

            // ตรวจสอบระดับแรงดันขาตรงๆ:
            int current_level = gpio_pin_get_dt(&pwm_gpio);
            if (current_level > 0) {
                g_current_duty_cycle = 1.0f; // ค้างที่ High = ปั๊มทำงาน 100%
            } else {
                g_current_duty_cycle = 0.0f; // ค้างที่ Low = ปั๊มหยุด 0%
            }
        }

        k_spin_unlock(&g_pwm_lock, key);
    }
}

K_THREAD_DEFINE(pwm_wd_thread_id, WATCHDOG_STACK_SIZE,
                pwm_watchdog_thread_entry, NULL, NULL, NULL,
                WATCHDOG_PRIORITY, 0, 0);

/* -------------------------------------------------------------------------- */
/* Public API Functions                                                       */
/* -------------------------------------------------------------------------- */
int kr260_pwm_receiver_init(void)
{
    LOG_INF("Initializing KR260 PWM Receiver Driver...");

    if (!gpio_is_ready_dt(&pwm_gpio)) {
        LOG_ERR("PWM Input GPIO device is NOT ready!");
        return -ENODEV;
    }

    // 1. กำหนดให้เป็นขา Input พร้อมต่อ Internal Pull-Down (ป้องกันสัญญาณลอย)
    int ret = gpio_pin_configure_dt(&pwm_gpio, GPIO_INPUT | GPIO_PULL_DOWN);
    if (ret != 0) {
        LOG_ERR("Failed to configure PWM GPIO pin (err: %d)", ret);
        return ret;
    }

    // 2. ตั้งค่า Interrupt ให้ทำงานทั้งขอบขาขึ้นและขอบขาลง (Both Edges)
    ret = gpio_pin_interrupt_configure_dt(&pwm_gpio, GPIO_INT_EDGE_BOTH);
    if (ret != 0) {
        LOG_ERR("Failed to configure Dual-Edge Interrupt (err: %d)", ret);
        return ret;
    }

    // 3. ลงทะเบียนฟังก์ชัน Callback เข้ากับระบบ Interrupt ของ Zephyr
    gpio_init_callback(&pwm_cb_data, pwm_gpio_callback, BIT(pwm_gpio.pin));
    ret = gpio_add_callback(pwm_gpio.port, &pwm_cb_data);
    if (ret != 0) {
        LOG_ERR("Failed to add GPIO callback (err: %d)", ret);
        return ret;
    }

    LOG_INF("KR260 PWM Receiver ready on pin %d (Dual-Edge Capture active)", pwm_gpio.pin);
    return 0;
}

float kr260_pwm_get_duty_cycle(void)
{
    k_spinlock_key_t key = k_spin_lock(&g_pwm_lock);
    float duty = g_current_duty_cycle;
    k_spin_unlock(&g_pwm_lock, key);
    return duty;
}

uint32_t kr260_pwm_get_frequency_hz(void)
{
    k_spinlock_key_t key = k_spin_lock(&g_pwm_lock);
    uint32_t freq = g_current_frequency_hz;
    k_spin_unlock(&g_pwm_lock, key);
    return freq;
}

bool kr260_pwm_is_signal_active(void)
{
    k_spinlock_key_t key = k_spin_lock(&g_pwm_lock);
    bool active = g_signal_active;
    k_spin_unlock(&g_pwm_lock, key);
    return active;
}
