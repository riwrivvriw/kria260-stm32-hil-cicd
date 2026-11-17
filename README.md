# STM32H5 HIL Simulator (Zephyr RTOS)

โปรเจกต์จำลองสภาพแวดล้อม (Hardware-in-the-Loop Plant Simulator) บนบอร์ด **STM32H563ZI (Nucleo-H563ZI)** 
ทำหน้าที่เป็นทั้ง **I2C Target (Slave)** และ **I2C Controller (Master Loopback)** พร้อมรับคำสั่งจาก Pytest บน Laptop ผ่านทางพอร์ต USB-C (Zephyr Shell)

---

## 1. การเชื่อมต่อสัญญาณสำหรับการทดสอบ (Pinout Guide)

| โมดูล | ฟังก์ชัน | บัสบนบอร์ด | พิน Nucleo-144 | หมายเหตุ |
|---|---|---|---|---|
| **I2C Target** | Sensor Slave (Addr `0x58`) | **I2C1** | `PB8` (SCL), `PB9` (SDA) | ต่อไปรอให้ KR260 หรือ I2C2 มาอ่าน |
| **I2C Controller** | Loopback Master | **I2C2** | `PF1` / `PB10` (SCL), `PF0` / `PB11` (SDA) | ใช้สำหรับ Self-test |
| **Host Interface** | Zephyr Shell (Pytest) | **ST-Link VCP / USB** | พอร์ต USB-C ของ ST-Link | 115200 8N1 |

> [!TIP]
> **การทำ Self-test Loopback บนบอร์ดตัวเอง:**
> นำสาย Jumper ต่อขา SCL ของ I2C1 เข้ากับ SCL ของ I2C2 และต่อ SDA ของ I2C1 เข้ากับ SDA ของ I2C2 
> *(อย่าลืม Pull-up Resistor 4.7kΩ เข้า 3.3V หากพินไม่ได้เปิด Internal Pull-up)*

---

## 2. วิธีการ Build และ Flash ด้วย Zephyr RTOS

### ขั้นตอนที่ 1: ตั้งค่า Zephyr Environment ชี้ไปที่ `~/stm32/zephyr`
เปิด Terminal บน Mac แล้วรันคำสั่ง:

```bash
# 1. Activate Python Virtual Environment ของ Zephyr (ถ้ามี)
source ~/stm32/zephyr/.venv/bin/activate  # หรือ path venv ที่คุณสร้างไว้

# 2. ตั้งค่า ZEPHYR_BASE ชี้ไปยังโฟลเดอร์ Zephyr ของคุณ
export ZEPHYR_BASE=~/stm32/zephyr
```

### ขั้นตอนที่ 2: Build Firmware
เข้ามาที่โฟลเดอร์โปรเจกต์นี้ (`~/hil`) แล้วรัน:

```bash
cd ~/hil
west build -b nucleo_h563zi -p auto
```

### ขั้นตอนที่ 3: Flash ลงบอร์ด STM32H563ZI
เสียบสาย USB-C ของบอร์ด Nucleo เข้ากับ Laptop แล้วรัน:

```bash
west flash
```

---

## 3. การทดสอบการทำงานผ่าน Zephyr Shell

เปิด Serial Terminal (เช่น `minicom`, `screen` หรือ VS Code Serial Monitor) ที่ Baudrate **115200**:

```bash
screen /dev/tty.usbmodem* 115200
```

กด Enter จะพบ Shell Prompt `hil:~$`:

```bash
# 1. ดูสถานะความดันและชิป
hil:~$ hil status
{"chip_id": "0x58", "pressure_kpa": 101.40, "leak": false, "auto": true}

# 2. สั่งบังคับค่าความดันคงที่
hil:~$ hil set_pressure 120.5
OK: Pressure set to 120.50 kPa (Auto-sim disabled)

# 3. สั่งจำลองการรั่ว (Leakage Injection)
hil:~$ hil inject_leak 1
OK: Leak state updated to 1

# 4. ทดสอบ I2C Loopback บนบอร์ดตัวเอง
hil:~$ hil loopback
Starting I2C Loopback Self-Test...
{"loopback": "PASS", "read_chip_id": "0x58", "read_pressure": 120.50}
```

---

## 4. การรันการทดสอบอัตโนมัติด้วย Pytest

แนะนำให้สร้าง Python Virtual Environment แยกสำหรับ HIL Test Automation:

```bash
# 1. สร้างและเข้าใช้งาน Virtual Environment
cd ~/hil
python3 -m venv .venv
source .venv/bin/activate

# 2. ติดตั้ง Dependencies สำหรับการทดสอบ
pip install -r requirements.txt

# 3. รันการทดสอบและสร้างรายงาน JUnit XML สำหรับ Azure DevOps
pytest tests/ -v --junitxml=reports/test_results.xml
```
