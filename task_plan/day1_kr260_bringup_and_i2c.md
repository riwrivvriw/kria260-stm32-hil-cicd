# Day 1: KR260 Bringup, Hardware Wiring & I2C Handshake

## 🎯 เป้าหมายประจำวัน (Daily Goals)
1. บูตระบบปฏิบัติการ PetaLinux บนบอร์ด Kria KR260 สำเร็จ และเชื่อมต่อผ่าน SSH จาก Laptop ได้
2. ต่อสายสัญญาณ 4 เส้น (SCL, SDA, PWM, GND) ระหว่างบอร์ด STM32H563ZI และ KR260
3. ตรวจสอบพบ I2C Slave Address `0x58` บนบอร์ด KR260 และอ่านค่า Register พื้นฐานได้
4. เขียนโมดูล Python Driver (`pressure_sensor.py`) บน KR260 เพื่ออ่านค่าความดันแบบ Real-time

---

## ⏱️ กำหนดการทำงาน (Hourly Schedule)

| ช่วงเวลา | กิจกรรม | ผลลัพธ์ที่คาดหวัง |
|---|---|---|
| **09:00 - 10:30** | เตรียม Image & บูต PetaLinux บน KR260 | บอร์ดบูตติดขึ้นหน้า Login UART |
| **10:30 - 12:00** | ตั้งค่า Network, Static IP & SSH Server | Laptop สามารถ `ssh petalinux@<KR260_IP>` ได้ |
| **12:00 - 13:00** | *พักกลางวัน* | - |
| **13:00 - 14:30** | ต่อสายฮาร์ดแวร์ 4 เส้น & วัดระดับแรงดัน 3.3V | เชื่อมต่อตาม Wiring Map ถูกต้อง |
| **14:30 - 16:00** | ทดสอบบัส I2C ด้วย `i2c-tools` บน Linux | พบอุปกรณ์ที่ Address `0x58` |
| **16:00 - 17:30** | เขียนโค้ด `pressure_sensor.py` บน KR260 | สคริปต์ Python อ่านค่าความดันแปลงหน่วย kPa ได้สำเร็จ |
| **17:30 - 18:00** | สรุปผลการทดสอบ Day 1 & อัปเดต Task Tracker | เอกสารและบันทึกผลพร้อมสำหรับ Day 2 |

---

## 🛠️ รายละเอียดงานและโค้ดที่ต้องพัฒนา (Implementation Steps)

### Step 1.1: บูต KR260 และตั้งค่า Network & SSH
1. เสียบการ์ด MicroSD (PetaLinux 2022.2 หรือ Kria Ubuntu) เข้ากับ KR260
2. เสียบสาย LAN เข้ากับ Laptop หรือ Router (วงเดียวกัน)
3. ตรวจสอบ IP ผ่าน Serial Port หรือใช้คำสั่ง:
   ```bash
   # บน KR260: ตั้งค่า Static IP หากไม่มีเราเตอร์แจก DHCP
   sudo ifconfig eth0 192.168.1.120 netmask 255.255.255.0 up
   ```
4. ทดสอบ SSH จากเครื่อง Host Laptop:
   ```bash
   ssh petalinux@192.168.1.120
   ```

---

### Step 1.2: การต่อสายฮาร์ดแวร์ (Hardware Wiring)

> [!CAUTION]
> **สำคัญมาก:** ระดับแรงดันของ STM32 และ KR260 ทำงานที่ **3.3V LVCMOS** ทั้งคู่ ห้ามนำไปต่อกับบอร์ด 5V เด็ดขาด และต้องต่อสาย **GND ร่วมกันเสมอ**

| ฟังก์ชัน | พินบน STM32H563ZI | พินบน Kria KR260 | รายละเอียด |
|---|---|---|---|
| **I2C SCL** | Arduino **D15** (`PB8`) | Raspberry Pi Header **Pin 5** (`AC14` / `I2C1_SCL`) | บัสสัญญาณนาฬิกา I2C 100 kHz |
| **I2C SDA** | Arduino **D14** (`PB9`) | Raspberry Pi Header **Pin 3** (`AD14` / `I2C1_SDA`) | ข้อมูล I2C Data |
| **Airpump PWM** | Arduino **D2** (`PF15`) | PMOD 1 **Pin 1** (`H12` / `pwm_out`) | สัญญาณ PWM ขับปั๊มลม (10-bit) |
| **Start/Stop IO** | Arduino **D3** (`PB13`) | PMOD 1 **Pin 3** (`H11` / `start_stop`) | สัญญาณเริ่ม/หยุดกระบวนการจาก KR260 |
| **Solenoid Valve**| Arduino **D4** (`PE11`) | PMOD 1 **Pin 2** (`E10` / `solenoid`) | สัญญาณสั่งเปิด/ปิดวาล์วระบายลม |
| **E-Stop Cutoff** | Arduino **D5** (`PE9`) | PMOD 1 **Pin 4** (`J10` / `estop`) | สัญญาณตัดการทำงานฉุกเฉินระดับฮาร์ดแวร์ |
| **Leak Audio AC** | Arduino **A2** (`PA4`) | PMOD 2 **Pin 1** / Audio In | สัญญาณเสียงลมรั่ว AC 3 kHz Sine wave จาก DAC1 |
| **Ethernet** | - | RJ45 Ethernet Port (`eth0`) | ต่อสาย LAN เข้า Host สำหรับ Video Stream & SSH |
| **Common GND** | Arduino **GND** | PMOD Pin 5/11 หรือ RPi **Pin 6** (`GND`) | กราวด์อ้างอิงของวงจรทั้งสองบอร์ด |

