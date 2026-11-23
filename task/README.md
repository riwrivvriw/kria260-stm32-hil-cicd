# ตารางติดตามงาน (Task Tracking Table)

เอกสารติดตามสถานะงานพัฒนาและส่งมอบ (Task Tracking & Deliverables) สำหรับโครงการ Hardware-in-the-Loop (HIL) Testbench with Azure CI/CD for Kria KR260 & STM32H563ZI

---

## 📋 รายการงานภาพรวม (Master Task List)

| Task ID | Linked Req ID | Task Name | Actionable Scope & Deliverable | Start | End | Status | Comment |
|:---:|:---:|---|---|:---:|:---:|:---:|---|
| **TASK-A05** | **HIL-002** | STM32H563ZI Plant Simulator Firmware | Develop STM32 firmware to read KR260 PWM/GPIO commands, parse UART test API commands, and simulate pressure (I2C), leak audio (AC), and Start/Stop IO. | 11/17/2026 | 11/20/2026 | **Finished (100%)** | Completed: PWM capture (`PF15`), I2C `0x58` target, AC leak audio (`PA4`), Solenoid Purge Valve (`PE11`), 6-state GI FSM, and Zephyr Shell Test API |
| **TASK-A06** | **HIL-003** | STM32 Multi-Domain State Machine & Architecture Diagrams | Design and generate high-resolution multi-domain state machine diagrams covering FPGA PL I/O, STM32 Mock Plant FSM Loop (4-step cyclic engine + 6-state GI physics), HIL Linux Domain (KR260 PS PID + V4L2 + Host Pytest CI), and Interface Loopbacks. | 11/18/2026 | 11/20/2026 | **Finished (100%)** | Completed: High-res PNG ([docs/images/stm32_plant_state_machine_interfaces.png](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/docs/images/stm32_plant_state_machine_interfaces.png)) and vector SVG ([docs/images/stm32_plant_state_machine_interfaces.svg](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/docs/images/stm32_plant_state_machine_interfaces.svg)) without line collision |
| **TASK-A07** | **HIL-004** | Interface Self-Test & Loopback Engine (`hil test_interfaces`) | Implement firmware CLI command `hil test_interfaces` to validate 5 core plant interfaces: I2C target `0x58`, Start/Stop (`PB13`), Solenoid Purge Valve (`PE11`), Hardware E-Stop (`PE9`), PWM Capture (`PF15`), and DAC Audio Leak (`PA4`). | 11/19/2026 | 11/22/2026 | **Finished (100%)** | Completed: Added `cmd_hil_test_interfaces` in [src/main.c](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/src/main.c) returning structured JSON report and integrated into HIL Pytest `test_07` |
| **TASK-A08** | **HIL-005** | Architectural & Hardware Walkthrough Documentation Suite | Author comprehensive technical documentation covering system overview, hardware pinout, firmware architecture, build & run instructions, and state machine with interface testing procedures. | 11/18/2026 | 11/23/2026 | **Finished (100%)** | Completed: 5 comprehensive guides in [howitwork/](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/howitwork/) with differential equations $\frac{dP}{dt}$, wiring diagrams, and loopback testing guides |

---

## 🔍 รายละเอียดงานเชิงลึก (Task Deep Dives)

### 1. TASK-A05: STM32H563ZI Plant Simulator Firmware (HIL-002)
* **Metadata:** 11/17/2026 – 11/20/2026 | Status: `Finished (100%)`
* **Scope & Implementation:**
  * **PWM Receiver Driver:** [src/kr260/kr260_pwm_receiver.c](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/src/kr260/kr260_pwm_receiver.c) วัด Pulse Width พิน `PF15` (Arduino D2) ด้วย Hardware Cycle Counter
  * **Discrete I/O Controller:** [src/io_controller.c](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/src/io_controller.c) จัดการ Start/Stop (`PB13`), Solenoid Purge Valve (`PE11`), Hardware E-Stop (`PE9`)
  * **I2C Pressure Target (0x58):** จำลอง RAM Register 8 Bytes แสดงผลความดัน $0.01\text{ kPa}$ resolution
  * **AC Audio Leak Simulation:** [src/audio_leak.c](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/src/audio_leak.c) สัญญาณเสียงลมรั่ว AC $3\text{ kHz}$ Sine Wave ผ่าน DAC1 (`PA4`)
  * **GI Finite State Machine:** [src/gi_state_machine.c](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/src/gi_state_machine.c) FSM 6 สถานะ: `IDLE`, `INSUFFLATION`, `STABLE_INSPECTION`, `LEAK_EVENT`, `DEFLATION_STOP`, `EMERGENCY_STOP`
  * **Zephyr Shell Test API:** คำสั่ง `hil status`, `hil set_state`, `hil set_pressure`, `hil inject_leak`, `hil set_start_stop`, `hil set_solenoid`, `hil set_estop`, `hil reset`

