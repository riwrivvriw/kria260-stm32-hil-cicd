/**
 * @file gi_state_machine.c
 * @brief การทำงานของ State Machine จำลองสภาพแวดล้อมทางเดินอาหารและกล้องส่องตรวจ
 */

#include "gi_state_machine.h"
#include "io_controller.h"
#include <strings.h>
#include <string.h>
#include <zephyr/logging/log.h>

LOG_MODULE_REGISTER(gi_state_machine, LOG_LEVEL_INF);

#define AMBIENT_PRESSURE_KPA   101.325f
#define DEFAULT_TARGET_KPA     125.0f
#define OVERPRESSURE_LIMIT_KPA 150.0f

static struct k_mutex g_sm_mutex;
static gi_system_status_t g_status;

void gi_state_machine_init(void)
{
    k_mutex_init(&g_sm_mutex);

    g_status.state = GI_STATE_IDLE;
    g_status.current_pressure_kpa = AMBIENT_PRESSURE_KPA;
    g_status.target_pressure_kpa = DEFAULT_TARGET_KPA;
    g_status.pump_duty = 0.0f;
    g_status.pwm_freq_hz = 0;
    g_status.leak_active = false;
    g_status.solenoid_valve_open = false;
    g_status.audio_leak_active = false;
    g_status.start_stop_io = false;
    g_status.estop_active = false;
    g_status.doctor_estop_btn = false;
    g_status.kr260_safety_tripped = false;
    g_status.auto_simulation = true;
    g_status.camera_scene = "STANDBY_PRE_PROCEDURE";

    LOG_INF("GI State Machine Initialized in IDLE state.");
}

gi_state_t gi_state_machine_get_state(void)
{
    gi_state_t s;
    k_mutex_lock(&g_sm_mutex, K_FOREVER);
    s = g_status.state;
    k_mutex_unlock(&g_sm_mutex);
    return s;
}

const char* gi_state_to_str(gi_state_t state)
{
    switch (state) {
    case GI_STATE_IDLE:              return "IDLE";
    case GI_STATE_INSUFFLATION:      return "INSUFFLATION";
    case GI_STATE_STABLE_INSPECTION: return "STABLE_INSPECTION";
    case GI_STATE_LEAK_EVENT:        return "LEAK_EVENT";
    case GI_STATE_DEFLATION_STOP:    return "DEFLATION_STOP";
    case GI_STATE_EMERGENCY_STOP:    return "EMERGENCY_STOP";
    default:                         return "UNKNOWN";
    }
}

const char* gi_state_get_camera_scene(gi_state_t state)
{
    switch (state) {
    case GI_STATE_IDLE:
        return "STANDBY_EXTERNAL_VIEW";
    case GI_STATE_INSUFFLATION:
        return "LUMEN_EXPANDING_INSUFFLATION";
    case GI_STATE_STABLE_INSPECTION:
        return "MUCOSAL_INSPECTION_POLYP_ACTIVE";
    case GI_STATE_LEAK_EVENT:
        return "CAVITY_COLLAPSING_TURBULENT_BUBBLES";
    case GI_STATE_DEFLATION_STOP:
        return "DESUFFLATION_SCOPE_RETRACTION";
    case GI_STATE_EMERGENCY_STOP:
        return "EMERGENCY_FREEZE_WARNING_OVERLAY";
    default:
        return "UNKNOWN_SCENE";
    }
}

void gi_state_machine_set_state(gi_state_t new_state)
{
    k_mutex_lock(&g_sm_mutex, K_FOREVER);
    g_status.state = new_state;
    g_status.camera_scene = gi_state_get_camera_scene(new_state);

    if (new_state == GI_STATE_LEAK_EVENT) {
        g_status.leak_active = true;
        g_status.audio_leak_active = true;
    } else if (new_state == GI_STATE_DEFLATION_STOP) {
        g_status.solenoid_valve_open = true;
        g_status.audio_leak_active = false;
    } else if (new_state == GI_STATE_EMERGENCY_STOP) {
        g_status.estop_active = true;
        g_status.solenoid_valve_open = true;
        g_status.audio_leak_active = false;
    } else {
        g_status.audio_leak_active = false;
        g_status.solenoid_valve_open = false;
    }

    LOG_INF("State explicitly set to: %s", gi_state_to_str(new_state));
    k_mutex_unlock(&g_sm_mutex);
}

