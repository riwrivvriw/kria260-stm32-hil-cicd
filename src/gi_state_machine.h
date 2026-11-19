/**
 * @file gi_state_machine.h
 * @brief Finite State Machine จำลองสภาพแวดล้อมทางเดินอาหาร (GI Environment)
 *        รวมถึงการปั๊มก๊าซ (Insufflation) และสถานะกล้องส่องตรวจ (Mock Camera Inside GI)
 */

#ifndef GI_STATE_MACHINE_H_
#define GI_STATE_MACHINE_H_

#include <zephyr/kernel.h>
#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief สถานะการทำงานของระบบส่องกล้องทางเดินอาหาร (GI Endoscopy System)
 */
typedef enum {
    GI_STATE_IDLE               = 0x00, /* Standby: ความดันบรรยากาศ (~101.3 kPa), กล้องรอเริ่มตรวจ, ปั๊มดับ */
    GI_STATE_INSUFFLATION       = 0x01, /* ปั๊มก๊าซเข้ากระเพาะ: KR260 ขับ PWM, ความดันเพิ่มขึ้น, กล้องเห็นโพรงขยายตัว */
    GI_STATE_STABLE_INSPECTION  = 0x02, /* ความดันคงที่ (~120-130 kPa): ส่องตรวจรอยโรค (Polyp), กล้องชัดเจน */
    GI_STATE_LEAK_EVENT         = 0x03, /* เกิดก๊าซรั่ว: ความดันลดลงฮวบ, ส่งเสียงลมรั่ว AC Audio, กล้องเห็นภาพยุบตัว */
    GI_STATE_DEFLATION_STOP     = 0x04, /* สิ้นสุดการตรวจ/ระบายก๊าซ: เปิด Solenoid Valve ระบายความดันกลับสู่ปกติ */
    GI_STATE_EMERGENCY_STOP     = 0x05, /* ตัดฉุกเฉิน (E-Stop): สั่งตัดปั๊มทันที, เปิดวาล์วระบาย, ระบบหยุดทำงาน */
} gi_state_t;

/**
 * @brief โครงสร้างข้อมูลสถานะโดยรวมของระบบ HIL Plant Simulator
 */
typedef struct {
    gi_state_t state;
    float current_pressure_kpa;
    float target_pressure_kpa;
    float pump_duty;            /* 0.0 - 1.0 (0% - 100%) */
    uint32_t pwm_freq_hz;
    bool leak_active;
    bool solenoid_valve_open;   /* true = เปิดวาล์วระบายก๊าซ (Vent) */
    bool audio_leak_active;     /* true = กำลังขับสัญญาณเสียงลมรั่ว AC Audio */
    bool start_stop_io;         /* สถานะลอจิก Start/Stop จาก KR260 */
    bool estop_active;          /* สถานะลอจิก Emergency Stop จาก KR260 */
    bool auto_simulation;       /* true = คำนวณสมการพลศาสตร์ตามเวลาจริง */
    const char *camera_scene;   /* คำอธิบายฉากวิดีโอที่ต้องสตรีมผ่าน Ethernet */
} gi_system_status_t;

/**
 * @brief เริ่มต้นระบบ State Machine
 */
void gi_state_machine_init(void);

/**
 * @brief อ่านสถานะปัจจุบันของ State Machine
 */
gi_state_t gi_state_machine_get_state(void);

/**
 * @brief แปลง Enum เป็นข้อความ String
 */
const char* gi_state_to_str(gi_state_t state);

/**
 * @brief อ่านชื่อฉากวิดีโอของกล้องส่องตรวจจำลองที่สอดคล้องกับสถานะปัจจุบัน
 */
const char* gi_state_get_camera_scene(gi_state_t state);

/**
 * @brief กำหนดสถานะใหม่ให้กับ State Machine (ใช้สำหรับ Test API / Shell)
 */
void gi_state_machine_set_state(gi_state_t new_state);

/**
 * @brief คำนวณและอัปเดต State Machine ตามสภาวะอินพุตจาก KR260 (PWM, IO, E-Stop, Solenoid)
 * @param dt คาบเวลาการคำนวณในหน่วยวินาที (เช่น 0.05s)
 * @param pump_duty ค่า Duty Cycle ที่วัดได้จาก KR260 (0.0 - 1.0)
 * @param pwm_freq ค่าความถี่ PWM (Hz)
 * @param start_stop_pin ลอจิกขา Start/Stop IO จาก KR260
 * @param estop_pin ลอจิกขา E-Stop จาก KR260
 * @param solenoid_valve_pin ลอจิกสถานะวาล์วเปิดระบายก๊าซ (true = เปิดวาล์วระบาย / Vent)
 */
void gi_state_machine_update(float dt, float pump_duty, uint32_t pwm_freq,
                             bool start_stop_pin, bool estop_pin, bool solenoid_valve_pin);

/**
 * @brief ดึงข้อมูลสถานะทั้งหมดแบบ Thread-safe
 */
void gi_state_machine_get_status(gi_system_status_t *out_status);

/**
 * @brief โหลดและสั่งรัน Scenario ทางคลินิกตามชื่อ (Dynamic Clinical Scenario)
 * @param name ชื่อ Scenario (เช่น "normal", "low_pressure", "over_expansion", "gas_leak", "tube_kink", "cough_spike")
 * @param custom_val ค่าพารามิเตอร์ความดันเริ่มต้น (กำหนด 0.0f เพื่อใช้ค่า Default ของ Scenario นั้น)
 * @return 0 เมื่อสำเร็จ, -ENOENT หากไม่พบชื่อ Scenario
 */
int gi_state_machine_apply_scenario(const char *name, float custom_val);

/**
 * @brief สั่งจำลองการรั่วของก๊าซ (Leak Injection)
 */
void gi_state_machine_inject_leak(bool active);

/**
 * @brief กำหนดค่าความดันคงที่ (ปิด Auto Simulation)
 */
void gi_state_machine_set_fixed_pressure(float pressure_kpa);

/**
 * @brief ควบคุมโซลินอยด์วาล์วระบายก๊าซ
 */
void gi_state_machine_set_solenoid(bool open_valve);

/**
 * @brief รีเซ็ตสถานะระบบกลับสู่ค่าเริ่มต้น (IDLE)
 */
void gi_state_machine_reset(void);

#ifdef __cplusplus
}
#endif

#endif /* GI_STATE_MACHINE_H_ */
