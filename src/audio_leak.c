/**
 * @file audio_leak.c
 * @brief จำลองสัญญาณเสียงลมรั่ว (AC Waveform) ผ่าน DAC / High-speed Pin Toggle
 */

#include "audio_leak.h"
#include <zephyr/device.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/logging/log.h>

#if DT_NODE_HAS_STATUS(DT_NODELABEL(dac1), okay)
#include <zephyr/drivers/dac.h>
static const struct device *dac_dev = DEVICE_DT_GET(DT_NODELABEL(dac1));
#define DAC_CHANNEL_ID 1
#define DAC_RESOLUTION 12
#endif

LOG_MODULE_REGISTER(audio_leak, LOG_LEVEL_INF);

static bool g_audio_enabled = false;
static uint32_t g_freq_hz = 3000;

#define AUDIO_STACK_SIZE 1024
#define AUDIO_PRIORITY   5

/* ตาราง Sine Wave 16 จุด ความละเอียด 12-bit (0 - 4095) */
static const uint16_t SINE_LUT_16[16] = {
    2048, 2831, 3495, 3939, 4095, 3939, 3495, 2831,
    2048, 1264,  600,  156,    0,  156,  600, 1264
};

static void audio_thread_entry(void *p1, void *p2, void *p3)
{
    ARG_UNUSED(p1);
    ARG_UNUSED(p2);
    ARG_UNUSED(p3);

    LOG_INF("Audio Leak Generator Thread Active.");
    size_t idx = 0;

    while (1) {
        if (g_audio_enabled) {
#if DT_NODE_HAS_STATUS(DT_NODELABEL(dac1), okay)
            if (device_is_ready(dac_dev)) {
                dac_write_value(dac_dev, DAC_CHANNEL_ID, SINE_LUT_16[idx]);
            }
#endif
            idx = (idx + 1) & 0x0F;
            /* ปรับช่วงเวลาสอดคล้องกับความถี่ 3 kHz (คาบเวลา ~333 us / 16 จุด = ~20 us) */
            k_busy_wait(20);
        } else {
#if DT_NODE_HAS_STATUS(DT_NODELABEL(dac1), okay)
            if (device_is_ready(dac_dev)) {
                dac_write_value(dac_dev, DAC_CHANNEL_ID, 0);
            }
#endif
            k_msleep(20);
        }
    }
}

K_THREAD_DEFINE(audio_thread_id, AUDIO_STACK_SIZE,
                audio_thread_entry, NULL, NULL, NULL,
                AUDIO_PRIORITY, 0, 0);

int audio_leak_init(void)
{
    g_audio_enabled = false;

#if DT_NODE_HAS_STATUS(DT_NODELABEL(dac1), okay)
    if (device_is_ready(dac_dev)) {
        struct dac_channel_cfg dac_cfg = {
            .channel_id = DAC_CHANNEL_ID,
            .resolution = DAC_RESOLUTION
        };
        int ret = dac_channel_setup(dac_dev, &dac_cfg);
        if (ret != 0) {
            LOG_WRN("DAC channel setup failed: %d", ret);
        } else {
            LOG_INF("DAC1 Channel 1 setup for AC Leak Sound completed.");
        }
    }
#endif

    LOG_INF("Audio Leak AC Generator ready (Default %u Hz).", g_freq_hz);
    return 0;
}

void audio_leak_set_enable(bool enable)
{
    g_audio_enabled = enable;
    if (enable) {
        LOG_INF("Audio Leak AC Generator: ACTIVATED (%u Hz Hiss)", g_freq_hz);
    } else {
        LOG_INF("Audio Leak AC Generator: MUTED");
    }
}

bool audio_leak_is_active(void)
{
    return g_audio_enabled;
}

void audio_leak_set_frequency(uint32_t freq_hz)
{
    g_freq_hz = (freq_hz > 0) ? freq_hz : 3000;
}
