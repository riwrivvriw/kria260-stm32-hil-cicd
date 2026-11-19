/**
 * @file io_controller.h
 * @brief จัดการขา Hardware GPIO สำหรับคำสั่ง Start/Stop, Solenoid Valve, และ E-Stop จาก KR260
 */

#ifndef IO_CONTROLLER_H_
#define IO_CONTROLLER_H_

#include <zephyr/kernel.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief เริ่มต้นกำหนดค่า GPIO สำหรับสัญญาณควบคุมจาก KR260
 */
int io_controller_init(void);

/**
 * @brief อ่านสถานะสัญญาณ Start/Stop (สถานะปัจจุบันที่กำลังขับออกไปยัง KR260)
 */
bool io_controller_get_start_stop(void);

/**
 * @brief สั่งขับสัญญาณจำลองปุ่มกดของแพทย์ (Mock Doctor Button) ออกไปยัง KR260
 * @param active true = สั่งเริ่มทำงาน (Start: ระดับ 3.3V), false = สั่งหยุดทำงาน (Stop: ระดับ 0V)
 * @return 0 เมื่อสำเร็จ, ค่าลบเมื่อเกิดข้อผิดพลาด
 */
int io_controller_set_doctor_button(bool active);

/**
 * @brief ส่งสัญญาณพัลส์จำลองการกดปุ่ม Start/Stop แบบ Momentary Switch
 * @param duration_ms ความกว้างพัลส์ในหน่วยมิลลิวินาที (เช่น 200 ms)
 * @return 0 เมื่อสำเร็จ
 */
int io_controller_pulse_doctor_button(uint32_t duration_ms);

/**
 * @brief อ่านสถานะสัญญาณ Emergency Stop จาก KR260
 */
bool io_controller_get_estop(void);

/**
 * @brief อ่านสถานะ Solenoid Valve Command จาก KR260 (Physical Pin หรือ Mock Override)
 * @note วาล์ว Solenoid ทำงานผ่านวงจรขับ N-Channel MOSFET แบบ Normally Open (NO):
 *       - ระดับแรงดัน HIGH (3.3V) -> MOSFET นำกระแส -> ขดลวดดึงแกน "ปิดวาล์ว" (Holding Gas)
 *       - ระดับแรงดัน LOW (0V)    -> MOSFET ดับ       -> ขดลวดคลายตัว "เปิดวาล์ว" (Venting Gas / Over-Expansion)
 * @return true = วาล์วเปิดระบายก๊าซ (Vent / Active Release), false = วาล์วปิดกักก๊าซ (Holding Pressure)
 */
bool io_controller_get_solenoid_valve(void);

/**
 * @brief บังคับค่าจำลองสัญญาณ Start/Stop ผ่านคำสั่ง UART Shell
 */
void io_controller_set_mock_start_stop(bool active);

/**
 * @brief บังคับค่าจำลองสัญญาณ Emergency Stop ผ่านคำสั่ง UART Shell
 */
void io_controller_set_mock_estop(bool active);

/**
 * @brief บังคับค่าจำลองสัญญาณ Solenoid Valve ผ่านคำสั่ง UART Shell
 */
void io_controller_set_mock_solenoid(bool active);

#ifdef __cplusplus
}
#endif

#endif /* IO_CONTROLLER_H_ */
