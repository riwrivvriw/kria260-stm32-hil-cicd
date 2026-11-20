/**
 * @file io_controller.c
 * @brief การทำงานของ Hardware GPIO Controller สำหรับ KR260 Handshake
 */

#include "io_controller.h"
#include <zephyr/drivers/gpio.h>
#include <zephyr/logging/log.h>

LOG_MODULE_REGISTER(io_controller, LOG_LEVEL_INF);

/* Mock overrides จาก UART Testbench API */
static bool g_mock_start_stop = false;
static bool g_mock_start_stop_override = false;

static bool g_mock_estop = false;
static bool g_mock_estop_override = false;

static bool g_mock_solenoid = false;
static bool g_mock_solenoid_override = false;

/* ตรวจสอบ DeviceTree Aliases หากมีการประกาศพิน */
#if DT_NODE_EXISTS(DT_ALIAS(kr260_start_stop))
static const struct gpio_dt_spec start_stop_gpio = GPIO_DT_SPEC_GET(DT_ALIAS(kr260_start_stop), gpios);
#endif

#if DT_NODE_EXISTS(DT_ALIAS(kr260_estop))
static const struct gpio_dt_spec estop_gpio = GPIO_DT_SPEC_GET(DT_ALIAS(kr260_estop), gpios);
#endif

#if DT_NODE_EXISTS(DT_ALIAS(kr260_solenoid))
static const struct gpio_dt_spec solenoid_gpio = GPIO_DT_SPEC_GET(DT_ALIAS(kr260_solenoid), gpios);
#endif

int io_controller_init(void)
{
#if DT_NODE_EXISTS(DT_ALIAS(kr260_start_stop))
    if (gpio_is_ready_dt(&start_stop_gpio)) {
        gpio_pin_configure_dt(&start_stop_gpio, GPIO_OUTPUT_INACTIVE);
        LOG_INF("KR260 Mock Doctor Start/Stop Output ready on %s pin %d (Default: STOP/0V)",
                start_stop_gpio.port->name, start_stop_gpio.pin);
    }
#endif

#if DT_NODE_EXISTS(DT_ALIAS(kr260_estop))
    if (gpio_is_ready_dt(&estop_gpio)) {
        gpio_pin_configure_dt(&estop_gpio, GPIO_INPUT);
        LOG_INF("KR260 E-Stop GPIO ready on %s pin %d", estop_gpio.port->name, estop_gpio.pin);
    }
#endif

#if DT_NODE_EXISTS(DT_ALIAS(kr260_solenoid))
    if (gpio_is_ready_dt(&solenoid_gpio)) {
        gpio_pin_configure_dt(&solenoid_gpio, GPIO_INPUT);
        LOG_INF("KR260 Solenoid Valve GPIO ready on %s pin %d", solenoid_gpio.port->name, solenoid_gpio.pin);
    }
#endif

    LOG_INF("IO Controller Initialized.");
    return 0;
}

bool io_controller_get_start_stop(void)
{
    return g_mock_start_stop;
}

int io_controller_set_doctor_button(bool active)
{
    g_mock_start_stop_override = true;
    g_mock_start_stop = active;

#if DT_NODE_EXISTS(DT_ALIAS(kr260_start_stop))
    if (gpio_is_ready_dt(&start_stop_gpio)) {
        gpio_pin_set_dt(&start_stop_gpio, active ? 1 : 0);
        LOG_INF("Mock Doctor Button driven to %s (Pin %d = %d)",
                active ? "START (3.3V)" : "STOP (0V)",
                start_stop_gpio.pin, active ? 1 : 0);
        return 0;
    }
#endif
    LOG_INF("Mock Doctor Button state updated: %s", active ? "START" : "STOP");
    return 0;
}

int io_controller_pulse_doctor_button(uint32_t duration_ms)
{
    LOG_INF("Mock Doctor Button: Sending momentary START pulse (%u ms)...", duration_ms);
    io_controller_set_doctor_button(true);
    k_msleep(duration_ms > 0 ? duration_ms : 200);
    io_controller_set_doctor_button(false);
    LOG_INF("Mock Doctor Button: Pulse complete, returned to STOP");
    return 0;
}

bool io_controller_get_estop(void)
{
    if (g_mock_estop_override) {
        return g_mock_estop;
    }
#if DT_NODE_EXISTS(DT_ALIAS(kr260_estop))
    if (gpio_is_ready_dt(&estop_gpio)) {
        return (gpio_pin_get_dt(&estop_gpio) > 0);
    }
#endif
    return g_mock_estop;
}

bool io_controller_get_solenoid_valve(void)
{
    if (g_mock_solenoid_override) {
        return g_mock_solenoid;
    }
#if DT_NODE_EXISTS(DT_ALIAS(kr260_solenoid))
    if (gpio_is_ready_dt(&solenoid_gpio)) {
        /*
         * วงจรฮาร์ดแวร์ Solenoid Valve:
         * ชนิด Normally Open (NO) ผ่าน N-Channel MOSFET:
         * - ขาเกต HIGH (3.3V) -> MOSFET ON -> ขดลวดดึงแกน "ปิดวาล์ว" (Holding Gas, valve_open = false)
         * - ขาเกต LOW (0V)    -> MOSFET OFF -> ขดลวดคลายแกน "เปิดวาล์ว" (Venting Gas, valve_open = true)
         */
        int pin_level = gpio_pin_get_dt(&solenoid_gpio);
        return (pin_level == 0); /* LOW = วาล์วเปิดระบายก๊าซทิ้ง (Over-Expansion Deflate) */
    }
#endif
    return g_mock_solenoid;
}

void io_controller_set_mock_start_stop(bool active)
{
    io_controller_set_doctor_button(active);
}

void io_controller_set_mock_estop(bool active)
{
    g_mock_estop_override = true;
    g_mock_estop = active;
    LOG_INF("Mock E-Stop set to %d", active);
}

void io_controller_set_mock_solenoid(bool active)
{
    g_mock_solenoid_override = true;
    g_mock_solenoid = active;
    LOG_INF("Mock Solenoid Valve set to %d", active);
}

void io_controller_clear_mock_overrides(void)
{
    g_mock_start_stop_override = false;
    g_mock_estop_override = false;
    g_mock_solenoid_override = false;
    g_mock_start_stop = false;
    g_mock_estop = false;
    g_mock_solenoid = false;
    LOG_INF("Mock GPIO overrides cleared. Now reading physical hardware pins.");
}

int io_controller_get_physical_levels(int *start_out, int *sol_in, int *estop_in)
{
#if DT_NODE_EXISTS(DT_ALIAS(kr260_start_stop))
    if (start_out && gpio_is_ready_dt(&start_stop_gpio)) {
        *start_out = gpio_pin_get_dt(&start_stop_gpio);
    }
#endif
#if DT_NODE_EXISTS(DT_ALIAS(kr260_solenoid))
    if (sol_in && gpio_is_ready_dt(&solenoid_gpio)) {
        *sol_in = gpio_pin_get_dt(&solenoid_gpio);
    }
#endif
#if DT_NODE_EXISTS(DT_ALIAS(kr260_estop))
    if (estop_in && gpio_is_ready_dt(&estop_gpio)) {
        *estop_in = gpio_pin_get_dt(&estop_gpio);
    }
#endif
    return 0;
}
