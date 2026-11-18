# ตารางติดตามงาน (Task Tracking Table)

เอกสารติดตามสถานะงานพัฒนาและส่งมอบ (Task Tracking & Deliverables) สำหรับโครงการ Hardware-in-the-Loop (HIL) Testbench

---

## 📋 รายการงาน (Task List)

| Task ID | Linked Req ID | Task Name | Actionable Scope & Deliverable | Start | End | Status | Comment |
|:---:|:---:|---|---|:---:|:---:|:---:|---|
| **TASK-A05** | **HIL-002** | STM32H563ZI Plant Simulator Firmware | Develop STM32 firmware to read KR260 PWM/GPIO commands, parse UART test API commands, and simulate pressure (I2C), leak audio (AC), and Start/Stop IO. | 11/17/2026 | 11/20/2026 | Just started | Design state machine for mock camera inside gi and pumping gas |

---

## 🔍 รายละเอียดงาน: TASK-A05 (Deep Dive)

### 1. ข้อมูลทั่วไป (Task Metadata)
* **Task ID:** `TASK-A05`
* **Linked Requirement ID:** `HIL-002`
* **Task Name:** STM32H563ZI Plant Simulator Firmware
* **Timeline:** 11/17/2026 – 11/20/2026 (ระยะเวลา 3 วัน)
* **Status:** `Just started`

### 2. ขอบเขตงานและการส่งมอบ (Actionable Scope & Deliverables)
* **PWM & GPIO Commands (from KR260):**
  * พัฒนาโมดูลจับเวลาสัญญาณ PWM (`kr260_pwm_receiver.c`) ขับปั๊มลมจาก KR260 พิน `PF15` (Arduino D2)
  * อ่านและควบคุมสัญญาณดิจิทัล IO Handshake:
    * Start/Stop IO บนพิน `PB13` (Arduino D3)
    * Solenoid Purge Valve บนพิน `PE11` (Arduino D4)
    * Hardware E-Stop Cutoff บนพิน `PE9` (Arduino D5)
* **UART Testbench API (Zephyr Shell):**
  * พัฒนาคำสั่ง `hil status`, `hil set_state`, `hil set_pressure`, `hil inject_leak`, `hil set_start_stop`, `hil set_solenoid`, `hil set_estop`, `hil reset`
  * ส่งข้อมูลตอบกลับเป็น JSON Format แบบ Non-blocking ผ่านพอร์ต USB Serial (115200 8N1)
* **Sensor Simulation (Pressure & AC Leak Audio):**
  * จำลองเซนเซอร์วัดความดันผ่าน I2C Target Address `0x58` ด้วยโครงสร้างหน่วยความจำ 8 ไบต์ (0.01 kPa resolution)
  * จำลองเสียงลมรั่ว AC Audio Waveform 3 kHz Sine wave (16-point LUT 12-bit) ผ่าน DAC1 Channel 1 (`PA4` / Arduino A2)
* **State Machine Design (Comment Requirement):**
  * ออกแบบและพัฒนาระบบ Finite State Machine (6 สถานะ) จำลองกระบวนการอัดก๊าซ (Insufflation / Deflation) และพฤติกรรมกล้องเอนโดสโคป (GI Mock Camera View):
    1. `GI_STATE_IDLE` (`0x00`) - ก่อนเริ่มตรวจ โพรงแฟบ
    2. `GI_STATE_INSUFFLATION` (`0x01`) - ปั๊มลมขยายโพรงทางเดินอาหาร
    3. `GI_STATE_STABLE_INSPECTION` (`0x02`) - รักษาระดับแรงดันคงที่ โพรงนิ่งพร้อมตรวจ AI
    4. `GI_STATE_LEAK_EVENT` (`0x03`) - แรงดันตก ปล่อยเสียงลมรั่ว AC 3 kHz
    5. `GI_STATE_DEFLATION_STOP` (`0x04`) - เปิดโซลินอยด์วาล์วระบายก๊าซทิ้ง
    6. `GI_STATE_EMERGENCY_STOP` (`0x05`) - ตัดไฟและหยุดฉุกเฉินระดับฮาร์ดแวร์

---

## 📁 ไฟล์ที่เกี่ยวข้องในระบบ (Source Code Links)

* **State Machine:** [src/gi_state_machine.h](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/src/gi_state_machine.h), [src/gi_state_machine.c](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/src/gi_state_machine.c)
* **AC Leak Audio:** [src/audio_leak.h](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/src/audio_leak.h), [src/audio_leak.c](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/src/audio_leak.c)
* **GPIO IO Controller:** [src/io_controller.h](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/src/io_controller.h), [src/io_controller.c](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/src/io_controller.c)
* **Main Firmware:** [src/main.c](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/src/main.c)
* **Video Stream Mock:** [tools/video_stream_mock.py](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/tools/video_stream_mock.py)
* **HIL Pytest Testbench:** [tests/test_hil_stm32.py](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/tests/test_hil_stm32.py)
