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
 * @brief อ่านสถานะสัญญาณ Start/Stop จาก KR260 (Physical Pin หรือ Mock Override)
 */
bool io_controller_get_start_stop(void);

/**
 * @brief อ่านสถานะสัญญาณ Emergency Stop จาก KR260
 */
bool io_controller_get_estop(void);

/**
 * @brief อ่านสถานะสัญญาณ Solenoid Valve Command จาก KR260
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
