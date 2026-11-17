# Day 3: End-to-End Pytest Automation, CSV Reporting & CI/CD Pipeline

## 🎯 เป้าหมายประจำวัน (Daily Goals)
1. พัฒนาระบบ Pytest HIL Controller บน Host Laptop ให้สั่งงานและทดสอบได้ทั้ง STM32 (ผ่าน Serial) และ KR260 (ผ่าน SSH)
2. เขียนชุดทดสอบ End-to-End (`tests/test_hil_closed_loop.py`):
   * ทดสอบ Closed-Loop Pressure Regulation
   * ทดสอบ Emergency Stop Response Time (Medical Safety Fail-Safe)
   * ทดสอบการรับ Frame วิดีโอจำลองเข้าสู่ระบบตรวจจับ (GI Detect)
3. รันชุดทดสอบทั้งหมดและยืนยันการสร้างรายงานผล **CSV Format** (`reports/test_results.csv`) ที่มีข้อมูล Telemetry ครบถ้วน
4. ตรวจสอบการรันอัตโนมัติบน Azure DevOps Pipeline
5. (ส่วนต่อขยาย Phase 3.1) เริ่มต้นพัฒนา DAC1 บน STM32 สำหรับจำลองเสียงลมรั่ว 3 kHz

---

## ⏱️ กำหนดการทำงาน (Hourly Schedule)

| ช่วงเวลา | กิจกรรม | ผลลัพธ์ที่คาดหวัง |
|---|---|---|
| **09:00 - 10:30** | พัฒนา SSH Remote Fixture (`kr260_client`) ใน Pytest | Laptop สามารถส่งคำสั่งรันสคริปต์บน KR260 ได้อัตโนมัติ |
| **10:30 - 12:00** | พัฒนาชุดทดสอบ `test_hil_closed_loop.py` | ได้ Test Cases ครอบคลุม Closed-Loop, E-Stop, และ Video |
| **12:00 - 13:00** | *พักกลางวัน* | - |
| **13:00 - 14:30** | รันและแก้ไขปัญหา E2E Tests บนฮาร์ดแวร์จริง | ทุก Test Case รันผ่าน (PASSED) |
| **14:30 - 15:30** | ตรวจสอบไฟล์ผลลัพธ์ CSV (`reports/test_results.csv`) | มีค่า Telemetry และ Duration ครบถ้วนทุกแถว |
| **15:30 - 16:30** | ทดสอบรันผ่าน Azure Pipelines / CI Runner | Pipeline รันสำเร็จ และบันทึก Artifact CSV ได้เรียบร้อย |
| **16:30 - 17:30** | พัฒนา DAC1 Sound Generator บน STM32 (Phase 3.1) | เปิดใช้งาน DAC ส่ง Sine wave ออกขา PA4 สำเร็จ |
| **17:30 - 18:00** | สรุปรายงานปิดโครงการ 3 วัน (Final Project Wrap-up) | เอกสารครบถ้วน โค้ดเสร็จสมบูรณ์ 100% พร้อมส่งมอบ |

---

## 🛠️ รายละเอียดงานและโค้ดที่ต้องพัฒนา (Implementation Steps)

### Step 3.1: พัฒนา SSH Remote Fixture บน Host Laptop (`tests/conftest.py`)

เพิ่ม Client สื่อสารทางไกลกับ KR260 ใน `tests/conftest.py`:

```python
import subprocess
import pytest

class KR260RemoteClient:
    def __init__(self, host: str = "192.168.1.120", user: str = "petalinux"):
        self.host = host
        self.user = user

    def run_cmd(self, cmd: str, timeout: float = 15.0) -> str:
        ssh_cmd = [
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=5",
            f"{self.user}@{self.host}",
            cmd
        ]
        res = subprocess.run(ssh_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
        if res.returncode != 0:
            raise RuntimeError(f"SSH Command failed ({res.returncode}): {res.stderr}")
        return res.stdout.strip()

@pytest.fixture(scope="module")
def kr260():
    client = KR260RemoteClient()
    yield client
```

---

### Step 3.2: พัฒนาชุดทดสอบ HIL End-to-End (`tests/test_hil_closed_loop.py`)

สร้างไฟล์ `tests/test_hil_closed_loop.py`:

