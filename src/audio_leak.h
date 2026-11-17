/**
 * @file audio_leak.h
 * @brief โมดูลจำลองสัญญาณเสียงลมรั่ว (AC Audio Leak Simulator)
 *        สร้างสัญญาณ AC waveform (3 kHz Hiss / Sine Wave) ผ่าน DAC/GPIO PA4
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
 * @brief สั่งเปิด/ปิด สัญญาณเสียงลมรั่ว
 * @param enable true = เปิดเสียง (AC Waveform Active), false = ปิดเสียง (0V Silent)
 */
void audio_leak_set_enable(bool enable);

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