void gi_state_machine_update(float dt, float pump_duty, uint32_t pwm_freq,
                             bool start_stop_pin, bool doctor_estop_btn,
                             bool kr260_safety_tripped, bool solenoid_valve_pin)
{
    k_mutex_lock(&g_sm_mutex, K_FOREVER);

    g_status.pump_duty = pump_duty;
    g_status.pwm_freq_hz = pwm_freq;
    g_status.start_stop_io = start_stop_pin;
    g_status.doctor_estop_btn = doctor_estop_btn;
    g_status.kr260_safety_tripped = kr260_safety_tripped;

    bool estop_asserted = doctor_estop_btn || kr260_safety_tripped;
    g_status.estop_active = estop_asserted;
    g_status.solenoid_valve_open = solenoid_valve_pin;

    // 1. ตรวจสอบ Emergency Stop (ความสำคัญสูงสุด)
    if (estop_asserted || g_status.current_pressure_kpa >= OVERPRESSURE_LIMIT_KPA) {
        if (g_status.state != GI_STATE_EMERGENCY_STOP) {
            g_status.state = GI_STATE_EMERGENCY_STOP;
            g_status.solenoid_valve_open = true;
            g_status.audio_leak_active = false;
            LOG_ERR("EMERGENCY STOP TRIGGERED! (P=%.2f kPa, DoctorBtn=%d, KR260Tripped=%d)",
                    (double)g_status.current_pressure_kpa, doctor_estop_btn, kr260_safety_tripped);
        }
    }

    // 2. State Machine Transitions
    switch (g_status.state) {
    case GI_STATE_IDLE:
        g_status.audio_leak_active = false;
        // เริ่มต้นการอัดก๊าซ (INSUFFLATION) เฉพาะเมื่อ KR260 ส่งสัญญาณ PWM มาขับปั๊มลมจริงๆ (Strict Hardware-Driven)
        if (pump_duty > 0.05f) {
            g_status.state = GI_STATE_INSUFFLATION;
            LOG_INF("Transition -> INSUFFLATION (KR260 Air Pump PWM active: %.1f%%)",
                    (double)(pump_duty * 100.0f));
        }
        break;

    case GI_STATE_INSUFFLATION:
        if (g_status.leak_active) {
            g_status.state = GI_STATE_LEAK_EVENT;
            g_status.audio_leak_active = true;
            LOG_WRN("Transition -> LEAK_EVENT (Air leak detected during insufflation)");
        } else if (solenoid_valve_pin || (!start_stop_pin && pump_duty < 0.02f)) {
            g_status.state = GI_STATE_DEFLATION_STOP;
            g_status.solenoid_valve_open = true;
            LOG_INF("Transition -> DEFLATION_STOP (Procedure stopped or valve venting)");
        } else if (g_status.current_pressure_kpa >= (g_status.target_pressure_kpa - 2.5f)) {
            g_status.state = GI_STATE_STABLE_INSPECTION;
            LOG_INF("Transition -> STABLE_INSPECTION (Target reached: %.2f kPa)",
                    (double)g_status.current_pressure_kpa);
        }
        break;

    case GI_STATE_STABLE_INSPECTION:
        g_status.audio_leak_active = false;
        if (g_status.leak_active) {
            g_status.state = GI_STATE_LEAK_EVENT;
            g_status.audio_leak_active = true;
            LOG_WRN("Transition -> LEAK_EVENT (Air leak detected during inspection)");
        } else if (solenoid_valve_pin || (!start_stop_pin && pump_duty < 0.02f)) {
            g_status.state = GI_STATE_DEFLATION_STOP;
            g_status.solenoid_valve_open = true;
            LOG_INF("Transition -> DEFLATION_STOP (Stop asserted or valve venting)");
        } else if (g_status.current_pressure_kpa < (g_status.target_pressure_kpa - 8.0f)) {
            // ความดันตกต่ำกว่าเกณฑ์ กลับไปเร่งปั๊มใหม่
            g_status.state = GI_STATE_INSUFFLATION;
            LOG_INF("Transition back -> INSUFFLATION (Pressure low: %.2f kPa)",
                    (double)g_status.current_pressure_kpa);
        }
        break;

    case GI_STATE_LEAK_EVENT:
        g_status.audio_leak_active = true;
        if (!g_status.leak_active) {
            // ซ่อมรอยรั่วหรือเคลียร์สถานะรั่วแล้ว
            g_status.audio_leak_active = false;
            g_status.state = GI_STATE_INSUFFLATION;
            LOG_INF("Transition -> INSUFFLATION (Leak cleared, repressurizing)");
        } else if (!start_stop_pin && pump_duty < 0.02f) {
            g_status.state = GI_STATE_DEFLATION_STOP;
            g_status.audio_leak_active = false;
            g_status.solenoid_valve_open = true;
            LOG_INF("Transition -> DEFLATION_STOP");
        }
        break;

    case GI_STATE_DEFLATION_STOP:
        g_status.solenoid_valve_open = true;
        g_status.audio_leak_active = false;
        // เมื่อความดันระบายลงจนใกล้เคียงบรรยากาศ ให้กลับสู่ IDLE
        if (g_status.current_pressure_kpa <= (AMBIENT_PRESSURE_KPA + 1.0f)) {
            g_status.state = GI_STATE_IDLE;
            g_status.solenoid_valve_open = false;
            LOG_INF("Transition -> IDLE (Pressure back to ambient)");
        }
        break;

    case GI_STATE_EMERGENCY_STOP:
        g_status.solenoid_valve_open = true;
        g_status.audio_leak_active = false;
        // ปลด E-Stop ผ่านคำสั่ง reset หรือปล่อยขาสัญญาณ
        if (!estop_asserted && g_status.current_pressure_kpa <= AMBIENT_PRESSURE_KPA + 2.0f) {
            // รอคำสั่ง Explicit Reset จากผู้ใช้
        }
        break;
    }

    // 3. คำนวณสมการพลศาสตร์ Closed-Loop (เมื่อเปิด Auto Simulation)
    if (g_status.auto_simulation) {
        const float k_pump = 28.0f; // อัตราปั๊ม (kPa/s ที่ 100% duty)
        const float k_leak = 22.0f; // อัตราการรั่ว (kPa/s)
        const float k_vent = 35.0f; // อัตราการระบายของวาล์ว Solenoid

        float effective_duty = (g_status.state == GI_STATE_EMERGENCY_STOP) ? 0.0f : pump_duty;
        float dp = (k_pump * effective_duty) * dt;

        // หักลบผลจากการรั่ว (อัตรา 22 kPa/s)
        if ((g_status.leak_active || g_status.state == GI_STATE_LEAK_EVENT) &&
            g_status.current_pressure_kpa > AMBIENT_PRESSURE_KPA) {
            float overpressure = g_status.current_pressure_kpa - AMBIENT_PRESSURE_KPA;
            float leak_decay = (overpressure > 24.0f) ? k_leak : (k_leak * (overpressure / 24.0f));
            if (leak_decay < 1.0f) leak_decay = 1.0f;
            dp -= leak_decay * dt;
        }

        // หักลบผลจากวาล์ว Solenoid ระบายก๊าซ (อัตรา 35 kPa/s)
        if (g_status.solenoid_valve_open && g_status.current_pressure_kpa > AMBIENT_PRESSURE_KPA) {
            float overpressure = g_status.current_pressure_kpa - AMBIENT_PRESSURE_KPA;
            float vent_decay = (overpressure > 24.0f) ? k_vent : (k_vent * (overpressure / 24.0f));
            if (vent_decay < 1.0f) vent_decay = 1.0f;
            dp -= vent_decay * dt;
        } else if (effective_duty < 0.02f && g_status.current_pressure_kpa > AMBIENT_PRESSURE_KPA) {
            // ซึมออกตามธรรมชาติเล็กน้อย
            dp -= 0.3f * (g_status.current_pressure_kpa - AMBIENT_PRESSURE_KPA) * dt;
        }

        g_status.current_pressure_kpa += dp;
        if (g_status.current_pressure_kpa < AMBIENT_PRESSURE_KPA) {
            g_status.current_pressure_kpa = AMBIENT_PRESSURE_KPA;
        }
    }

    g_status.camera_scene = gi_state_get_camera_scene(g_status.state);

    k_mutex_unlock(&g_sm_mutex);
}