---

### Step 1.3: ตรวจสอบการสื่อสาร I2C บน Linux (KR260)

รันคำสั่งบน KR260 เพื่อตรวจเช็กบัส I2C (โดยทั่วไป Raspberry Pi Header แมปเข้ากับ `/dev/i2c-1`):

```bash
# 1. สแกนหาอุปกรณ์บนบัส I2C 1
sudo i2cdetect -y -r 1
```
*ผลลัพธ์ที่ถูกต้อง:* ตารางจะแสดงตัวเลข `58` ปรากฏขึ้นในพิกัดแถว 50 หลัก 8

```bash
# 2. อ่าน Register 0x00 (Chip ID) จาก STM32
sudo i2cget -y 1 0x58 0x00
# ผลลัพธ์ต้องได้: 0x58

# 3. อ่าน Register 0x02 และ 0x03 (Pressure MSB, LSB)
sudo i2cget -y 1 0x58 0x02
sudo i2cget -y 1 0x58 0x03
```

---

### Step 1.4: โค้ด Python สำหรับอ่านค่าเซนเซอร์บน KR260

สร้างไฟล์ `software/drivers/pressure_sensor.py`:

```python
"""
software/drivers/pressure_sensor.py
ไดรเวอร์อ่านค่าเซนเซอร์ความดันจำลองบนบอร์ด STM32 ผ่านบัส I2C1 บน Kria KR260
"""

import time
from smbus2 import SMBus

class STM32PressureSensor:
    I2C_ADDR = 0x58
    REG_CHIP_ID = 0x00
    REG_STATUS = 0x01
    REG_PRESSURE_MSB = 0x02
    REG_PRESSURE_LSB = 0x03
    REG_GI_STATE = 0x04
    REG_PUMP_DUTY = 0x05
    REG_TARGET_PRESSURE = 0x06
    REG_IO_STATUS = 0x07

    STATE_NAMES = {
        0x00: "IDLE",
        0x01: "INSUFFLATION",
        0x02: "STABLE_INSPECTION",
        0x03: "LEAK_EVENT",
        0x04: "DEFLATION_STOP",
        0x05: "EMERGENCY_STOP"
    }

    def __init__(self, bus_id: int = 1):
        self.bus_id = bus_id
        self.bus = None

    def connect(self):
        self.bus = SMBus(self.bus_id)

    def read_chip_id(self) -> int:
        if not self.bus:
            raise RuntimeError("Bus not connected")
        return self.bus.read_byte_data(self.I2C_ADDR, self.REG_CHIP_ID)

    def read_telemetry(self) -> dict:
        """อ่านข้อมูลครบ 8 ไบต์: Chip ID, Status, Pressure MSB/LSB, State, Duty, Target, IO"""
        if not self.bus:
            raise RuntimeError("Bus not connected")

        # อ่านข้อมูลรวดเดียว 8 ไบต์
        data = self.bus.read_i2c_block_data(self.I2C_ADDR, self.REG_CHIP_ID, 8)
        chip_id = data[0]
        status = data[1]
        raw_pressure = (data[2] << 8) | data[3]
        pressure_kpa = raw_pressure / 100.0
        gi_state = data[4]
        pump_duty = data[5]
        target_kpa = float(data[6])
        io_status = data[7]

        return {
            "chip_id": hex(chip_id),
            "leak_active": bool(status & 0x01),
            "valve_open": bool(status & 0x02),
            "overpressure": bool(status & 0x04),
            "estop_active": bool(status & 0x08),
            "pressure_kpa": pressure_kpa,
            "gi_state": self.STATE_NAMES.get(gi_state, f"UNKNOWN({gi_state})"),
            "pump_duty_pct": pump_duty,
            "target_pressure_kpa": target_kpa,
            "io": {
                "start_stop": bool(io_status & 0x01),
                "solenoid": bool(io_status & 0x02),
                "estop": bool(io_status & 0x04),
            },
            "timestamp": time.time()
        }

    def close(self):
        if self.bus:
            self.bus.close()

if __name__ == "__main__":
    sensor = STM32PressureSensor(bus_id=1)
    sensor.connect()
    print("Reading 8-byte telemetry from STM32 (Ctrl+C to stop)...")
    try:
        while True:
            t = sensor.read_telemetry()
            print(f"[State: {t['gi_state']:<18}] Press: {t['pressure_kpa']:5.2f}/{t['target_pressure_kpa']:.0f} kPa | "
                  f"Duty: {t['pump_duty_pct']:3d}% | Leak: {t['leak_active']} | Solenoid: {t['valve_open']} | E-Stop: {t['estop_active']}")
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        sensor.close()
```

---

## ✅ เช็กลิสต์การตรวจรับงาน Day 1 (Day 1 Verification Checklist)
* [ ] SSH เข้า KR260 จาก Host Laptop ได้อย่างเสถียร
* [ ] คำสั่ง `i2cdetect -y -r 1` พบ Address `0x58`
* [ ] สคริปต์ `pressure_sensor.py` รันแล้วแสดงผลตัวเลขความดันใกล้เคียงกับที่ STM32 Shell พิมพ์ออกมา
* [ ] Commit โค้ด `software/drivers/pressure_sensor.py` ขึ้น Git
