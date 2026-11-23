/**
 * @file main.c
 * @brief STM32H5 HIL Plant Simulator (Zephyr RTOS)
 * @details จำลองสภาพแวดล้อมทางเดินอาหาร (GI Plant & Insufflator Simulation)
 *          - รับคำสั่ง Airpump PWM และ GPIO Command จาก Kria KR260
 *          - จำลองแรงดันก๊าซผ่านบัส I2C Target (EEPROM Addr 0x58)
 *          - ขับสัญญาณเสียงลมรั่ว AC Audio Waveform ผ่าน DAC
 *          - ควบคุม Finite State Machine สอดคล้องกับภาพกล้องตรวจ (Mock Camera Stream)
 *          - รองรับ UART Test API สำหรับ Host CI/CD Testbench
 */

#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/i2c.h>
#include <zephyr/drivers/i2c/target/eeprom.h>
#include <zephyr/shell/shell.h>
#include <zephyr/logging/log.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>

#include "kr260/kr260_pwm_receiver.h"
#include "gi_state_machine.h"
#include "audio_leak.h"
#include "io_controller.h"

LOG_MODULE_REGISTER(hil_main, LOG_LEVEL_INF);

/* -------------------------------------------------------------------------- */
/* นิยาม Register Map ของ I2C Target (0x58)                                    */
/* -------------------------------------------------------------------------- */
#define TARGET_I2C_ADDR       0x58
#define REG_CHIP_ID           0x00  /* 0x58 */
#define REG_STATUS            0x01  /* Bitfield Status */
#define REG_PRESSURE_MSB      0x02  /* Pressure in kPa * 100 (MSB) */
#define REG_PRESSURE_LSB      0x03  /* Pressure in kPa * 100 (LSB) */
#define REG_GI_STATE          0x04  /* State ID: 0..5 */
#define REG_PUMP_DUTY         0x05  /* Duty 0-100% */
#define REG_TARGET_PRESSURE   0x06  /* Target Pressure Setpoint */
#define REG_IO_STATUS         0x07  /* Bit 0: Start/Stop, Bit 1: E-Stop, Bit 2: Valve */
#define BUFFER_SIZE           256

/* Status Bits */
#define STATUS_BIT_LEAK       (1 << 0)
#define STATUS_BIT_VALVE      (1 << 1)
#define STATUS_BIT_PUMPING    (1 << 2)
#define STATUS_BIT_AUDIO      (1 << 3)
#define STATUS_BIT_CAMERA     (1 << 4)
#define STATUS_BIT_ESTOP      (1 << 5)

static uint8_t g_i2c_buffer[BUFFER_SIZE];
static struct k_mutex g_i2c_mutex;
static const struct device *g_target_dev;

static void update_eeprom_memory(void)
{
    if (g_target_dev && device_is_ready(g_target_dev)) {
        eeprom_target_write_data(g_target_dev, 0, g_i2c_buffer, 8);
    }
}

/* -------------------------------------------------------------------------- */
/* Thread ประมวลผลจำลองระบบและปรับปรุงค่า Register (20 Hz / 50ms)              */
/* -------------------------------------------------------------------------- */
#define SIM_STACK_SIZE 2048
#define SIM_PRIORITY   7

