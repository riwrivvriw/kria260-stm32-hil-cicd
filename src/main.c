/**
 * @file main.c
 * @brief STM32H5 HIL Plant Simulator (Zephyr RTOS)
 * @details ทำหน้าที่เป็นทั้ง I2C Target (Slave), Closed-Loop Pressure Plant Simulator,
 *          และรับสัญญาณ Airpump PWM จากบอร์ด Kria KR260 เพื่อคำนวณความดันแบบ Real-Time
 */

#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/i2c.h>
#include <zephyr/drivers/i2c/target/eeprom.h>
#include <zephyr/shell/shell.h>
#include <zephyr/logging/log.h>
#include <stdio.h>
#include <stdlib.h>

#include "kr260/kr260_pwm_receiver.h"

LOG_MODULE_REGISTER(hil_simulator, LOG_LEVEL_INF);

/* -------------------------------------------------------------------------- */
/* นิยาม Register Map ของ Sensor จำลอง                                         */
/* -------------------------------------------------------------------------- */
#define TARGET_I2C_ADDR       0x58
#define REG_CHIP_ID           0x00
#define REG_STATUS            0x01
#define REG_PRESSURE_MSB      0x02
#define REG_PRESSURE_LSB      0x03
#define BUFFER_SIZE           256

/* Buffer สำหรับเก็บข้อมูล I2C Target */
static uint8_t g_i2c_buffer[BUFFER_SIZE];
static struct k_mutex g_buffer_mutex;
static const struct device *g_target_dev;

/* ตัวแปรสถานะระบบ Plant Simulation */
static float g_current_pressure_kpa = 101.325f; // ค่าความดันเริ่มต้น (1 atm = 101.325 kPa)
static bool  g_leak_injected = false;           // จำลองสภาวะลมรั่ว
static bool  g_auto_simulation = true;          // เปิด/ปิด การคำนวณฟิสิกส์อัตโนมัติ

/* ฟังก์ชันช่วยอัปเดตลง EEPROM Target Hardware */
static void update_eeprom_memory(void)
{
    if (g_target_dev && device_is_ready(g_target_dev)) {
        eeprom_target_write_data(g_target_dev, 0, g_i2c_buffer, 4);
    }
}

/* -------------------------------------------------------------------------- */
/* Thread จำลองฟิสิกส์ความดัน (Closed-Loop Plant Model Simulation Thread)       */
/* -------------------------------------------------------------------------- */
#define SIM_STACK_SIZE 1024
#define SIM_PRIORITY   7

static void plant_sim_thread_entry(void *p1, void *p2, void *p3)
{
    ARG_UNUSED(p1);
    ARG_UNUSED(p2);
    ARG_UNUSED(p3);

    LOG_INF("Closed-Loop Plant Simulation Thread Started.");
    const float dt = 0.05f;          // คาบเวลาการคำนวณ 50ms (0.05 วินาที)
    const float k_pump = 25.0f;      // อัตราการเพิ่มความดันเมื่อปั๊มทำงาน 100% (kPa/s)
    const float k_leak = 18.0f;      // อัตราการระบายความดันเมื่อเกิดรอยรั่ว
    const float p_ambient = 101.325f;// ความดันบรรยากาศ

    while (1) {
        if (g_auto_simulation) {
            // อ่านค่า Duty Cycle ปัจจุบันที่ KR260 ส่งมา (0.0 - 1.0)
            float pump_duty = kr260_pwm_get_duty_cycle();

            k_mutex_lock(&g_buffer_mutex, K_FOREVER);

            // สมการพลศาสตร์ Closed-Loop: dP/dt = (K_pump * Duty) - (K_leak * Leak)
            float dp = (k_pump * pump_duty) * dt;

            if (g_leak_injected) {
                // หากมีการรั่ว ความดันจะลดลงอย่างรวดเร็วสู่ระดับบรรยากาศ
                dp -= k_leak * (g_current_pressure_kpa - p_ambient) * dt;
            } else if (pump_duty < 0.02f && g_current_pressure_kpa > p_ambient) {
                // หากปั๊มดับและไม่มีการรั่ว ความดันจะค่อยๆ คลายตัวลงช้าๆ
                dp -= 0.5f * (g_current_pressure_kpa - p_ambient) * dt;
            }

            g_current_pressure_kpa += dp;
            if (g_current_pressure_kpa < p_ambient) {
                g_current_pressure_kpa = p_ambient;
            }

            // แปลงค่าความดันเป็น Fixed-point 16-bit (คูณ 100 เพื่อเก็บทศนิยม 2 ตำแหน่ง)
            uint16_t raw_val = (uint16_t)(g_current_pressure_kpa * 100.0f);

            // อัปเดตข้อมูลลง Register Buffer ให้ KR260 เข้ามาอ่านผ่าน I2C
            g_i2c_buffer[REG_CHIP_ID]      = TARGET_I2C_ADDR;
            g_i2c_buffer[REG_STATUS]       = g_leak_injected ? 0x01 : 0x00;
            g_i2c_buffer[REG_PRESSURE_MSB] = (raw_val >> 8) & 0xFF;
            g_i2c_buffer[REG_PRESSURE_LSB] = raw_val & 0xFF;

            update_eeprom_memory();

            k_mutex_unlock(&g_buffer_mutex);
        }

        // วนลูปคำนวณทุกๆ 50ms (20 Hz)
        k_msleep(50);
    }
}