### 2. TASK-A06: STM32 Multi-Domain State Machine & Architecture Diagrams (HIL-003)
* **Metadata:** 11/18/2026 – 11/20/2026 | Status: `Finished (100%)`
* **Scope & Implementation:**
  * ออกแบบสถาปัตยกรรมแบ่งออกเป็น 4 โดเมนหลัก:
    1. **Domain 1 (Left - Blue):** FPGA PL I/O & Actuators (Airpump PWM, Start/Stop IO, Solenoid Valve, Hardware E-Stop, DAC Audio Receiver)
    2. **Domain 2 (Center - Green):** STM32 Mock Plant FSM Loop (4-Step Cyclic Engine: Receive Command $\rightarrow$ Parse & Read Sensors $\rightarrow$ Physics Simulation & Update $\rightarrow$ Send Response) และ 6-State GI Medical Physics
    3. **Domain 3 (Right - Amber):** HIL Linux Domain (KR260 PS PID Loop, V4L2 Video Pipeline, Host PC Pytest Controller)
    4. **Domain 4 (Bottom - Cyan):** Interface Self-Test & Loopback Validation (I2C, GPIO, PWM, Audio, Telemetry)
  * **Deliverables:**
    * PNG Resolution: $1650 \times 1850\text{ px}$ ([docs/images/stm32_plant_state_machine_interfaces.png](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/docs/images/stm32_plant_state_machine_interfaces.png))
    * Vector SVG: ([docs/images/stm32_plant_state_machine_interfaces.svg](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/docs/images/stm32_plant_state_machine_interfaces.svg))

### 3. TASK-A07: Interface Self-Test & Loopback Engine (HIL-004)
* **Metadata:** 11/19/2026 – 11/22/2026 | Status: `Finished (100%)`
* **Scope & Implementation:**
  * ฝังฟังก์ชัน `cmd_hil_test_interfaces()` ใน [src/main.c](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/src/main.c) เพื่อให้รันคำสั่ง `hil test_interfaces` ผ่านพอร์ต Serial
  * ตรวจสอบความพร้อมระดับฮาร์ดแวร์แบบเรียลไทม์:
    * I2C Target `0x58` (Registers 0x00-0x07)
    * Start/Stop IO (`PB13`)
    * Solenoid Purge Valve (`PE11`)
    * Hardware E-Stop Cutoff (`PE9`)
    * Airpump PWM Capture Receiver (`PF15`)
    * AC Audio Leak DAC (`PA4`)
  * ส่งข้อมูลกลับในรูปแบบ Structured JSON เพื่อให้ Pytest Suite ([tests/test_hil_stm32.py](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/tests/test_hil_stm32.py) `test_07`) ประมวลผลได้ทันที

### 4. TASK-A08: Architectural & Hardware Walkthrough Documentation Suite (HIL-005)
* **Metadata:** 11/18/2026 – 11/23/2026 | Status: `Finished (100%)`
* **Scope & Implementation:**
  * จัดทำเอกสารคู่มือเชิงเทคนิคฉบับสมบูรณ์ในโฟลเดอร์ [howitwork/](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/howitwork/):
    1. [01_system_overview_and_architecture.md](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/howitwork/01_system_overview_and_architecture.md): โครงสร้าง HIL Testbench, ภาพรวมสถาปัตยกรรม และตารางเปรียบเทียบ
    2. [02_hardware_and_pinout.md](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/howitwork/02_hardware_and_pinout.md): แผนผังสายไฟ Nucleo-H563ZI $\leftrightarrow$ Kria KR260, สัญญาณ PMOD, RPi Header และมาตรการความปลอดภัย
    3. [03_firmware_architecture_and_modules.md](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/howitwork/03_firmware_architecture_and_modules.md): เจาะลึกโมดูล Zephyr RTOS, RTOS Threads, DAC 12-bit LUT, DWT Cycle Counter
    4. [04_how_to_build_flash_and_run.md](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/howitwork/04_how_to_build_flash_and_run.md): ขั้นตอนการคอมไพล์ผ่าน `make build`, แฟลชผ่าน `make flash`, รัน Pytest `make test` และคำสั่ง Zephyr Shell API
    5. [05_stm32_plant_state_machine_and_interfaces.md](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/howitwork/05_stm32_plant_state_machine_and_interfaces.md): ไดอะแกรม State Machine 4 โดเมน, สมการโมเดลการอัดก๊าซ $\frac{dP}{dt}$, และขั้นตอนการทดสอบ Loopback แต่ละ Interface

---

## 📁 ดัชนีไฟล์ซอร์สโค้ดและทรัพยากรหลัก (Resource Index)

* **ไดอะแกรมสถาปัตยกรรม:** [docs/images/stm32_plant_state_machine_interfaces.png](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/docs/images/stm32_plant_state_machine_interfaces.png) | [docs/images/stm32_plant_state_machine_interfaces.svg](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/docs/images/stm32_plant_state_machine_interfaces.svg)
* **เฟิร์มแวร์ Plant Simulator:** [src/main.c](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/src/main.c) | [src/gi_state_machine.c](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/src/gi_state_machine.c) | [src/audio_leak.c](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/src/audio_leak.c) | [src/io_controller.c](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/src/io_controller.c) | [src/kr260/kr260_pwm_receiver.c](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/src/kr260/kr260_pwm_receiver.c)
* **ชุดทดสอบ HIL Pytest:** [tests/test_hil_stm32.py](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/tests/test_hil_stm32.py) | [tests/clinical_scenarios.json](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/tests/clinical_scenarios.json) | [reports/test_results.csv](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/reports/test_results.csv)
* **FPGA RTL Core:** [hardware/rtl/pwm_controller.sv](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/hardware/rtl/pwm_controller.sv) | [hardware/rtl/axi_pwm_controller.sv](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/hardware/rtl/axi_pwm_controller.sv) | [hardware/xdc/kr260_constraints.xdc](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/hardware/xdc/kr260_constraints.xdc)
* **ชุดคู่มือเทคนิค:** [howitwork/README.md](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/howitwork/README.md)