static void plant_sim_thread_entry(void *p1, void *p2, void *p3)
{
    ARG_UNUSED(p1);
    ARG_UNUSED(p2);
    ARG_UNUSED(p3);

    LOG_INF("HIL Plant Simulator Core Thread Started.");
    const float dt = 0.05f;

    while (1) {
        // 1. อ่านอินพุตจาก KR260 (PWM และ GPIO)
        float pump_duty = kr260_pwm_get_duty_cycle();
        uint32_t pwm_freq = kr260_pwm_get_frequency_hz();
        bool start_stop_io = io_controller_get_start_stop();
        bool doctor_estop_btn = io_controller_get_doctor_estop();
        bool kr260_tripped = io_controller_get_safety_tripped();
        bool solenoid_open = io_controller_get_solenoid_valve();

        // 2. อัปเดต Finite State Machine
        gi_state_machine_update(dt, pump_duty, pwm_freq, start_stop_io,
                                doctor_estop_btn, kr260_tripped, solenoid_open);

        // 3. อ่านสถานะปัจจุบันของระบบ
        gi_system_status_t sys_stat;
        gi_state_machine_get_status(&sys_stat);

        // 4. ซิงค์สัญญาณเสียง AC/I2S Audio Leak Generator กับ FSM
        audio_leak_sync_fsm(sys_stat.audio_leak_active);

        // 5. แปลงข้อมูลลง I2C Target Register Buffer
        k_mutex_lock(&g_i2c_mutex, K_FOREVER);

        uint16_t raw_pressure = (uint16_t)(sys_stat.current_pressure_kpa * 100.0f);
        uint8_t status_flags = 0;
        if (sys_stat.leak_active)        status_flags |= STATUS_BIT_LEAK;
        if (sys_stat.solenoid_valve_open) status_flags |= STATUS_BIT_VALVE;
        if (sys_stat.pump_duty > 0.05f)  status_flags |= STATUS_BIT_PUMPING;
        if (sys_stat.audio_leak_active)  status_flags |= STATUS_BIT_AUDIO;
        if (sys_stat.state != GI_STATE_IDLE) status_flags |= STATUS_BIT_CAMERA;
        if (sys_stat.estop_active)       status_flags |= STATUS_BIT_ESTOP;

        uint8_t io_flags = 0;
        if (sys_stat.start_stop_io)      io_flags |= (1 << 0);
        if (sys_stat.estop_active)       io_flags |= (1 << 1);
        if (sys_stat.solenoid_valve_open) io_flags |= (1 << 2);

        g_i2c_buffer[REG_CHIP_ID]         = TARGET_I2C_ADDR;
        g_i2c_buffer[REG_STATUS]          = status_flags;
        g_i2c_buffer[REG_PRESSURE_MSB]    = (raw_pressure >> 8) & 0xFF;
        g_i2c_buffer[REG_PRESSURE_LSB]    = raw_pressure & 0xFF;
        g_i2c_buffer[REG_GI_STATE]        = (uint8_t)sys_stat.state;
        g_i2c_buffer[REG_PUMP_DUTY]       = (uint8_t)(sys_stat.pump_duty * 100.0f);
        g_i2c_buffer[REG_TARGET_PRESSURE] = (uint8_t)sys_stat.target_pressure_kpa;
        g_i2c_buffer[REG_IO_STATUS]       = io_flags;

        update_eeprom_memory();

        k_mutex_unlock(&g_i2c_mutex);

        k_msleep(50);
    }
}

K_THREAD_DEFINE(sim_thread_id, SIM_STACK_SIZE,
                plant_sim_thread_entry, NULL, NULL, NULL,
                SIM_PRIORITY, 0, 0);