K_THREAD_DEFINE(sim_thread_id, SIM_STACK_SIZE,
                plant_sim_thread_entry, NULL, NULL, NULL,
                SIM_PRIORITY, 0, 0);

/* -------------------------------------------------------------------------- */
/* ฟังก์ชันทดสอบ I2C Loopback (Master อ่าน Slave ตัวเอง)                        */
/* -------------------------------------------------------------------------- */
static int run_i2c_loopback_test(uint16_t *read_raw_pressure, uint8_t *read_chip_id)
{
    const struct device *i2c_master = DEVICE_DT_GET(DT_ALIAS(hil_master));

    if (!device_is_ready(i2c_master)) {
        LOG_ERR("I2C Master device (hil-master) is not ready!");
        return -ENODEV;
    }

    uint8_t reg_addr = REG_CHIP_ID;
    uint8_t rx_data[4] = {0};

    int ret = i2c_write_read(i2c_master, TARGET_I2C_ADDR, 
                             &reg_addr, 1, 
                             rx_data, sizeof(rx_data));
    if (ret != 0) {
        LOG_ERR("I2C Loopback Transaction Failed (err: %d)", ret);
        return ret;
    }

    *read_chip_id = rx_data[0];
    *read_raw_pressure = (rx_data[2] << 8) | rx_data[3];
    return 0;
}

/* -------------------------------------------------------------------------- */
/* Zephyr Shell Commands (รับคำสั่งจาก Pytest ผ่าน USB Serial)                */
/* -------------------------------------------------------------------------- */
static int cmd_hil_status(const struct shell *sh, size_t argc, char **argv)
{
    ARG_UNUSED(argc);
    ARG_UNUSED(argv);

    float pump_duty = kr260_pwm_get_duty_cycle();
    uint32_t pwm_freq = kr260_pwm_get_frequency_hz();

    k_mutex_lock(&g_buffer_mutex, K_FOREVER);
    // รายงานสถานะ JSON พร้อมค่า PWM Duty Cycle ที่วัดได้จาก KR260 แบบสดๆ
    shell_print(sh, "{\"chip_id\": \"0x%02X\", \"pressure_kpa\": %.2f, \"pump_duty\": %.2f, \"pwm_freq_hz\": %u, \"leak\": %s, \"auto\": %s}",
                g_i2c_buffer[REG_CHIP_ID],
                (double)g_current_pressure_kpa,
                (double)pump_duty,
                pwm_freq,
                g_leak_injected ? "true" : "false",
                g_auto_simulation ? "true" : "false");
    k_mutex_unlock(&g_buffer_mutex);

    return 0;
}

static int cmd_hil_set_pressure(const struct shell *sh, size_t argc, char **argv)
{
    if (argc < 2) {
        shell_error(sh, "Usage: hil set_pressure <float_value_in_kpa>");
        return -EINVAL;
    }

    float new_pressure = strtof(argv[1], NULL);
    k_mutex_lock(&g_buffer_mutex, K_FOREVER);
    g_auto_simulation = false; // ปิดการคำนวณอัตโนมัติ เพื่อตรึงค่าตามที่เทสต์เคสต้องการ
    g_current_pressure_kpa = new_pressure;
    
    uint16_t raw_val = (uint16_t)(g_current_pressure_kpa * 100.0f);
    g_i2c_buffer[REG_PRESSURE_MSB] = (raw_val >> 8) & 0xFF;
    g_i2c_buffer[REG_PRESSURE_LSB] = raw_val & 0xFF;
    update_eeprom_memory();
    k_mutex_unlock(&g_buffer_mutex);

    shell_print(sh, "OK: Pressure set to %.2f kPa (Auto-sim disabled)", (double)new_pressure);
    return 0;
}

