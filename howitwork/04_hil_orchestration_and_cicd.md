# คู่มือการทดสอบระบบ HIL และ CI/CD Pipeline (HIL Testbench & CI/CD Operations)

เอกสารฉบับนี้อธิบายสถาปัตยกรรมการทำงานของระบบทดสอบอัตโนมัติ **Pytest Hardware-in-the-Loop (HIL) Testbench** การส่งออกผลการทดสอบในรูปแบบ **CSV Format** และการเชื่อมต่อเข้ากับ **Azure DevOps CI/CD Pipeline**

---

## 1. หลักการทำงานภายใน (Internal Architecture)

ระบบทดสอบ HIL ทำหน้าที่เป็น **Master Test Orchestrator** ควบคุมและตรวจสอบการทำงานของเฟิร์มแวร์ STM32 และ KR260 แบบอัตโนมัติ โดยไม่ต้องอาศัยคนกดปุ่มหรือเสียบสายสลับไปมา

```
+-----------------------------------------------------------------------------------+
|                        AZURE DEVOPS CI/CD PIPELINE                                |
|                        (azure-pipelines.yml)                                      |
+-----------------------------------------+-----------------------------------------+
                                          | Trigger on Git Push / Scheduled Run
                                          v
+-----------------------------------------------------------------------------------+
|                          SELF-HOSTED TESTBENCH AGENT                              |
|                                                                                   |
|  [tests/test_hil_stm32.py]                                                        |
|  1. Auto-detect Serial Port:                                                      |
|     - สแกนหา ST-Link / STM32 Virtual COM Port อัตโนมัติ (ข้ามแพลตฟอร์ม)          |
|  2. Robust Serial Protocol Handler:                                               |
|     - ป้องกัน DTR/RTS Reset กระตุกบอร์ด                                           |
|     - กรองรหัสสี ANSI Escape Sequences (ANSI_REGEX) ออกจาก JSON อย่างหมดจด        |
|  3. Pytest Test Suites (6 Test Cases):                                            |
|     • test_01_read_hil_status: ตรวจสอบ JSON Schema และช่วงแรงดัน                  |
|     • test_02_set_manual_pressure: สั่งปรับค่าความดันจำลอง                        |
|     • test_03_state_machine_transitions: ทดสอบการเปลี่ยนสถานะ FSM ครบ 6 สถานะ    |
|     • test_04_leak_injection_and_audio: ทดสอบฉีดลมรั่วและคลื่นเสียง AC 3 kHz      |
|     • test_05_mock_control_ios: ทดสอบจำลองสัญญาณ Start/Stop, Solenoid, E-Stop     |
|     • test_06_i2c_loopback_self_test: ทดสอบบัส I2C ระหว่าง 2 บอร์ด                |
|                                                                                   |
|  [tests/conftest.py]                                                              |
|  4. Custom CSV Test Reporting Engine:                                             |
|     - รวบรวม Status (PASSED/FAILED/SKIPPED), Duration, และ Telemetry Metrics      |
|     - ส่งออกเป็นไฟล์ reports/test_results.csv                                     |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                         PIPELINE ARTIFACTS & DASHBOARD                            |
|  • Publish reports/test_results.csv เข้าสู่ Azure DevOps Artifacts                |
|  • วิเคราะห์ค่าสถิติ Telemetry ความดัน, Duty cycle, และอัตราการตอบสนอง             |
+-----------------------------------------------------------------------------------+
```

---

### 1.1 ระบบ Auto-detect Serial Port และ ANSI Filter

ใน [tests/test_hil_stm32.py](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/tests/test_hil_stm32.py):
1. **การค้นหาพอร์ต ST-Link อัตโนมัติ:**
   * ตรวจสอบ Environment Variable `HIL_PORT` หรือ `STM32_PORT` ก่อน
   * หากไม่มี จะสแกนผ่าน `serial.tools.list_ports.comports()` ตรวจหา Device Description ที่มีคีย์เวิร์ด `"stlink"`, `"st-link"`, `"stm"`, `"stmicroelectronics"`, หรือ `"nucleo"`
   * ป้องกันการจับคู่ผิดพลาดกับพอร์ตอื่นๆ เช่น Intel AMT หรือ Bluetooth COM Ports
