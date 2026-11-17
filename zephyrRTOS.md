# คู่มือเจาะลึกการทำงานของเฟิร์มแวร์ Zephyr RTOS บน STM32H5 (zephyrRTOS.md)
## โครงการ: HIL Plant Simulator สำหรับ Kria KR260 (GI Detect System)

เอกสารฉบับนี้อธิบายโครงสร้างและการทำงานของเฟิร์มแวร์ [src/main.c](file:///Users/pongpipat/hil/src/main.c) บน **Zephyr RTOS (v4.x)** อย่างละเอียดแบบ **ทีละฟังก์ชัน (Function-by-Function Breakdown)** เพื่อให้เข้าใจกลไกภายในของระบบ Embedded RTOS อย่างถ่องแท้

---

## 1. สถาปัตยกรรมภาพรวมของเฟิร์มแวร์ (Firmware Architecture)

เฟิร์มแวร์ประกอบด้วย 3 องค์ประกอบหลักที่ทำงานร่วมกันแบบ Asynchronous:

1. **Main Thread (System Initialization):** กำหนดค่าฮาร์ดแวร์, ตั้งค่า Mutex, และลงทะเบียน I2C Target
2. **Plant Simulator Thread (RTOS Preemptive Thread):** เธรดเบื้องหลังคำนวณสมการฟิสิกส์ความดันแบบ Real-Time ทุกๆ 50ms (20 Hz)
3. **Zephyr Shell Subsystem (Interrupt/Event-Driven):** รับคำสั่งจาก Host PC ผ่าน USB-C UART ตอบกลับผลลัพธ์เป็น JSON

```
                        +------------------------------------+
                        |           Zephyr Kernel            |
                        +-----------------+------------------+
                                          |
         +--------------------------------+--------------------------------+
         | (Priority 7)                                                    | (Event Driven)
         v                                                                 v
+-------------------------------+      [k_mutex_lock]     +--------------------------------+
|  plant_sim_thread_entry()     | <=====================> |  Zephyr Shell Command Handlers |
|  - คำนวณความดัน Real-time     |    ป้องกัน Race Condition|  - hil status (JSON output)    |
|  - อัปเดตลง g_i2c_buffer      |   บน Memory Buffer 256B  |  - hil set_pressure <val>      |
|  - update_eeprom_memory()     |                         |  - hil inject_leak <0|1>       |
+---------------+---------------+                         +--------------------------------+
                |
                v (eeprom_target_write_data)
+------------------------------------------------------------------------------------------+
|                        I2C Target Hardware Driver (Address 0x58)                         |
|   - รอรับคำสั่ง Read/Write จาก KR260 Master ในระดับ Hardware Interrupt (Zero CPU Wait)   |
+------------------------------------------------------------------------------------------+
```

---

## 2. อธิบายตัวแปรและโครงสร้างข้อมูลส่วนกลาง (Global State)

```c
#define TARGET_I2C_ADDR       0x58
#define REG_CHIP_ID           0x00
#define REG_STATUS            0x01
#define REG_PRESSURE_MSB      0x02
#define REG_PRESSURE_LSB      0x03
#define BUFFER_SIZE           256

static uint8_t g_i2c_buffer[BUFFER_SIZE];
static struct k_mutex g_buffer_mutex;
static const struct device *g_target_dev;

static float g_current_pressure_kpa = 101.325f;
static bool  g_leak_injected = false;
static bool  g_auto_simulation = true;
```

* **`g_i2c_buffer`**: Memory Buffer ขนาด 256 ไบต์ ทำหน้าที่เป็น **Virtual Register Map** ของเซนเซอร์ เมื่อ Master (KR260) อ่าน I2C Address `0x58` ฮาร์ดแวร์จะดึงไบต์จาก Array นี้ส่งกลับไป
* **`g_buffer_mutex`**: ตัวล็อก (RTOS Mutex) สำหรับป้องกันปัญหา **Race Condition** เนื่องจากมีทั้ง Thread คำนวณฟิสิกส์ และ Thread ของ Shell ที่พยายามอ่าน/เขียน Buffer ก้อนเดียวกัน
* **`g_current_pressure_kpa`**: ตัวแปรเก็บค่าสถานะความดันปัจจุบัน (หน่วย: kPa)
* **`g_leak_injected`**: ธงบอกสถานะว่าขณะนี้เกิดสภาวะ "ลมรั่ว" หรือไม่ (0 = ปกติ, 1 = รั่ว)
* **`g_auto_simulation`**: ควบคุมว่าให้ Thread คำนวณฟิสิกส์อัตโนมัติ หรือให้ตรึงค่าคงที่ตามที่ Test Case สั่ง

---

## 3. เจาะลึกการทำงานทีละฟังก์ชัน (Function-by-Function Breakdown)

---

### ฟังก์ชันที่ 1: `main()` — จุดเริ่มต้นระบบและการผูกไดรเวอร์
```c
int main(void)
{
    LOG_INF("==================================================");
    LOG_INF(" STM32H5 HIL Plant Simulator Initializing...     ");
    ...
    k_mutex_init(&g_buffer_mutex);

    // กำหนดค่าเริ่มต้นให้กับ Buffer
    g_i2c_buffer[REG_CHIP_ID] = TARGET_I2C_ADDR;
    g_i2c_buffer[REG_STATUS]  = 0x00;

    // เชื่อมต่อ Buffer เข้ากับ I2C Target EEPROM Driver
    g_target_dev = DEVICE_DT_GET(DT_ALIAS(hil_target));
    if (!device_is_ready(g_target_dev)) {
        LOG_ERR("Target device (hil-target) is NOT ready!");
        return -ENODEV;
    }

    update_eeprom_memory();
    return 0;
}
```

* **หน้าที่:** เป็นฟังก์ชันแรกที่รันหลังจาก Zephyr Kernel บูตเสร็จสิ้น
* **กลไกการทำงาน:**
  1. เรียก `k_mutex_init(&g_buffer_mutex)` เพื่อเตรียม Mutex ให้พร้อมใช้งาน
  2. เขียนค่าเริ่มต้นลงใน Buffer เช่น กำหนดให้ Register `0x00` มีค่าเท่ากับ `0x58` (Chip ID)
  3. ดึง Device Pointer ของ I2C Target จาก DeviceTree (`DT_ALIAS(hil_target)`) ซึ่งแมปไว้กับ `&i2c1` ใน [app.overlay](file:///Users/pongpipat/hil/app.overlay)
  4. ตรวจสอบความพร้อมของฮาร์ดแวร์ด้วย `device_is_ready()` หากฮาร์ดแวร์พร้อม จะทำการซิงก์ค่าเริ่มต้นเข้าไดรเวอร์ทันที

---

### ฟังก์ชันที่ 2: `update_eeprom_memory()` — ซิงก์ข้อมูลลงไดรเวอร์ฮาร์ดแวร์
```c
static void update_eeprom_memory(void)
{
    if (g_target_dev && device_is_ready(g_target_dev)) {
        eeprom_target_write_data(g_target_dev, 0, g_i2c_buffer, 4);
    }
}
```

* **หน้าที่:** คัดลอกข้อมูล 4 ไบต์แรก (`Chip ID`, `Status`, `Pressure MSB`, `Pressure LSB`) จาก RAM ส่งมอบให้ไดรเวอร์ `zephyr,i2c-target-eeprom`
* **กลไกการทำงาน:**
  * ไดรเวอร์ EEPROM Target ของ Zephyr จะเก็บข้อมูลนี้ไว้ใน Internal RAM ของไดรเวอร์ เมื่อฝั่ง KR260 ส่ง Clock เข้ามาอ่านผ่านบัส I2C ไดรเวอร์จะตอบกลับทางฮาร์ดแวร์ Interrupt ทันทีโดยไม่รบกวนการทำงานของ CPU

---

### ฟังก์ชันที่ 3: `plant_sim_thread_entry()` — แบบจำลองฟิสิกส์ความดัน Real-Time
```c
static void plant_sim_thread_entry(void *p1, void *p2, void *p3)
{
    while (1) {
        if (g_auto_simulation) {
            k_mutex_lock(&g_buffer_mutex, K_FOREVER);

            if (g_leak_injected) {
                // หากมีการรั่ว ความดันจะลดลงอย่างรวดเร็ว
                g_current_pressure_kpa -= 0.8f;
                if (g_current_pressure_kpa < 70.0f) {
                    g_current_pressure_kpa = 70.0f;
                }
            } else {
                // สภาวะปกติ: จำลองคลื่นความดันกระเพื่อมเบาๆ
                static float step = 0.1f;
                g_current_pressure_kpa += step;
                if (g_current_pressure_kpa >= 105.0f || g_current_pressure_kpa <= 98.0f) {
                    step = -step;
                }
            }

            // แปลงค่าความดันเป็น Fixed-point 16-bit
            uint16_t raw_val = (uint16_t)(g_current_pressure_kpa * 100.0f);

            // อัปเดตข้อมูลลง Register Buffer
            g_i2c_buffer[REG_CHIP_ID]      = TARGET_I2C_ADDR;
            g_i2c_buffer[REG_STATUS]       = g_leak_injected ? 0x01 : 0x00;
            g_i2c_buffer[REG_PRESSURE_MSB] = (raw_val >> 8) & 0xFF;
            g_i2c_buffer[REG_PRESSURE_LSB] = raw_val & 0xFF;

            update_eeprom_memory();

            k_mutex_unlock(&g_buffer_mutex);
        }

        k_msleep(50); // วนลูปทุกๆ 50ms
    }
}
```

* **หน้าที่:** จำลองพฤติกรรมทางกายภาพของระบบความดันอากาศ (Pneumatic Dynamics)
* **กลไกการทำงาน:**
  1. ลูปทำงานซ้ำทุก 50 ms ด้วยคำสั่ง `k_msleep(50)` ซึ่งจะสลับให้ CPU ไปรันงานอื่นในระหว่างหน่วงเวลา (Non-blocking)
  2. ใช้ `k_mutex_lock()` ก่อนแก้ไขตัวแปรส่วนกลาง เพื่อไม่ให้ฟังก์ชัน Shell เข้ามาอ่านข้อมูลในจังหวะที่คำนวณค้างอยู่ครึ่งๆ กลางๆ
  3. **คำนวณสมการความดัน:**
     * **ถ้า `g_leak_injected == true`:** จำลองลมรั่ว ความดันลดลงทีละ $0.8 \text{ kPa}$ จนถึงขีดจำกัด $70 \text{ kPa}$
     * **ถ้าสภาวะปกติ:** จำลองความดันทางเดินอาหารกระเพื่อมเบาๆ ระหว่าง $98.0 - 105.0 \text{ kPa}$
  4. **Fixed-Point Scaling:** นำค่า Float มาคูณ 100 เพื่อเก็บทศนิยม 2 ตำแหน่ง แล้วแยกเป็น 2 ไบต์ (MSB/LSB) บันทึกลง Buffer จากนั้นปลดล็อกด้วย `k_mutex_unlock()`

---

### ฟังก์ชันที่ 4: `K_THREAD_DEFINE(...)` — มาโครสร้างและสั่งรัน RTOS Thread
```c
#define SIM_STACK_SIZE 1024
#define SIM_PRIORITY   7

K_THREAD_DEFINE(sim_thread_id, SIM_STACK_SIZE,
                plant_sim_thread_entry, NULL, NULL, NULL,
                SIM_PRIORITY, 0, 0);
```

* **หน้าที่:** เป็นมาโครพิเศษของ Zephyr RTOS สำหรับสร้างเธรดตอน Compile-Time
* **พารามิเตอร์:**
  * `sim_thread_id`: ชื่อตัวแปรระบุตัวตนของเธรด (Thread ID)
  * `SIM_STACK_SIZE (1024 bytes)`: ขนาดหน่วยความจำ Stack ที่จัดสรรให้เธรดนี้
  * `plant_sim_thread_entry`: ฟังก์ชันเริ่มต้นที่จะให้เธรดนี้ทำงาน
  * `SIM_PRIORITY (7)`: ลำดับความสำคัญในการแย่ง CPU (ตัวเลขยิ่งน้อย ยิ่งสำคัญสูง)
  * `0, 0`: เริ่มทำงานทันทีที่บูต (Start Delay = 0)

---

### ฟังก์ชันที่ 5: `run_i2c_loopback_test()` — ตรวจสอบระบบด้วย Master Loopback
```c
static int run_i2c_loopback_test(uint16_t *read_raw_pressure, uint8_t *read_chip_id)
{
    const struct device *i2c_master = DEVICE_DT_GET(DT_ALIAS(hil_master));

    if (!device_is_ready(i2c_master)) {
        LOG_ERR("I2C Master device (hil-master) is not ready!");
        return -ENODEV;
    }

    uint8_t reg_addr = REG_CHIP_ID;
    uint8_t rx_data[4] = {0};

    // ส่ง Register Address 0x00 แล้วอ่านข้อมูลกลับมา 4 bytes รวดเดียว
    int ret = i2c_write_read(i2c_master, TARGET_I2C_ADDR, 
                             &reg_addr, 1, 
                             rx_data, sizeof(rx_data));
    if (ret != 0) {
        LOG_ERR("I2C Loopback Transaction Failed (err: %d)", ret);
        return ret;
    }

    *read_chip_id = rx_data[0];
    *read_raw_pressure = (rx_data[2] << 8) | rx_data[3];
    return 0;
}
```

* **หน้าที่:** ใช้คอนโทรลเลอร์ `I2C2` (Master) ส่งคำสั่งไปอ่านค่าจาก `I2C1` (Slave) Address `0x58`
* **กลไกการทำงาน:**
  * ใช้คำสั่งมาตรฐาน `i2c_write_read()`:
    1. ส่ง START condition ตามด้วย Address `0x58` (Write) เพื่อบอกว่าจะอ่าน Register `0x00`
    2. ส่ง REPEATED START ตามด้วย Address `0x58` (Read) เพื่อดึงข้อมูลกลับมา 4 ไบต์
  * แยกข้อมูลไบต์ที่ได้กลับมาเป็น `chip_id` และค่า `raw_pressure`

---

### ฟังก์ชันที่ 6 ถึง 9: ชุดคำสั่ง Zephyr Shell Handlers (เชื่อมต่อ Pytest)

กลุ่มฟังก์ชันนี้จะทำงานเมื่อได้รับคำสั่งผ่าน Serial UART จากสคริปต์ Pytest บน Laptop:

#### 6. `cmd_hil_status()` — ตอบสถานะระบบเป็น JSON
```c
static int cmd_hil_status(const struct shell *sh, size_t argc, char **argv)
{
    k_mutex_lock(&g_buffer_mutex, K_FOREVER);
    shell_print(sh, "{\"chip_id\": \"0x%02X\", \"pressure_kpa\": %.2f, \"leak\": %s, \"auto\": %s}",
                g_i2c_buffer[REG_CHIP_ID],
                (double)g_current_pressure_kpa,
                g_leak_injected ? "true" : "false",
                g_auto_simulation ? "true" : "false");
    k_mutex_unlock(&g_buffer_mutex);
    return 0;
}
```
* **คำสั่ง:** `hil status`
* **การทำงาน:** ล็อก Mutex แล้วจัดรูปแบบข้อมูลออกทาง Serial Console ในรูปแบบ **JSON String บรรทัดเดียว** เพื่อให้ Python ฝั่ง Host นำไป `json.loads()` ได้ง่ายที่สุด

#### 7. `cmd_hil_set_pressure()` — บังคับค่าความดันคงที่
```c
static int cmd_hil_set_pressure(const struct shell *sh, size_t argc, char **argv)
{
    float new_pressure = strtof(argv[1], NULL);
    k_mutex_lock(&g_buffer_mutex, K_FOREVER);
    g_auto_simulation = false; // ปิดคำนวณอัตโนมัติ เพื่อตรึงค่าความดัน
    g_current_pressure_kpa = new_pressure;
    ...
    update_eeprom_memory();
    k_mutex_unlock(&g_buffer_mutex);
    return 0;
}
```
* **คำสั่ง:** `hil set_pressure <value>` (เช่น `hil set_pressure 125.50`)
* **การทำงาน:** แปลงสตริงตัวเลขเป็น Float ด้วย `strtof()` และตั้งค่า `g_auto_simulation = false` เพื่อตรึงค่าความดันไว้ตามที่ Test Case ต้องการทดสอบ

#### 8. `cmd_hil_inject_leak()` — จำลองสภาวะลมรั่ว
```c
static int cmd_hil_inject_leak(const struct shell *sh, size_t argc, char **argv)
{
    int leak_flag = atoi(argv[1]);
    k_mutex_lock(&g_buffer_mutex, K_FOREVER);
    g_leak_injected = (leak_flag != 0);
    g_auto_simulation = true;
    update_eeprom_memory();
    k_mutex_unlock(&g_buffer_mutex);
    return 0;
}
```
* **คำสั่ง:** `hil inject_leak 1` (เปิดรั่ว) หรือ `hil inject_leak 0` (ปิดรั่ว)
* **การทำงาน:** เปลี่ยนสถานะตัวแปร `g_leak_injected` ส่งผลให้ Thread ฟิสิกส์เริ่มลดระดับความดันลงอย่างรวดเร็ว

#### 9. `cmd_hil_loopback()` — สั่งรัน Self-Test
* **คำสั่ง:** `hil loopback`
* **การทำงาน:** เรียกฟังก์ชัน `run_i2c_loopback_test()` หากสำเร็จจะตอบกลับเป็น JSON `{"loopback": "PASS", ...}`

---

### ฟังก์ชันที่ 10: การลงทะเบียนคำสั่งเข้า Zephyr Shell Tree
```c
SHELL_STATIC_SUBCMD_SET_CREATE(sub_hil,
    SHELL_CMD(status, NULL, "Get current HIL plant status (JSON)", cmd_hil_status),
    SHELL_CMD(set_pressure, NULL, "Set fixed pressure value", cmd_hil_set_pressure),
    SHELL_CMD(inject_leak, NULL, "Inject/Clear air leakage state (0 or 1)", cmd_hil_inject_leak),
    SHELL_CMD(loopback, NULL, "Execute I2C Master-to-Slave loopback test", cmd_hil_loopback),
    SHELL_SUBCMD_SET_END
);

SHELL_CMD_REGISTER(hil, &sub_hil, "HIL Plant Controller Commands", NULL);
```

* **หน้าที่:** เป็นมาโครของ Zephyr ในการผูกฟังก์ชันภาษา C เข้ากับระบบ Terminal
* **ผลลัพธ์:** ทำให้เกิดคำสั่งหลักชื่อ `hil` ตามด้วยคำสั่งย่อย `status`, `set_pressure`, `inject_leak`, `loopback` พร้อมระบบ Help Text อัตโนมัติเมื่อพิมพ์คำสั่งผิด

---

## 4. สรุปจุดเด่นเชิงวิศวกรรมของโค้ดชุดนี้

1. **Deterministic Timing:** สมการฟิสิกส์รันใน RTOS Thread ที่มีคาบเวลาแม่นยำ (50ms $\pm$ jitter ต่ำ) ไม่โดนรบกวนจากการทำงานของ Shell
2. **Thread-Safe Architecture:** ใช้ `k_mutex` ปกป้อง Critical Section ทำให้ข้อมูลค่าความดันที่ส่งผ่าน I2C ไปยัง KR260 ไม่เกิดการฉีกขาดของข้อมูล (Data Corruption)
3. **Zero CPU Overhead for I2C:** ฮาร์ดแวร์ I2C Target ตอบสนองการอ่านจากภายนอกแบบ Autonomous ไม่ต้องรอให้ CPU ทำการโพลล์ (Polling)
4. **Machine-Readable API:** ออกแบบการสื่อสารผ่าน Shell ให้ตอบกลับเป็น JSON Format เพื่อรองรับ Automated Test และ CI/CD 100%
