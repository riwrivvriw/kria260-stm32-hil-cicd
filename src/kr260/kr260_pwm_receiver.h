/**
 * @file kr260_pwm_receiver.h
 * @brief ไดรเวอร์สำหรับรับและตรวจวัดสัญญาณ PWM จากบอร์ด Kria KR260 (Airpump PWM)
 * @project HIL Testbench & GI Detect System
 */

#ifndef KR260_PWM_RECEIVER_H_
#define KR260_PWM_RECEIVER_H_

#include <zephyr/kernel.h>
#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief เริ่มต้นระบบตรวจจับสัญญาณ PWM จาก KR260
 * @return 0 หากสำเร็จ, ค่าติดลบหากเกิดข้อผิดพลาด
 */
int kr260_pwm_receiver_init(void);

/**
 * @brief อ่านค่า Duty Cycle ปัจจุบันที่ส่งมาจาก KR260
 * @return ค่า Duty Cycle ในช่วง 0.0f (0%) ถึง 1.0f (100%)
 */
float kr260_pwm_get_duty_cycle(void);

/**
 * @brief อ่านค่าความถี่ของสัญญาณ PWM ที่วัดได้
 * @return ความถี่ในหน่วย Hertz (Hz)
 */
uint32_t kr260_pwm_get_frequency_hz(void);

/**
 * @brief ตรวจสอบว่ามีสัญญาณ PWM ส่งมาจาก KR260 อยู่หรือไม่
 * @return true หากตรวจพบสัญญาณต่อเนื่อง, false หากไม่มีสัญญาณ (Timeout)
 */
bool kr260_pwm_is_signal_active(void);

#ifdef __cplusplus
}
#endif

#endif /* KR260_PWM_RECEIVER_H_ */
