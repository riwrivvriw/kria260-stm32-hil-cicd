# Day 2: Closed-Loop PID Pressure Controller & Video Stream Engine

## 🎯 เป้าหมายประจำวัน (Daily Goals)
1. พัฒนาโมดูลควบคุม PWM ฝั่ง KR260 (`pwm_driver.py`) เพื่อสั่งการปั๊มลมไปยังพิน PMOD1 (`H12`)
2. พัฒนาระบบควบคุมความดันแบบวงปิด (Closed-Loop PID Controller) ดึง Feedback จาก I2C ของ STM32 และปรับ Duty Cycle อัตโนมัติ
3. ติดตั้งและคอนฟิกไดรเวอร์กล้องเสมือน `v4l2loopback` บน KR260 สำหรับรับภาพวิดีโอจำลอง
4. สร้างท่อส่งสตรีมวิดีโอ GStreamer จาก Laptop เข้าสู่อุปกรณ์ `/dev/video10` บน KR260

---

## ⏱️ กำหนดการทำงาน (Hourly Schedule)

| ช่วงเวลา | กิจกรรม | ผลลัพธ์ที่คาดหวัง |
|---|---|---|
| **09:00 - 10:30** | พัฒนาไดรเวอร์ขับ PWM บน KR260 (`pwm_driver.py`) | สามารถสั่ง Duty 0-100% ออกพิน H12 ได้ |
| **10:30 - 12:00** | เชื่อม Closed-Loop: STM32 วัด PWM $\rightarrow$ คำนวณความดัน | คำสั่ง `hil status` บน STM32 เห็นค่า Duty เปลี่ยนตามที่ KR260 สั่ง |
| **12:00 - 13:00** | *พักกลางวัน* | - |
| **13:00 - 15:00** | พัฒนาและจูนอัลกอริทึม PID Controller บน KR260 | ค่าความดันลู่เข้าหา Setpoint (เช่น 120 kPa) ภายใน 3 วินาที |
| **15:00 - 16:30** | โหลดและตั้งค่าโมดูล `v4l2loopback` บน KR260 | เกิด Device Node `/dev/video10` บนระบบ |
| **16:30 - 17:30** | เขียนสคริปต์สตรีมวิดีโอ GStreamer จาก Host Laptop | KR260 รับ Frame ภาพวิดีโอกระเพาะอาหารได้ราบรื่น |
| **17:30 - 18:00** | สรุปผลการทดสอบ Day 2 & อัปเดต Task Tracker | โค้ด Closed-loop & Video Pipeline พร้อมใช้งาน |

---

## 🛠️ รายละเอียดงานและโค้ดที่ต้องพัฒนา (Implementation Steps)

### Step 2.1: ไดรเวอร์ควบคุม PWM บน KR260 (`software/drivers/pwm_driver.py`)

ใช้ Memory-mapped I/O (MMAP) ผ่าน `/dev/mem` หรือ AXI UIO เพื่อควบคุม Register ของโมดูล `axi_pwm_controller.sv` (Offset `0x00`: Control, `0x04`: Prescaler, `0x08`: Duty):

```python
"""
software/drivers/pwm_driver.py
ควบคุมโมดูล AXI4-Lite PWM Controller บน KR260 FPGA
"""

import os
import mmap
import struct

class KR260PWMDriver:
    # กำหนด Base Address ตามที่ระบุใน Vivado Address Editor (เช่น 0xA0000000)
    AXI_PWM_BASE = 0xA0000000
    MAP_SIZE = 4096

    REG_CTRL = 0x00
    REG_PRESCALER = 0x04
    REG_DUTY = 0x08
    REG_STATUS = 0x0C

    def __init__(self, base_addr: int = AXI_PWM_BASE):
        self.base_addr = base_addr
        self.fd = None
        self.mem = None

    def open(self):
        self.fd = os.open("/dev/mem", os.O_RDWR | os.O_SYNC)
        self.mem = mmap.mmap(
            self.fd, self.MAP_SIZE,
            mmap.MAP_SHARED,
            mmap.PROT_READ | mmap.PROT_WRITE,
            offset=self.base_addr
        )

    def write_reg(self, offset: int, value: int):
        self.mem.seek(offset)
        self.mem.write(struct.pack("<I", value))

    def read_reg(self, offset: int) -> int:
        self.mem.seek(offset)
        return struct.unpack("<I", self.mem.read(4))[0]

    def set_duty_cycle(self, duty_percent: float):
        """กำหนด Duty Cycle 0.0% - 100.0% (แปลงเป็น 10-bit: 0 - 1023)"""
        duty_percent = max(0.0, min(100.0, duty_percent))
        raw_duty = int((duty_percent / 100.0) * 1023)
        self.write_reg(self.REG_DUTY, raw_duty)
        # สั่งเปิดการทำงาน (Enable = 1)
        self.write_reg(self.REG_CTRL, 0x01)

    def emergency_stop(self):
        """สั่งตัดการทำงานปั๊มทันทีผ่าน Hardware/Software Estop"""
        self.write_reg(self.REG_CTRL, 0x02) # Bit 1 = Emergency Stop
        self.write_reg(self.REG_DUTY, 0)

    def close(self):
        if self.mem:
            self.mem.close()
        if self.fd:
            os.close(self.fd)
```