void gi_state_machine_get_status(gi_system_status_t *out_status)
{
    if (!out_status) return;
    k_mutex_lock(&g_sm_mutex, K_FOREVER);
    *out_status = g_status;
    k_mutex_unlock(&g_sm_mutex);
}

int gi_state_machine_apply_scenario(const char *name, float custom_val)
{
    if (!name) return -EINVAL;

    k_mutex_lock(&g_sm_mutex, K_FOREVER);

    // เมื่อเริ่ม Scenario ทางคลินิก ระบบถือว่าแพทย์เริ่มการตรวจ (Doctor Start = true)
    g_status.start_stop_io = true;
    io_controller_set_doctor_button(true);

    if (strcasecmp(name, "normal") == 0) {
        g_status.state = GI_STATE_STABLE_INSPECTION;
        g_status.current_pressure_kpa = (custom_val > 0) ? custom_val : DEFAULT_TARGET_KPA;
        g_status.leak_active = false;
        g_status.audio_leak_active = false;
        g_status.solenoid_valve_open = false;
        g_status.auto_simulation = true;
        LOG_INF("Scenario applied: NORMAL (P=%.2f kPa)", (double)g_status.current_pressure_kpa);
    } else if (strcasecmp(name, "low_pressure") == 0) {
        g_status.state = GI_STATE_INSUFFLATION;
        g_status.current_pressure_kpa = (custom_val > 0) ? custom_val : 110.0f;
        g_status.leak_active = false;
        g_status.audio_leak_active = false;
        g_status.solenoid_valve_open = false;
        g_status.auto_simulation = true;
        LOG_INF("Scenario applied: LOW_PRESSURE (P=%.2f kPa)", (double)g_status.current_pressure_kpa);
    } else if (strcasecmp(name, "over_expansion") == 0 || strcasecmp(name, "overpressure") == 0) {
        // เมื่อความดันเกินเพดานความปลอดภัย (150 kPa) ระบบจะตัดเข้า EMERGENCY_STOP เพื่อระบายก๊าซทิ้ง
        g_status.current_pressure_kpa = (custom_val > 0) ? custom_val : 152.0f;
        g_status.state = GI_STATE_EMERGENCY_STOP;
        g_status.leak_active = false;
        g_status.audio_leak_active = false;
        g_status.solenoid_valve_open = true;
        g_status.auto_simulation = true;
        LOG_INF("Scenario applied: OVER_EXPANSION (P=%.2f kPa, Safety Hazard Cutoff)", (double)g_status.current_pressure_kpa);
    } else if (strcasecmp(name, "gas_leak") == 0) {
        g_status.state = GI_STATE_LEAK_EVENT;
        g_status.current_pressure_kpa = (custom_val > 0) ? custom_val : 125.0f;
        g_status.leak_active = true;
        g_status.audio_leak_active = true;
        g_status.solenoid_valve_open = false;
        g_status.auto_simulation = true;
        LOG_INF("Scenario applied: GAS_LEAK (P=%.2f kPa, Audio Leak Active)", (double)g_status.current_pressure_kpa);
    } else if (strcasecmp(name, "tube_kink") == 0) {
        g_status.state = GI_STATE_INSUFFLATION;
        g_status.current_pressure_kpa = (custom_val > 0) ? custom_val : AMBIENT_PRESSURE_KPA;
        g_status.leak_active = false;
        g_status.audio_leak_active = false;
        g_status.solenoid_valve_open = false;
        g_status.auto_simulation = false; // Block pressure rise to simulate occlusion
        LOG_INF("Scenario applied: TUBE_KINK / OCCLUSION (P=%.2f kPa, Flat)", (double)g_status.current_pressure_kpa);
    } else if (strcasecmp(name, "cough_spike") == 0) {
        // อาการไอชั่วคราว ดันขึ้นสูงใกล้ขอบเขตปลอดภัย (145 kPa) แต่ยังไม่ตัดฉุกเฉิน
        g_status.state = GI_STATE_STABLE_INSPECTION;
        g_status.current_pressure_kpa = (custom_val > 0) ? custom_val : 145.0f;
        g_status.leak_active = false;
        g_status.audio_leak_active = false;
        g_status.solenoid_valve_open = false;
        g_status.auto_simulation = true;
        LOG_INF("Scenario applied: COUGH_SPIKE (P=%.2f kPa, Transient)", (double)g_status.current_pressure_kpa);
    } else {
        k_mutex_unlock(&g_sm_mutex);
        return -ENOENT;
    }

    g_status.camera_scene = gi_state_get_camera_scene(g_status.state);
    k_mutex_unlock(&g_sm_mutex);
    return 0;
}

