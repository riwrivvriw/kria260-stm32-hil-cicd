/**
 * @file audio_leak.h
 * @brief โมดูลจำลองสัญญาณเสียงลมรั่วดิจิทัล (Digital I2S Audio Leak Simulator)
 *        สร้างสัญญาณดิจิทัล PCM Stereo Frame (จำลอง Digital MEMS Mic) ผ่าน I2S2
 *        - BCLK   : PB13 (Arduino D18)
 *        - WS     : PB12 (Arduino D19)
 *        - SD/DOUT: PB15 (Arduino D17)
 */

#ifndef AUDIO_LEAK_H_
#define AUDIO_LEAK_H_

#include <zephyr/kernel.h>
#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief เริ่มต้นโมดูลสร้างสัญญาณเสียงลมรั่ว
 * @return 0 เมื่อสำเร็จ, ค่าติดลบเมื่อเกิดข้อผิดพลาด
 */
int audio_leak_init(void);

/**
 * @brief สั่งเปิด/ปิด สัญญาณเสียงลมรั่วแบบ Manual Override
 * @param enable true = เปิดเสียง (I2S Waveform Active), false = ปิดเสียง (Silent)
 */
void audio_leak_set_enable(bool enable);

/**
 * @brief ซิงค์สถานะเสียงกับ GI FSM อัตโนมัติ (จะไม่มีผลหากติด Manual Override)
 */
void audio_leak_sync_fsm(bool fsm_active);

/**
 * @brief เคลียร์ค่า Manual Override เพื่อให้ FSM ควบคุมเสียงตามสภาวะคลินิก
 */
void audio_leak_clear_override(void);

/**
 * @brief ตรวจสอบสถานะการทำงานของสัญญาณเสียง
 */
bool audio_leak_is_active(void);

/**
 * @brief กำหนดความถี่ของเสียงจำลอง (ค่าเริ่มต้น 3000 Hz)
 */
void audio_leak_set_frequency(uint32_t freq_hz);

#ifdef __cplusplus
}
#endif

#endif /* AUDIO_LEAK_H_ */