static int cmd_hil_inject_leak(const struct shell *sh, size_t argc, char **argv)
{
    if (argc < 2) {
        shell_error(sh, "Usage: hil inject_leak <0|1>");
        return -EINVAL;
    }

    int leak_flag = atoi(argv[1]);
    k_mutex_lock(&g_buffer_mutex, K_FOREVER);
    g_leak_injected = (leak_flag != 0);
    g_auto_simulation = true;
    update_eeprom_memory();
    k_mutex_unlock(&g_buffer_mutex);

    shell_print(sh, "OK: Leak state updated to %d", leak_flag);
    return 0;
}

static int cmd_hil_loopback(const struct shell *sh, size_t argc, char **argv)
{
    ARG_UNUSED(argc);
    ARG_UNUSED(argv);

    uint16_t raw_pressure = 0;
    uint8_t chip_id = 0;

    shell_print(sh, "Starting I2C Loopback Self-Test...");
    int ret = run_i2c_loopback_test(&raw_pressure, &chip_id);
    if (ret == 0) {
        float parsed_pressure = (float)raw_pressure / 100.0f;
        shell_print(sh, "{\"loopback\": \"PASS\", \"read_chip_id\": \"0x%02X\", \"read_pressure\": %.2f}",
                    chip_id, (double)parsed_pressure);
    } else {
        shell_error(sh, "{\"loopback\": \"FAIL\", \"error_code\": %d}", ret);
    }

    return ret;
}

/* ลงทะเบียนคำสั่งย่อยเข้ากลุ่มคำสั่ง "hil" */
SHELL_STATIC_SUBCMD_SET_CREATE(sub_hil,
    SHELL_CMD(status, NULL, "Get current HIL plant status (JSON)", cmd_hil_status),
    SHELL_CMD(set_pressure, NULL, "Set fixed pressure value", cmd_hil_set_pressure),
    SHELL_CMD(inject_leak, NULL, "Inject/Clear air leakage state (0 or 1)", cmd_hil_inject_leak),
    SHELL_CMD(loopback, NULL, "Execute I2C Master-to-Slave loopback test", cmd_hil_loopback),
    SHELL_SUBCMD_SET_END
);

SHELL_CMD_REGISTER(hil, &sub_hil, "HIL Plant Controller Commands", NULL);

/* -------------------------------------------------------------------------- */
/* ฟังก์ชัน Main เริ่มต้นระบบ                                                  */
/* -------------------------------------------------------------------------- */
int main(void)
{
    LOG_INF("==================================================");
    LOG_INF(" STM32H5 HIL Plant Simulator Initializing...     ");
    LOG_INF(" OS: Zephyr RTOS | Target: Nucleo-H563ZI         ");
    LOG_INF("==================================================");

    k_mutex_init(&g_buffer_mutex);

    // กำหนดค่าเริ่มต้นให้กับ Buffer
    g_i2c_buffer[REG_CHIP_ID] = TARGET_I2C_ADDR;
    g_i2c_buffer[REG_STATUS]  = 0x00;

    // 1. เชื่อมต่อ Buffer เข้ากับ I2C Target EEPROM Driver
    g_target_dev = DEVICE_DT_GET(DT_ALIAS(hil_target));
    if (!device_is_ready(g_target_dev)) {
        LOG_ERR("Target device (hil-target) is NOT ready!");
        return -ENODEV;
    }
    update_eeprom_memory();

    // 2. เริ่มต้นระบบตรวจวัดสัญญาณ PWM จาก KR260
    int ret = kr260_pwm_receiver_init();
    if (ret != 0) {
        LOG_WRN("KR260 PWM Receiver init returned %d (Pin may not be driven yet)", ret);
    }

    LOG_INF("I2C Target registered at address 0x%02X successfully.", TARGET_I2C_ADDR);
    LOG_INF("Zephyr Shell ready. Type 'hil status' to inspect.");

    return 0;
}