```python
"""
tests/test_hil_closed_loop.py
ชุดทดสอบระบบปิดลูปอัตโนมัติ (Closed-Loop HIL Automated Tests)
ทดสอบร่วมกันระหว่าง Host, STM32 (Serial), และ KR260 (SSH)
"""

import pytest
import time

@pytest.mark.hardware
def test_01_verify_cross_board_i2c(hil, kr260, csv_record):
    """ทดสอบว่า KR260 สามารถอ่านค่าตรงกับที่ STM32 รายงาน"""
    stm32_data = hil.send_cmd_json("hil status")
    
    # สั่งให้ KR260 รันสคริปต์อ่านค่าจาก I2C Bus 1
    kr260_out = kr260.run_cmd("python3 -c 'from software.drivers.pressure_sensor import STM32PressureSensor; s = STM32PressureSensor(); s.connect(); print(s.read_telemetry())'")
    
    csv_record({
        "stm32_pressure": stm32_data["pressure_kpa"],
        "kr260_raw_output": kr260_out
    })
    
    assert stm32_data["chip_id"] == "0x58"
    assert "0x58" in kr260_out

@pytest.mark.hardware
def test_02_closed_loop_pressure_regulation(hil, kr260, csv_record):
    """ทดสอบสั่ง KR260 ให้คุมความดันไปที่ 120 kPa แล้วตรวจดูค่าบน STM32"""
    target_kpa = 120.0
    
    # สั่งรัน PID Runner บน KR260 เป็นเวลา 5 วินาที
    kr260.run_cmd(f"python3 -c 'from software.control.closed_loop_runner import run_pressure_control; run_pressure_control({target_kpa}, 5.0)'")
    
    # ตรวจสอบค่าสุดท้ายบน STM32
    stm32_data = hil.send_cmd_json("hil status")
    measured_kpa = stm32_data["pressure_kpa"]
    
    csv_record({
        "target_kpa": target_kpa,
        "final_measured_kpa": measured_kpa,
        "pump_duty": stm32_data.get("pump_duty", 0.0),
        "error_percent": abs(measured_kpa - target_kpa) / target_kpa * 100.0
    })
    
    # ความดันต้องลู่เข้าใกล้ Target ภายในช่วง $\pm 5\text{ kPa}$
    assert abs(measured_kpa - target_kpa) < 5.0, f"Regulation failed: {measured_kpa} kPa"

@pytest.mark.safety
def test_03_emergency_stop_fail_safe(hil, kr260, csv_record):
    """ทดสอบระบบตัดไฟฉุกเฉิน (Emergency Stop) ค่า Duty ต้องตกเหลือ 0 ทันที"""
    # สั่ง E-stop ผ่าน KR260
    kr260.run_cmd("python3 -c 'from software.drivers.pwm_driver import KR260PWMDriver; p = KR260PWMDriver(); p.open(); p.emergency_stop(); p.close()'")
    
    time.sleep(0.1)
    stm32_data = hil.send_cmd_json("hil status")
    duty = stm32_data.get("pump_duty", 0.0)
    
    csv_record({
        "safety_check": "Emergency Stop Triggered",
        "pump_duty_after_estop": duty
    })
    
    assert duty == 0.0, f"Safety violation! Pump duty still active: {duty}%"
```

---

### Step 3.3: การรันการทดสอบและผลลัพธ์รายงานผล CSV

รันคำสั่ง Pytest บน Host Laptop:

```bash
pytest tests/ -v --csv=reports/test_results.csv
```

ไฟล์ [reports/test_results.csv](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/reports/test_results.csv) จะถูกอัปเดตอัตโนมัติ:
```csv
timestamp,suite,test_name,status,duration_sec,message,telemetry_data
2026-11-19 14:32:10,test_hil_closed_loop,test_01_verify_cross_board_i2c,PASSED,0.8521,"","{""stm32_pressure"": 101.4, ""kr260_raw_output"": ""...""}"
2026-11-19 14:32:16,test_hil_closed_loop,test_02_closed_loop_pressure_regulation,PASSED,5.4310,"","{""target_kpa"": 120.0, ""final_measured_kpa"": 119.8, ""error_percent"": 0.16}"
2026-11-19 14:32:17,test_hil_closed_loop,test_03_emergency_stop_fail_safe,PASSED,0.2104,"","{""safety_check"": ""Emergency Stop Triggered"", ""pump_duty_after_estop"": 0.0}"
```

---

### Step 3.4: ส่วนขยาย Phase 3.1: STM32 DAC จำลองเสียงลมรั่ว (Leakage Sound Simulation)

1. อัปเดต `app.overlay` เพื่อเปิด DAC1 Channel 1 (พิน Arduino `A2` / `PA4`):
   ```dts
   &dac1 {
       status = "okay";
       pinctrl-0 = <&dac1_out1_pa4>;
       pinctrl-names = "default";
   };
   ```
2. พัฒนาฟังก์ชันสร้างคลื่นเสียง Sine wave 3 kHz ใน `src/main.c` เพื่อจำลองเสียงฟู่เมื่อตรวจพบลมรั่ว (`g_leak_injected = true`)

---

## ✅ เช็กลิสต์การส่งมอบงาน Day 3 (Final Delivery Checklist)
* [ ] ชุดทดสอบ End-to-End รันผ่านครบ 100% บนฮาร์ดแวร์จริง
* [ ] ไฟล์รายงานผล CSV ถูกสร้างอย่างสมบูรณ์ และมีข้อมูล Telemetry ครบถ้วน
* [ ] ตรวจสอบความถูกต้องของ Azure DevOps Pipeline (`azure-pipelines.yml`)
* [ ] Push การเปลี่ยนแปลงและโค้ดทั้งหมดขึ้น GitHub Main Branch