2. **การกรองสีเทอร์มินัล (ANSI Strip):**
   * Zephyr Shell มักส่งรหัสสี ANSI เช่น `\x1b[1;32m` มาพร้อมข้อความ
   * ใช้ Regex `re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')` เพื่อตัดรหัสสีทิ้ง เหลือเฉพาะ JSON String บริสุทธิ์ ทำให้ `json.loads()` แปลงค่าได้อย่างแม่นยำ 100%

---

### 1.2 โครงสร้างรายงานผลการทดสอบ CSV (`reports/test_results.csv`)

รายงานผลถูกบันทึกเป็นไฟล์ CSV ตามมาตรฐานตารางข้อมูล:

```csv
timestamp,suite,test_name,status,duration_sec,message,telemetry_data
2026-11-17 17:24:58,test_hil_stm32,test_01_read_hil_status,PASSED,0.2450,OK,"{'chip_id': '0x58', 'state': 'INSPECT', 'pressure_kpa': 120.45, 'pump_duty': 45.2, 'leak': False}"
2026-11-17 17:24:58,test_hil_stm32,test_02_set_manual_pressure,PASSED,0.1820,OK,"{'target_pressure': 128.5, 'measured_pressure_kpa': 128.5}"
2026-11-17 17:24:58,test_hil_stm32,test_03_state_machine_transitions,PASSED,0.3120,OK,"{'tested_states': ['INSUFFLATE', 'LEAK', 'DEFLATE', 'ESTOP', 'IDLE']}"
2026-11-17 17:24:58,test_hil_stm32,test_04_leak_injection_and_audio,PASSED,0.1980,OK,"{'leak_active': True, 'audio_ac_active': True}"
2026-11-17 17:24:58,test_hil_stm32,test_05_mock_control_ios,PASSED,0.2100,OK,"{'io_start_stop': True, 'io_solenoid': True, 'io_estop': True}"
2026-11-17 17:24:58,test_hil_stm32,test_06_i2c_loopback_self_test,SKIPPED,0.0002,Skipped: รอต่อสาย I2C เข้ากับบอร์ด Kria KR260,
```

---

## 2. ขั้นตอนการรันการทดสอบ (How to Run HIL Tests)

### 2.1 การรันการทดสอบในเครื่อง Local (Host Laptop)

1. เสียบบอร์ด STM32 Nucleo เข้ากับพอร์ต USB
2. เปิด Terminal ในโฟลเดอร์โปรเจกต์ และรันคำสั่ง Pytest:

```bash
# รันชุดทดสอบทั้งหมด และส่งออกรายงานผล CSV
python -m pytest tests/test_hil_stm32.py -v --csv=reports/test_results.csv
```

#### การระบุพอร์ต Serial แบบเจาะจง (Optional):
หากมีหลายบอร์ดเชื่อมต่อพร้อมกัน สามารถกำหนดพอร์ตผ่าน Environment Variable ได้:
```bash
# บน Windows PowerShell:
$env:HIL_PORT="COM4"; python -m pytest tests/test_hil_stm32.py -v

# บน Linux / macOS:
HIL_PORT=/dev/ttyACM0 python3 -m pytest tests/test_hil_stm32.py -v
```

#### การรันเฉพาะหมวดหมู่ (Markers):
```bash
# รันเฉพาะ Smoke Tests
python -m pytest tests/test_hil_stm32.py -m smoke -v

# รันเฉพาะการทดสอบด้านความปลอดภัย (Safety & E-Stop)
python -m pytest tests/test_hil_stm32.py -m safety -v
```

---

### 2.2 การทำงานบน Azure DevOps CI/CD Pipeline (`azure-pipelines.yml`)

เมื่อมีการ `git push` ขึ้น Branch `main` หรือเปิด Pull Request:
1. **Agent Setup:** Azure Agent บน Host Laptop จะดึงโค้ดเวอร์ชันล่าสุด
2. **Pytest Execution:** Pipeline สั่งรันคำสั่ง:
   ```bash
   python -m pytest tests/test_hil_stm32.py --csv=$(Build.ArtifactStagingDirectory)/test_results.csv
   ```
3. **Artifact Publishing:** Pipeline จะอัปโหลดไฟล์ `test_results.csv` ขึ้นสู่ Pipeline Artifacts ให้ทีมวิศวกรดาวน์โหลดไปวิเคราะห์คุณภาพของระบบได้ทันที
