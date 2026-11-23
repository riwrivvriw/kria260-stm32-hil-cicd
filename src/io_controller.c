/**
 * @file io_controller.c
 * @brief การทำงานของ Hardware GPIO Controller สำหรับ Dual E-Stop และ Handshake ร่วมกับ KR260
 */

#include "io_controller.h"
#include <zephyr/drivers/gpio.h>
#include <zephyr/logging/log.h>

LOG_MODULE_REGISTER(io_controller, LOG_LEVEL_INF);

/* Mock overrides จาก UART Testbench API */
static bool g_mock_start_stop = false;
static bool g_mock_start_stop_override = false;

static bool g_mock_estop_btn = false;
static bool g_mock_estop_btn_override = false;

static bool g_mock_safety_tripped = false;
static bool g_mock_safety_tripped_override = false;

static bool g_mock_solenoid = false;
static bool g_mock_solenoid_override = false;

/* ตรวจสอบ DeviceTree Aliases */
#if DT_NODE_EXISTS(DT_ALIAS(kr260_start_stop))
static const struct gpio_dt_spec start_stop_gpio = GPIO_DT_SPEC_GET(DT_ALIAS(kr260_start_stop), gpios);
#endif

#if DT_NODE_EXISTS(DT_ALIAS(kr260_estop_btn))
static const struct gpio_dt_spec estop_btn_gpio = GPIO_DT_SPEC_GET(DT_ALIAS(kr260_estop_btn), gpios);
#endif

#if DT_NODE_EXISTS(DT_ALIAS(kr260_solenoid))
static const struct gpio_dt_spec solenoid_gpio = GPIO_DT_SPEC_GET(DT_ALIAS(kr260_solenoid), gpios);
#endif

#if DT_NODE_EXISTS(DT_ALIAS(kr260_safety_tripped))
static const struct gpio_dt_spec safety_tripped_gpio = GPIO_DT_SPEC_GET(DT_ALIAS(kr260_safety_tripped), gpios);
#endif

int io_controller_init(void)
{
#if DT_NODE_EXISTS(DT_ALIAS(kr260_start_stop))
    if (gpio_is_ready_dt(&start_stop_gpio)) {
        gpio_pin_configure_dt(&start_stop_gpio, GPIO_OUTPUT_INACTIVE);
        LOG_INF("KR260 Mock Doctor Start/Stop Output ready on %s pin %d (Default: STOP/0V, Arduino D3)",
                start_stop_gpio.port->name, start_stop_gpio.pin);
    }
#endif

#if DT_NODE_EXISTS(DT_ALIAS(kr260_estop_btn))
    if (gpio_is_ready_dt(&estop_btn_gpio)) {
        gpio_pin_configure_dt(&estop_btn_gpio, GPIO_OUTPUT_INACTIVE);
        LOG_INF("KR260 Mock Doctor E-Stop Button Output ready on %s pin %d (Default: RELEASED/0V, Arduino D5)",
                estop_btn_gpio.port->name, estop_btn_gpio.pin);
    }
#endif

#if DT_NODE_EXISTS(DT_ALIAS(kr260_solenoid))
    if (gpio_is_ready_dt(&solenoid_gpio)) {
        gpio_pin_configure_dt(&solenoid_gpio, GPIO_INPUT);
        LOG_INF("KR260 Solenoid Valve Input ready on %s pin %d (Arduino D4)",
                solenoid_gpio.port->name, solenoid_gpio.pin);
    }
#endif

#if DT_NODE_EXISTS(DT_ALIAS(kr260_safety_tripped))
    if (gpio_is_ready_dt(&safety_tripped_gpio)) {
        gpio_pin_configure_dt(&safety_tripped_gpio, GPIO_INPUT);
        LOG_INF("KR260 Safety Tripped Status Input ready on %s pin %d (Arduino D6)",
                safety_tripped_gpio.port->name, safety_tripped_gpio.pin);
    }
#endif

    LOG_INF("Dual E-Stop IO Controller Initialized.");
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
    return 0;
}

int io_controller_pulse_doctor_button(uint32_t duration_ms)
{
    LOG_INF("Mock Doctor Button: Sending momentary START pulse (%u ms)...", duration_ms);
    io_controller_set_doctor_button(true);
    k_msleep(duration_ms > 0 ? duration_ms : 200);
    io_controller_set_doctor_button(false);
    return 0;
}