---

### Step 2.2: อัลกอริทึม Closed-Loop PID Pressure Controller (`software/control/pid_controller.py`)

สมการควบคุม:
$$u(t) = K_p e(t) + K_i \int_0^t e(\tau) d\tau + K_d \frac{de(t)}{dt}$$

```python
"""
software/control/pid_controller.py
ระบบควบคุมความดันแบบวงปิด (PID Closed-Loop Pressure Controller)
"""

import time

class PIDController:
    def __init__(self, kp: float = 1.2, ki: float = 0.3, kd: float = 0.05,
                 out_min: float = 0.0, out_max: float = 100.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.out_min = out_min
        self.out_max = out_max

        self.integral = 0.0
        self.prev_error = 0.0
        self.prev_time = None

    def reset(self):
        self.integral = 0.0
        self.prev_error = 0.0
        self.prev_time = None

    def compute(self, setpoint: float, current_val: float) -> float:
        now = time.time()
        if self.prev_time is None:
            dt = 0.05
        else:
            dt = max(now - self.prev_time, 0.001)

        error = setpoint - current_val
        self.integral += error * dt

        # Anti-windup clamping
        self.integral = max(self.out_min, min(self.out_max, self.integral))

        derivative = (error - self.prev_error) / dt

        output = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)
        output = max(self.out_min, min(self.out_max, output))

        self.prev_error = error
        self.prev_time = now
        return output
```

สคริปต์รัน Loop การควบคุม (`software/control/closed_loop_runner.py`):
```python
"""
software/control/closed_loop_runner.py
รัน Control Loop อ่าน I2C จาก STM32 และคำนวณ PID สั่ง PWM ปั๊มลม
"""

import time
from software.drivers.pressure_sensor import STM32PressureSensor
from software.drivers.pwm_driver import KR260PWMDriver
from software.control.pid_controller import PIDController

def run_pressure_control(target_kpa: float = 120.0, duration_sec: float = 10.0):
    sensor = STM32PressureSensor(bus_id=1)
    pwm = KR260PWMDriver()
    pid = PIDController(kp=1.5, ki=0.4, kd=0.08)

    sensor.connect()
    pwm.open()
    print(f"[*] Starting Closed-Loop Control to Target: {target_kpa:.2f} kPa")

    start_time = time.time()
    try:
        while time.time() - start_time < duration_sec:
            telemetry = sensor.read_telemetry()
            current_p = telemetry["pressure_kpa"]

            duty = pid.compute(target_kpa, current_p)
            pwm.set_duty_cycle(duty)

            print(f"[Loop] Target: {target_kpa:.1f} | Measured: {current_p:.2f} kPa | Duty: {duty:.1f}%")
            time.sleep(0.05)
    finally:
        pwm.set_duty_cycle(0.0)
        pwm.close()
        sensor.close()
        print("[*] Control loop stopped safely.")

if __name__ == "__main__":
    run_pressure_control(120.0, 10.0)
```

---

### Step 2.3: การตั้งค่า Virtual Camera และ GStreamer Injection Engine

1. **โหลดโมดูล Kernel บน KR260:**
   ```bash
   sudo modprobe v4l2loopback devices=1 video_nr=10 card_label="GI_Virtual_Cam" exclusive_caps=1
   ```
2. **ทดสอบสตรีมวิดีโอจาก Host Laptop ไปยัง KR260 (ผ่าน Network UDP/RTP):**
   * บน KR260 (Receiver):
     ```bash
     gst-launch-1.0 -v udpsrc port=5000 caps="application/x-rtp, media=video, encoding-name=H264" ! \
     rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! video/x-raw,format=YUY2 ! \
     v4l2sink device=/dev/video10
     ```
   * บน Host Laptop (Sender) - ใช้สคริปต์ [tools/video_stream_mock.py](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/tools/video_stream_mock.py):
     ```bash
     # สตรีมภาพจำลองส่องกล้อง GI Endoscopy พร้อม On-Screen Display (OSD) ซิงค์กับ STM32 Sensor Data
     python tools/video_stream_mock.py --target-ip 192.168.1.120 --port 5000 --fps 30 --state STABLE_INSPECTION --pressure 120.0
     ```
     *(หรือใช้ GStreamer CLI พื้นฐาน: `gst-launch-1.0 videotestsrc pattern=ball ! video/x-raw,width=640,height=480,framerate=30/1 ! x264enc tune=zerolatency bitrate=1000 speed-preset=ultrafast ! rtph264pay ! udpsink host=192.168.1.120 port=5000`)*

---

## ✅ เช็กลิสต์การตรวจรับงาน Day 2 (Day 2 Verification Checklist)
* [ ] KR260 ขับ PWM ออกพิน PMOD1 ได้ และ STM32 สามารถตรวจจับ Duty Cycle ได้อย่างแม่นยำ
* [ ] Closed-loop Runner สามารถคุมค่าความดันให้เสถียรที่ Setpoint ที่กำหนด ($\pm 2\text{ kPa}$)
* [ ] อุปกรณ์ `/dev/video10` ถูกสร้างและพร้อมรับภาพ
* [ ] สามารถสตรีมวิดีโอจาก Laptop เข้า KR260 ได้โดยไม่มีข้อผิดพลาด
