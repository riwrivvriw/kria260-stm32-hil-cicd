/**
 * @file audio_leak.c
 * @brief จำลองสัญญาณเสียงลมรั่วดิจิทัล (Digital I2S Audio Transmitter)
 *        จำลองสัญญาณ Digital MEMS Microphone ผ่าน I2S2 (DMA-driven PCM stream)
 */

#include "audio_leak.h"
#include <zephyr/device.h>
#include <zephyr/drivers/i2s.h>
#include <zephyr/logging/log.h>
#include <string.h>

LOG_MODULE_REGISTER(audio_leak, LOG_LEVEL_INF);

#if DT_NODE_HAS_STATUS(DT_NODELABEL(i2s2), okay)
static const struct device *const i2s_dev = DEVICE_DT_GET(DT_NODELABEL(i2s2));
#else
static const struct device *const i2s_dev = NULL;
#endif

static bool g_audio_enabled = false;
static bool g_manual_override = false;
static uint32_t g_freq_hz = 3000;
static bool g_i2s_ready = false;

#define AUDIO_STACK_SIZE 2048
#define AUDIO_PRIORITY   10

/*
 * การตั้งค่า Audio Buffer สำหรับ I2S DMA Ring:
 * - 16 kHz Sample Rate, 16-bit PCM, 2 Channels (Stereo frame)
 * - แต่ละ Block มี 256 samples ต่อ Channel = 512 int16_t = 1024 Bytes (16 ms ต่อ Block)
 * - 4 Blocks = 64 ms Ring buffer ป้องกัน DMA Underrun
 */
#define NUM_BLOCKS 4
#define SAMPLES_PER_BLOCK 256
#define BLOCK_SIZE (SAMPLES_PER_BLOCK * 2 * sizeof(int16_t))

#ifdef CONFIG_NOCACHE_MEMORY
#define MEM_SLAB_CACHE_ATTR __nocache
#else
#define MEM_SLAB_CACHE_ATTR
#endif

static char MEM_SLAB_CACHE_ATTR __aligned(4)
    _i2s_tx_slab_buffer[NUM_BLOCKS * BLOCK_SIZE];

static struct k_mem_slab i2s_tx_slab;

/*
 * ตาราง Sine Wave 16 จุด ความละเอียด 16-bit signed (-16000 ถึง +16000)
 * ที่ Fs = 16 kHz: 16 จุดจะบรรจุ 3 รอบคลื่นพอดี -> f = (3 / 16) * 16000 = 3000 Hz!
 */
static const int16_t SINE_LUT_3KHZ[16] = {
         0,  14782,  11314,  -6123, -16000,  -6123,  11314,  14782,
         0, -14782, -11314,   6123,  16000,   6123, -11314, -14782
};

