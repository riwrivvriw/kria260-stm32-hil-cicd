/**
 * @file io_controller.h
 * @brief จัดการขา Hardware GPIO สำหรับ Dual E-Stop, Start/Stop, และ Solenoid Valve
 *        - Doctor Start/Stop Button (Output -> KR260 Pin D3 / PE13)
 *        - Doctor E-Stop Button     (Output -> KR260 Pin D5 / PE11)
 *        - Solenoid Purge Valve     (Input  <- KR260 Pin D4 / PE14)
 *        - KR260 Safety Tripped     (Input  <- KR260 Pin D6 / PE9)
 */

#ifndef IO_CONTROLLER_H_
#define IO_CONTROLLER_H_

#include <zephyr/kernel.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief เริ่มต้นกำหนดค่า GPIO สำหรับสัญญาณควบคุมทั้งหมด
 */
int io_controller_init(void);

/**
 * @brief อ่านสถานะสัญญาณ Start/Stop (สถานะปัจจุบันที่กำลังขับออกไปยัง KR260)
 */
bool io_controller_get_start_stop(void);

/**
 * @brief สั่งขับสัญญาณจำลองปุ่มกดของแพทย์ (Mock Doctor Button) ออกไปยัง KR260 (Arduino D3)
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
 * @brief สั่งขับสัญญาณจำลองปุ่ม Emergency Stop ของแพทย์ (Mock Doctor E-Stop Button) ออกไปยัง KR260 (Arduino D5)
 * @param active true = กดปุ่ม E-Stop (3.3V), false = ปล่อยปุ่ม E-Stop (0V)
 * @return 0 เมื่อสำเร็จ
 */
int io_controller_set_doctor_estop(bool active);

/**
 * @brief อ่านสถานะการขับปุ่ม Emergency Stop ของแพทย์ปัจจุบัน (Arduino D5)
 */
bool io_controller_get_doctor_estop(void);

/**
 * @brief อ่านสถานะสัญญาณ Safety Tripped จาก KR260 (Arduino D6)
 *        (KR260 ส่งสัญญาณระดับ HIGH เมื่อฮาร์ดแวร์หรือ Vitis AI ตัดการทำงานฉุกเฉิน)
 */
bool io_controller_get_safety_tripped(void);

/**
 * @brief อ่านสถานะ Emergency Stop สรุปรวม (รวมทั้ง Doctor E-Stop Button, KR260 Tripped, และ Mock)
 */
bool io_controller_get_estop(void);

/**
 * @brief อ่านสถานะ Solenoid Valve Command จาก KR260 (Arduino D4)
 * @return true = วาล์วเปิดระบายก๊าซ (Vent / Active Release), false = วาล์วปิดกักก๊าซ (Holding Pressure)
 */
bool io_controller_get_solenoid_valve(void);

/**
 * @brief บังคับค่าจำลองสัญญาณ Start/Stop ผ่านคำสั่ง UART Shell
 */
void io_controller_set_mock_start_stop(bool active);

/**
 * @brief บังคับค่าจำลองสัญญาณ Doctor E-Stop Button ผ่านคำสั่ง UART Shell
 */
void io_controller_set_mock_estop(bool active);

/**
 * @brief บังคับค่าจำลองสัญญาณ KR260 Safety Tripped ผ่านคำสั่ง UART Shell
 */
void io_controller_set_mock_safety_tripped(bool active);

/**
 * @brief บังคับค่าจำลองสัญญาณ Solenoid Valve ผ่านคำสั่ง UART Shell
 */
void io_controller_set_mock_solenoid(bool active);

/**
 * @brief ล้างค่า Mock Overrides ทั้งหมดเพื่อกลับมาอ่านค่าจากพินฮาร์ดแวร์จริง
 */
void io_controller_clear_mock_overrides(void);

/**
 * @brief อ่านระดับแรงดันลอจิก (0 หรือ 1) โดยตรงจากพินฮาร์ดแวร์
 */
int io_controller_get_physical_levels(int *d3_start_out, int *d5_estop_btn_out,
                                      int *d4_sol_in, int *d6_tripped_in);

#ifdef __cplusplus
}
#endif

#endif /* IO_CONTROLLER_H_ */