int io_controller_set_doctor_estop(bool active)
{
    g_mock_estop_btn_override = true;
    g_mock_estop_btn = active;

#if DT_NODE_EXISTS(DT_ALIAS(kr260_estop_btn))
    if (gpio_is_ready_dt(&estop_btn_gpio)) {
        gpio_pin_set_dt(&estop_btn_gpio, active ? 1 : 0);
        LOG_INF("Mock Doctor E-Stop Button driven to %s (Pin %d = %d)",
                active ? "PRESSED (3.3V)" : "RELEASED (0V)",
                estop_btn_gpio.pin, active ? 1 : 0);
        return 0;
    }
#endif
    return 0;
}

bool io_controller_get_doctor_estop(void)
{
    if (g_mock_estop_btn_override) {
        return g_mock_estop_btn;
    }
#if DT_NODE_EXISTS(DT_ALIAS(kr260_estop_btn))
    if (gpio_is_ready_dt(&estop_btn_gpio)) {
        return (gpio_pin_get_dt(&estop_btn_gpio) > 0);
    }
#endif
    return g_mock_estop_btn;
}

bool io_controller_get_safety_tripped(void)
{
    if (g_mock_safety_tripped_override) {
        return g_mock_safety_tripped;
    }
#if DT_NODE_EXISTS(DT_ALIAS(kr260_safety_tripped))
    if (gpio_is_ready_dt(&safety_tripped_gpio)) {
        return (gpio_pin_get_dt(&safety_tripped_gpio) > 0);
    }
#endif
    return g_mock_safety_tripped;
}

bool io_controller_get_estop(void)
{
    return io_controller_get_doctor_estop() || io_controller_get_safety_tripped();
}

bool io_controller_get_solenoid_valve(void)
{
    if (g_mock_solenoid_override) {
        return g_mock_solenoid;
    }
#if DT_NODE_EXISTS(DT_ALIAS(kr260_solenoid))
    if (gpio_is_ready_dt(&solenoid_gpio)) {
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
    io_controller_set_doctor_estop(active);
    io_controller_set_mock_safety_tripped(active);
    LOG_INF("Mock E-Stop (Doctor Button & Safety Trip) set to %d", active);
}

void io_controller_set_mock_safety_tripped(bool active)
{
    g_mock_safety_tripped_override = true;
    g_mock_safety_tripped = active;
    LOG_INF("Mock KR260 Safety Tripped set to %d", active);
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
    g_mock_estop_btn_override = false;
    g_mock_safety_tripped_override = false;
    g_mock_solenoid_override = false;

    g_mock_start_stop = false;
    g_mock_estop_btn = false;
    g_mock_safety_tripped = false;
    g_mock_solenoid = false;

#if DT_NODE_EXISTS(DT_ALIAS(kr260_start_stop))
    if (gpio_is_ready_dt(&start_stop_gpio)) {
        gpio_pin_set_dt(&start_stop_gpio, 0);
    }
#endif
#if DT_NODE_EXISTS(DT_ALIAS(kr260_estop_btn))
    if (gpio_is_ready_dt(&estop_btn_gpio)) {
        gpio_pin_set_dt(&estop_btn_gpio, 0);
    }
#endif

    LOG_INF("Mock GPIO overrides cleared. Now reading physical hardware pins.");
}

int io_controller_get_physical_levels(int *d3_start_out, int *d5_estop_btn_out,
                                      int *d4_sol_in, int *d6_tripped_in)
{
#if DT_NODE_EXISTS(DT_ALIAS(kr260_start_stop))
    if (d3_start_out && gpio_is_ready_dt(&start_stop_gpio)) {
        *d3_start_out = gpio_pin_get_dt(&start_stop_gpio);
    }
#endif
#if DT_NODE_EXISTS(DT_ALIAS(kr260_estop_btn))
    if (d5_estop_btn_out && gpio_is_ready_dt(&estop_btn_gpio)) {
        *d5_estop_btn_out = gpio_pin_get_dt(&estop_btn_gpio);
    }
#endif
#if DT_NODE_EXISTS(DT_ALIAS(kr260_solenoid))
    if (d4_sol_in && gpio_is_ready_dt(&solenoid_gpio)) {
        *d4_sol_in = gpio_pin_get_dt(&solenoid_gpio);
    }
#endif
#if DT_NODE_EXISTS(DT_ALIAS(kr260_safety_tripped))
    if (d6_tripped_in && gpio_is_ready_dt(&safety_tripped_gpio)) {
        *d6_tripped_in = gpio_pin_get_dt(&safety_tripped_gpio);
    }
#endif
    return 0;
}