void gi_state_machine_inject_leak(bool active)
{
    k_mutex_lock(&g_sm_mutex, K_FOREVER);
    g_status.leak_active = active;
    g_status.auto_simulation = true;
    if (active) {
        g_status.state = GI_STATE_LEAK_EVENT;
        g_status.audio_leak_active = true;
    }
    k_mutex_unlock(&g_sm_mutex);
}

void gi_state_machine_set_fixed_pressure(float pressure_kpa)
{
    k_mutex_lock(&g_sm_mutex, K_FOREVER);
    g_status.auto_simulation = false;
    g_status.current_pressure_kpa = pressure_kpa;
    k_mutex_unlock(&g_sm_mutex);
}

void gi_state_machine_set_auto(bool enable)
{
    k_mutex_lock(&g_sm_mutex, K_FOREVER);
    g_status.auto_simulation = enable;
    k_mutex_unlock(&g_sm_mutex);
}

void gi_state_machine_set_solenoid(bool open_valve)
{
    k_mutex_lock(&g_sm_mutex, K_FOREVER);
    g_status.solenoid_valve_open = open_valve;
    k_mutex_unlock(&g_sm_mutex);
}

void gi_state_machine_reset(void)
{
    k_mutex_lock(&g_sm_mutex, K_FOREVER);
    g_status.state = GI_STATE_IDLE;
    g_status.current_pressure_kpa = AMBIENT_PRESSURE_KPA;
    g_status.leak_active = false;
    g_status.solenoid_valve_open = false;
    g_status.audio_leak_active = false;
    g_status.estop_active = false;
    g_status.doctor_estop_btn = false;
    g_status.kr260_safety_tripped = false;
    g_status.auto_simulation = true;
    g_status.camera_scene = gi_state_get_camera_scene(GI_STATE_IDLE);
    LOG_INF("GI State Machine Reset to IDLE.");
    k_mutex_unlock(&g_sm_mutex);
}