/* -------------------------------------------------------------------------- */
/* ฟังก์ชัน I2C Loopback Self-test                                             */
/* -------------------------------------------------------------------------- */
static int run_i2c_loopback_test(uint16_t *read_raw_pressure, uint8_t *read_chip_id)
{
    const struct device *i2c_master = DEVICE_DT_GET(DT_ALIAS(hil_master));
    if (!device_is_ready(i2c_master)) {
        LOG_ERR("I2C Master device (hil-master) is not ready!");
        return -ENODEV;
    }

    uint8_t reg_addr = REG_CHIP_ID;
    uint8_t rx_data[8] = {0};

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
/* Zephyr Shell Commands (UART Test API สำหรับ Host Laptop)                   */
/* -------------------------------------------------------------------------- */
static int cmd_hil_status(const struct shell *sh, size_t argc, char **argv)
{
    ARG_UNUSED(argc);
    ARG_UNUSED(argv);

    gi_system_status_t s;
    gi_state_machine_get_status(&s);

    k_mutex_lock(&g_i2c_mutex, K_FOREVER);
    // รายงานผลเป็น JSON Format ละเอียดสำหรับ Pytest Framework
    shell_print(sh,
        "{\"chip_id\": \"0x%02X\", \"state\": \"%s\", \"state_id\": %d, "
        "\"pressure_kpa\": %.2f, \"target_kpa\": %.2f, \"pump_duty\": %.2f, \"pwm_freq_hz\": %u, "
        "\"leak\": %s, \"valve_open\": %s, \"audio_active\": %s, "
        "\"start_stop_io\": %s, \"estop\": %s, \"doctor_estop_btn\": %s, \"kr260_safety_tripped\": %s, "
        "\"camera_scene\": \"%s\", \"auto\": %s}",
        g_i2c_buffer[REG_CHIP_ID],
        gi_state_to_str(s.state),
        (int)s.state,
        (double)s.current_pressure_kpa,
        (double)s.target_pressure_kpa,
        (double)s.pump_duty,
        s.pwm_freq_hz,
        s.leak_active ? "true" : "false",
        s.solenoid_valve_open ? "true" : "false",
        s.audio_leak_active ? "true" : "false",
        s.start_stop_io ? "true" : "false",
        s.estop_active ? "true" : "false",
        s.doctor_estop_btn ? "true" : "false",
        s.kr260_safety_tripped ? "true" : "false",
        s.camera_scene,
        s.auto_simulation ? "true" : "false");
    k_mutex_unlock(&g_i2c_mutex);

    return 0;
}

static int cmd_hil_set_state(const struct shell *sh, size_t argc, char **argv)
{
    if (argc < 2) {
        shell_error(sh, "Usage: hil set_state <IDLE|INSUFFLATE|INSPECT|LEAK|DEFLATE|ESTOP>");
        return -EINVAL;
    }

    const char *state_arg = argv[1];
    gi_state_t target_state = GI_STATE_IDLE;

    if (strcasecmp(state_arg, "IDLE") == 0)             target_state = GI_STATE_IDLE;
    else if (strcasecmp(state_arg, "INSUFFLATE") == 0)  target_state = GI_STATE_INSUFFLATION;
    else if (strcasecmp(state_arg, "INSPECT") == 0)     target_state = GI_STATE_STABLE_INSPECTION;
    else if (strcasecmp(state_arg, "LEAK") == 0)        target_state = GI_STATE_LEAK_EVENT;
    else if (strcasecmp(state_arg, "DEFLATE") == 0)     target_state = GI_STATE_DEFLATION_STOP;
    else if (strcasecmp(state_arg, "ESTOP") == 0)       target_state = GI_STATE_EMERGENCY_STOP;
    else {
        shell_error(sh, "Unknown state: %s", state_arg);
        return -EINVAL;
    }

    gi_state_machine_set_state(target_state);
    shell_print(sh, "OK: State transitioned to %s", gi_state_to_str(target_state));
    return 0;
}

static int cmd_hil_set_pressure(const struct shell *sh, size_t argc, char **argv)
{
    if (argc < 2) {
        shell_error(sh, "Usage: hil set_pressure <float_value_in_kpa>");
        return -EINVAL;
    }

    float new_pressure = strtof(argv[1], NULL);
    gi_state_machine_set_fixed_pressure(new_pressure);
    shell_print(sh, "OK: Pressure set to %.2f kPa (Auto-sim disabled. Use 'hil auto 1' to enable decay/vent)", (double)new_pressure);
    return 0;
}

static int cmd_hil_auto(const struct shell *sh, size_t argc, char **argv)
{
    if (argc < 2) {
        shell_error(sh, "Usage: hil auto <0|1>");
        return -EINVAL;
    }

    int enable = atoi(argv[1]);
    gi_state_machine_set_auto(enable != 0);
    shell_print(sh, "OK: Auto Physics Simulation set to %d", enable);
    return 0;
}

static int cmd_hil_inject_leak(const struct shell *sh, size_t argc, char **argv)
{
    if (argc < 2) {
        shell_error(sh, "Usage: hil inject_leak <0|1>");
        return -EINVAL;
    }

    int leak_flag = atoi(argv[1]);
    gi_state_machine_inject_leak(leak_flag != 0);
    shell_print(sh, "OK: Leak injection set to %d", leak_flag);
    return 0;
}

static int cmd_hil_audio_leak(const struct shell *sh, size_t argc, char **argv)
{
    if (argc < 2) {
        shell_error(sh, "Usage: hil audio_leak <0|1>");
        return -EINVAL;
    }

    int audio_flag = atoi(argv[1]);
    audio_leak_set_enable(audio_flag != 0);
    shell_print(sh, "OK: AC Audio Leak set to %d", audio_flag);
    return 0;
}

static int cmd_hil_button(const struct shell *sh, size_t argc, char **argv)
{
    if (argc < 2) {
        shell_error(sh, "Usage: hil button <start|stop|estop_on|estop_off|pulse|status> [pulse_ms]");
        return -EINVAL;
    }

    if (strcasecmp(argv[1], "start") == 0) {
        io_controller_set_doctor_button(true);
        shell_print(sh, "OK: Doctor Button -> START (Driven 3.3V to KR260 Pin D3 to start AI & PID)");
    } else if (strcasecmp(argv[1], "stop") == 0) {
        io_controller_set_doctor_button(false);
        shell_print(sh, "OK: Doctor Button -> STOP (Driven 0V to KR260 Pin D3 to stop and vent)");
    } else if (strcasecmp(argv[1], "estop_on") == 0 || strcasecmp(argv[1], "estop") == 0) {
        io_controller_set_doctor_estop(true);
        shell_print(sh, "OK: Doctor Button -> EMERGENCY STOP PRESSED (Driven 3.3V to KR260 Pin D5)");
    } else if (strcasecmp(argv[1], "estop_off") == 0) {
        io_controller_set_doctor_estop(false);
        shell_print(sh, "OK: Doctor Button -> EMERGENCY STOP RELEASED (Driven 0V to KR260 Pin D5)");
    } else if (strcasecmp(argv[1], "pulse") == 0) {
        uint32_t ms = (argc >= 3) ? atoi(argv[2]) : 200;
        io_controller_pulse_doctor_button(ms);
        shell_print(sh, "OK: Doctor Button -> Momentary Pulse (%u ms) sent to KR260", ms);
    } else if (strcasecmp(argv[1], "status") == 0) {
        bool start_act = io_controller_get_start_stop();
        bool estop_act = io_controller_get_doctor_estop();
        shell_print(sh, "{\"button_start\": %s, \"button_estop\": %s}",
                    start_act ? "true" : "false", estop_act ? "true" : "false");
    } else {
        shell_error(sh, "Unknown action: %s (Use 'start', 'stop', 'estop_on', 'estop_off', 'pulse', or 'status')", argv[1]);
        return -EINVAL;
    }
    return 0;
}

static int cmd_hil_start_stop(const struct shell *sh, size_t argc, char **argv)
{
    if (argc < 2) {
        shell_error(sh, "Usage: hil set_start_stop <0|1>");
        return -EINVAL;
    }

    int val = atoi(argv[1]);
    io_controller_set_doctor_button(val != 0);
    shell_print(sh, "OK: Start/Stop IO set to %d", val);
    return 0;
}

static int cmd_hil_estop(const struct shell *sh, size_t argc, char **argv)
{
    if (argc < 2) {
        shell_error(sh, "Usage: hil set_estop <0|1>");
        return -EINVAL;
    }

    int val = atoi(argv[1]);
    io_controller_set_mock_estop(val != 0);
    shell_print(sh, "OK: E-Stop IO (Doctor Button & Safety Flag) set to %d", val);
    return 0;
}

static int cmd_hil_safety_tripped(const struct shell *sh, size_t argc, char **argv)
{
    if (argc < 2) {
        shell_error(sh, "Usage: hil set_safety_tripped <0|1>");
        return -EINVAL;
    }

    int val = atoi(argv[1]);
    io_controller_set_mock_safety_tripped(val != 0);
    shell_print(sh, "OK: KR260 Safety Tripped Status IO set to %d", val);
    return 0;
}

static int cmd_hil_solenoid(const struct shell *sh, size_t argc, char **argv)
{
    if (argc < 2) {
        shell_error(sh, "Usage: hil set_solenoid <0|1>");
        return -EINVAL;
    }

    int val = atoi(argv[1]);
    io_controller_set_mock_solenoid(val != 0);
    gi_state_machine_set_solenoid(val != 0);
    shell_print(sh, "OK: Solenoid Valve set to %d", val);
    return 0;
}

static int cmd_hil_reset(const struct shell *sh, size_t argc, char **argv)
{
    ARG_UNUSED(argc);
    ARG_UNUSED(argv);

    gi_state_machine_reset();
    audio_leak_clear_override();
    audio_leak_set_enable(false);
    io_controller_clear_mock_overrides();

    shell_print(sh, "OK: HIL System Simulator fully reset to IDLE (Mock GPIO overrides cleared)");
    return 0;
}

static int cmd_hil_test_gpio(const struct shell *sh, size_t argc, char **argv)
{
    ARG_UNUSED(argc);
    ARG_UNUSED(argv);

    int d3_out = -1, d5_btn_out = -1, d4_sol_in = -1, d6_trip_in = -1;
    io_controller_get_physical_levels(&d3_out, &d5_btn_out, &d4_sol_in, &d6_trip_in);

    shell_print(sh,
        "{\"physical_gpio\": {\"d3_button_out\": %d, \"d5_estop_btn_out\": %d, \"d4_solenoid_in\": %d, \"d6_safety_tripped_in\": %d}}",
        d3_out, d5_btn_out, d4_sol_in, d6_trip_in);
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

static int cmd_hil_scenario(const struct shell *sh, size_t argc, char **argv)
{
    if (argc < 2) {
        shell_error(sh, "Usage: hil scenario <normal|low_pressure|over_expansion|gas_leak|tube_kink|cough_spike> [custom_val]");
        return -EINVAL;
    }

    audio_leak_clear_override();
    float custom_val = (argc >= 3) ? strtof(argv[2], NULL) : 0.0f;
    int ret = gi_state_machine_apply_scenario(argv[1], custom_val);
    if (ret == 0) {
        shell_print(sh, "OK: Scenario '%s' loaded and running dynamically", argv[1]);
    } else {
        shell_error(sh, "Unknown scenario '%s'. Available: normal, low_pressure, over_expansion, gas_leak, tube_kink, cough_spike", argv[1]);
    }
    return ret;
}

static int cmd_hil_test_interfaces(const struct shell *sh, size_t argc, char **argv)
{
    ARG_UNUSED(argc);
    ARG_UNUSED(argv);

    uint16_t raw_pressure = 0;
    uint8_t chip_id = 0;
    int i2c_ret = run_i2c_loopback_test(&raw_pressure, &chip_id);
    const char *i2c_status = (i2c_ret == 0 && chip_id == TARGET_I2C_ADDR) ? "PASS" : "WAIT_WIRING";

    bool io_start = io_controller_get_start_stop();
    bool io_estop_btn = io_controller_get_doctor_estop();
    bool io_sol = io_controller_get_solenoid_valve();
    bool io_tripped = io_controller_get_safety_tripped();
    bool io_estop = io_controller_get_estop();

    float pwm_duty = kr260_pwm_get_duty_cycle();
    uint32_t pwm_freq = kr260_pwm_get_frequency_hz();
    bool pwm_active = kr260_pwm_is_signal_active();

    bool i2s_active = audio_leak_is_active();

    shell_print(sh,
        "{\"interface_loopback_test\": {"
        "\"i2c_target_0x58\": \"%s\", "
        "\"io_lines\": {\"start_stop\": %s, \"doctor_estop_btn\": %s, \"solenoid\": %s, \"kr260_safety_tripped\": %s, \"estop\": %s}, "
        "\"pwm_capture\": {\"active\": %s, \"duty_pct\": %.2f, \"freq_hz\": %u}, "
        "\"i2s_audio_leak\": {\"active\": %s}, "
        "\"status\": \"READY\"}}",
        i2c_status,
        io_start ? "true" : "false", io_estop_btn ? "true" : "false", io_sol ? "true" : "false",
        io_tripped ? "true" : "false", io_estop ? "true" : "false",
        pwm_active ? "true" : "false", (double)(pwm_duty * 100.0f), pwm_freq,
        i2s_active ? "true" : "false"
    );

    return 0;
}

/* ลงทะเบียนคำสั่ง CLI ย่อย */
SHELL_STATIC_SUBCMD_SET_CREATE(sub_hil,
    SHELL_CMD(status, NULL, "Get full HIL plant status (JSON)", cmd_hil_status),
    SHELL_CMD(scenario, NULL, "Apply named clinical scenario <normal|low_pressure|over_expansion|gas_leak|...>", cmd_hil_scenario),
    SHELL_CMD(set_state, NULL, "Force FSM state <IDLE|INSUFFLATE|INSPECT|LEAK|DEFLATE|ESTOP>", cmd_hil_set_state),
    SHELL_CMD(set_pressure, NULL, "Set fixed pressure value in kPa", cmd_hil_set_pressure),
    SHELL_CMD(auto, NULL, "Enable or disable auto physics simulation <0|1>", cmd_hil_auto),
    SHELL_CMD(inject_leak, NULL, "Inject or clear gas leak <0|1>", cmd_hil_inject_leak),
    SHELL_CMD(audio_leak, NULL, "Control AC Audio Leak Generator <0|1>", cmd_hil_audio_leak),
    SHELL_CMD(button, NULL, "Simulate Doctor Start/Stop/E-Stop button <start|stop|estop_on|estop_off|pulse|status>", cmd_hil_button),
    SHELL_CMD(set_start_stop, NULL, "Set Start/Stop IO command <0|1>", cmd_hil_start_stop),
    SHELL_CMD(set_estop, NULL, "Set Doctor E-Stop & Safety Flag <0|1>", cmd_hil_estop),
    SHELL_CMD(set_safety_tripped, NULL, "Set KR260 Safety Tripped Status IO <0|1>", cmd_hil_safety_tripped),
    SHELL_CMD(set_solenoid, NULL, "Set Solenoid Purge Valve <0|1>", cmd_hil_solenoid),
    SHELL_CMD(reset, NULL, "Reset plant simulator to default IDLE", cmd_hil_reset),
    SHELL_CMD(loopback, NULL, "Execute I2C loopback test", cmd_hil_loopback),
    SHELL_CMD(test_gpio, NULL, "Read physical GPIO levels (D3, D5, D4, D6)", cmd_hil_test_gpio),
    SHELL_CMD(test_interfaces, NULL, "Execute all interface loopback & status tests", cmd_hil_test_interfaces),
    SHELL_SUBCMD_SET_END
);

SHELL_CMD_REGISTER(hil, &sub_hil, "HIL GI Simulator Testbench API", NULL);

/* -------------------------------------------------------------------------- */
/* ฟังก์ชัน Main เริ่มต้นระบบ                                                  */
/* -------------------------------------------------------------------------- */
int main(void)
{
    LOG_INF("==================================================");
    LOG_INF(" STM32H5 HIL Plant Simulator Initializing...     ");
    LOG_INF(" GI Insufflator, Audio Leak & Camera Mock Core    ");
    LOG_INF(" OS: Zephyr RTOS | Target: Nucleo-H563ZI         ");
    LOG_INF("==================================================");

    k_mutex_init(&g_i2c_mutex);

    // 1. เริ่มต้น Subsystems ทั้งหมด
    gi_state_machine_init();
    audio_leak_init();
    io_controller_init();

    // 2. กำหนดค่า Buffer เริ่มต้น
    g_i2c_buffer[REG_CHIP_ID] = TARGET_I2C_ADDR;
    g_i2c_buffer[REG_STATUS]  = 0x00;

    // 3. ผูก I2C Target EEPROM Device
    g_target_dev = DEVICE_DT_GET(DT_ALIAS(hil_target));
    if (!device_is_ready(g_target_dev)) {
        LOG_ERR("Target device (hil-target) is NOT ready!");
        return -ENODEV;
    }
    update_eeprom_memory();

    // 4. เริ่มต้น PWM Receiver จาก KR260
    int ret = kr260_pwm_receiver_init();
    if (ret != 0) {
        LOG_WRN("KR260 PWM Receiver init returned %d (Pin may not be driven yet)", ret);
    }

    LOG_INF("I2C Target registered at address 0x%02X successfully.", TARGET_I2C_ADDR);
    LOG_INF("Zephyr Shell ready. Type 'hil status' to inspect system.");

    return 0;
}