static void audio_thread_entry(void *p1, void *p2, void *p3)
{
    ARG_UNUSED(p1);
    ARG_UNUSED(p2);
    ARG_UNUSED(p3);

    LOG_INF("I2S Digital Audio Leak Thread Started.");

    if (!g_i2s_ready || i2s_dev == NULL) {
        LOG_WRN("I2S device not ready. Digital Audio Leak stream halted.");
        return;
    }

    bool streaming = false;
    uint32_t lut_idx = 0;

    while (1) {
        void *tx_buf = NULL;

        /* จัดสรร Buffer จาก Memory Slab (ถ้า Buffer เต็ม DMA จะคืนบล็อกกลับมาเอง) */
        int ret = k_mem_slab_alloc(&i2s_tx_slab, &tx_buf, K_MSEC(100));
        if (ret != 0 || tx_buf == NULL) {
            k_msleep(5);
            continue;
        }

        int16_t *samples = (int16_t *)tx_buf;

        if (g_audio_enabled) {
            /* สร้างสัญญาณเสียง Hiss 3 kHz PCM Stereo Frame */
            for (size_t i = 0; i < SAMPLES_PER_BLOCK; i++) {
                int16_t val = SINE_LUT_3KHZ[lut_idx & 0x0F];
                lut_idx++;
                /* I2S Stereo format: Channel 0 (Left), Channel 1 (Right) */
                samples[2 * i]     = val;
                samples[2 * i + 1] = val;
            }
        } else {
            /* เมื่อ Muted: ส่ง Digital Silence (0) ให้ Bit Clock ยังวิ่งเสถียร */
            memset(tx_buf, 0, BLOCK_SIZE);
            lut_idx = 0;
        }

        /* ส่งข้อมูลเข้า I2S Driver (DMA Queue) */
        ret = i2s_write(i2s_dev, tx_buf, BLOCK_SIZE);
        if (ret < 0) {
            /* กรณีส่งไม่ผ่าน ต้องคืนบล็อกเข้า Slab เองเพื่อไม่ให้ Memory รั่ว */
            k_mem_slab_free(&i2s_tx_slab, tx_buf);
            k_msleep(10);
            continue;
        }

        /* เริ่ม Trigger ให้ I2S DMA ทำงานในครั้งแรก */
        if (!streaming) {
            ret = i2s_trigger(i2s_dev, I2S_DIR_TX, I2S_TRIGGER_START);
            if (ret == 0) {
                streaming = true;
                LOG_INF("I2S DMA Audio Stream Triggered Successfully.");
            }
        }
    }
}

K_THREAD_DEFINE(audio_thread_id, AUDIO_STACK_SIZE,
                audio_thread_entry, NULL, NULL, NULL,
                AUDIO_PRIORITY, 0, 0);

int audio_leak_init(void)
{
    g_audio_enabled = false;
    g_i2s_ready = false;

    k_mem_slab_init(&i2s_tx_slab, _i2s_tx_slab_buffer, BLOCK_SIZE, NUM_BLOCKS);

    if (i2s_dev == NULL || !device_is_ready(i2s_dev)) {
        LOG_ERR("I2S2 device not available or not ready!");
        return -ENODEV;
    }

    struct i2s_config i2s_cfg = {
        .word_size = 16U,
        .channels = 2U,
        .format = I2S_FMT_DATA_FORMAT_I2S,
        .options = I2S_OPT_FRAME_CLK_CONTROLLER | I2S_OPT_BIT_CLK_CONTROLLER,
        .frame_clk_freq = 16000, /* 16 kHz Sample Rate (Standard MEMS Mic) */
        .mem_slab = &i2s_tx_slab,
        .block_size = BLOCK_SIZE,
        .timeout = 1000,
    };

    int ret = i2s_configure(i2s_dev, I2S_DIR_TX, &i2s_cfg);
    if (ret != 0) {
        LOG_ERR("Failed to configure I2S2 transmitter: %d", ret);
        return ret;
    }

    g_i2s_ready = true;
    LOG_INF("I2S2 Digital Audio Leak Initialized: 16kHz 16-bit (BCLK=PB13, WS=PB12, SD=PB15)");
    return 0;
}

static void audio_leak_apply(bool enable)
{
    if (g_audio_enabled == enable) {
        return;
    }

    g_audio_enabled = enable;
    if (enable) {
        LOG_INF("I2S Audio Leak: ACTIVATED (%u Hz PCM Sine Wave)", g_freq_hz);
    } else {
        LOG_INF("I2S Audio Leak: MUTED (Transmitting digital silence)");
    }
}

void audio_leak_set_enable(bool enable)
{
    g_manual_override = true;
    audio_leak_apply(enable);
}

void audio_leak_sync_fsm(bool fsm_active)
{
    if (!g_manual_override) {
        audio_leak_apply(fsm_active);
    }
}

void audio_leak_clear_override(void)
{
    g_manual_override = false;
}

bool audio_leak_is_active(void)
{
    return g_audio_enabled;
}

void audio_leak_set_frequency(uint32_t freq_hz)
{
    g_freq_hz = (freq_hz > 0) ? freq_hz : 3000;
}
