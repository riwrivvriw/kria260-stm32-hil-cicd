# สถาปัตยกรรมระบบและการทำงานของเฟิร์มแวร์ (Firmware Architecture & Operations Guide)

คู่มือวิศวกรรมฉบับสมบูรณ์ อธิบายหลักการทำงานภายใน (Internal Mechanics) และขั้นตอนการคอมไพล์ แฟลช และรัน (Build, Flash & Run) สำหรับเฟิร์มแวร์ทุกระบบในโครงการ **Hardware-in-the-Loop (HIL) Testbench for Kria KR260 & STM32H563ZI**

---

## 📌 ภาพรวมสถาปัตยกรรมเฟิร์มแวร์ (Dual-System Co-Design)

ระบบนี้ประกอบด้วยเฟิร์มแวร์ 2 ฝั่งที่ทำงานสอดประสานกันแบบเรียลไทม์ (Closed-Loop HIL):

```
+----------------------------------------------------------------------------------------------------+
|                                    1. HOST TESTBENCH & CI/CD                                       |
|  - Pytest HIL Controller: tests/test_hil_stm32.py (Auto-detect Serial COM / USB)                   |
|  - Synthetic Video Mock Engine: tools/video_stream_mock.py (UDP/RTP H.264 Port 5000 over Ethernet) |
|  - CSV Telemetry & Metrics Logger: reports/test_results.csv                                       |
+----------------------------------+------------------------------------+----------------------------+
                                   | USB Serial (115200 8N1)            | Ethernet LAN (RJ45)
                                   v                                    v
+--------------------------------------------------+    +--------------------------------------------+
| 2. PLANT SIMULATOR: STM32H563ZI                  |    | 3. DEVICE UNDER TEST (DUT): KRIA KR260     |
| (RTOS: Zephyr RTOS 4.x)                          |    | (OS: PetaLinux / Ubuntu 22.04)             |
|                                                  |    |                                            |
| [Firmware Modules]                               |    | [FPGA PL - Hardware RTL Firmware]          |
| • GI Finite State Machine (gi_state_machine.c)   |    | • PWM Core: hardware/rtl/pwm_controller.sv |
|   - 6 States (Idle, Insufflate, Stable, Leak,    |    |   (10-bit resolution, hardware E-Stop)     |
|     Deflate, E-Stop)                             |    | • AXI Lite Interface: axi_pwm_controller.sv|
|   - Real-time dP/dt dynamic physics equation     |    |                                            |
| • PWM Pulse Capture (kr260_pwm_receiver.c)       |<===+=== PMOD1 Pin 1 (PF15 / Arduino D2)        |
|   - DWT 250MHz dual-edge timer & watchdog        |    |                                            |
| • I2C Target EEPROM Driver (0x58, 8 Bytes)       |<===+=== RPi Header SCL/SDA (PB8/PB9 / D15/D14)  |
| • AC Audio Leak Waveform (audio_leak.c)          |===>+=== PMOD2 Pin 1 (PA4 / Arduino A2) ADC In  |
|   - DAC1 Ch1 3 kHz Sine Wave (16-point LUT)      |    |                                            |
| • GPIO IO Controller (io_controller.c)           |    | [Linux PS - Embedded Software Stack]       |
|   - Start/Stop IO (PB13 / Arduino D3)            |<===+=== PMOD1 Pin 3 (Start/Stop Trigger)        |
|   - Solenoid Valve IO (PE11 / Arduino D4)        |<===+=== PMOD1 Pin 2 (Purge Valve Output)        |
|   - Hardware E-Stop IO (PE9 / Arduino D5)        |<===+=== PMOD1 Pin 4 (Safety Cutoff Output)      |
| • Zephyr Shell Command Interface (JSON output)   |    | • Closed-Loop PID Pressure Controller      |
|                                                  |    | • Virtual Camera: /dev/video10 (v4l2loop)  |
|                                                  |    | • Vitis AI GI Polyp/Leak Detection Core    |
+--------------------------------------------------+    +--------------------------------------------+
```

---

## 📑 สารบัญคู่มือ (Documentation Index)

| เอกสาร | หัวข้อหลัก | เหมาะสำหรับ |
|---|---|---|
| **[01_stm32_zephyr_firmware.md](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/howitwork/01_stm32_zephyr_firmware.md)** | **STM32 Plant Simulator Firmware:**<br>• สถาปัตยกรรม State Machine (6 สถานะ), สมการฟิสิกส์ความดัน, ระบบวัด PWM ด้วย DWT Hardware Timer, I2C 8-byte Register Map, DAC AC Audio Generator, การควบคุม IO<br>• วิธีการ Build, Flash และ Debug ด้วย Zephyr `west` | Embedded Developers / Firmware Engineers |
| **[02_kr260_fpga_and_linux_firmware.md](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/howitwork/02_kr260_fpga_and_linux_firmware.md)** | **Kria KR260 FPGA RTL & Embedded Linux:**<br>• โมดูล SystemVerilog ขับปั๊มลม 10-bit, AXI4-Lite Slave Wrapper, พิน Constraints (XDC)<br>• สแตกซอฟต์แวร์บน Linux: SMBus I2C Driver, Closed-Loop PID Controller, และวิธีรันบน PetaLinux | FPGA & Linux Control Engineers |
| **[03_video_stream_and_sensor_sync.md](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/howitwork/03_video_stream_and_sensor_sync.md)** | **Virtual Video Stream Engine & Sensor Sync:**<br>• การสร้างภาพส่องกล้องจำลองผ่านสายแลน Ethernet (UDP/RTP H.264)<br>• การซิงค์ฉากกล้องและ On-Screen Display (OSD) แบบเรียลไทม์ตาม State Machine<br>• วิธีเปิดใช้งาน `v4l2loopback` และการรับภาพบน KR260 | Computer Vision / System Testers |
| **[04_hil_orchestration_and_cicd.md](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/howitwork/04_hil_orchestration_and_cicd.md)** | **HIL Testbench & CI/CD Pipeline:**<br>• สถาปัตยกรรม Pytest HIL Runner, Auto-detect Serial Port, ระบบกรอง ANSI Escape Sequence<br>• การบันทึกผลทดสอบลงไฟล์ CSV Format (`reports/test_results.csv`)<br>• การตั้งค่า Azure DevOps Pipeline สำหรับการทดสอบอัตโนมัติ | DevOps / Quality Assurance Engineers |

---

## 🔌 สรุปตารางการเชื่อมต่อฮาร์ดแวร์ (Hardware Pin Mapping)

| สัญญาณ (Signal) | STM32 Nucleo-H563ZI | Kria KR260 Pin | หน้าที่ทางวิศวกรรม |
|---|---|---|---|
| **I2C SCL** | Arduino **D15** (`PB8`) | RPi Header **Pin 5** (`AC14`) | บัส Clock Master จาก KR260 อ่านค่าจาก STM32 (100 kHz) |
| **I2C SDA** | Arduino **D14** (`PB9`) | RPi Header **Pin 3** (`AD14`) | บัสข้อมูล I2C Data สองทิศทาง |
| **Airpump PWM** | Arduino **D2** (`PF15`) | PMOD 1 **Pin 1** (`H12`) | สัญญาณ PWM ขับปั๊มลมจาก KR260 $\rightarrow$ STM32 วัดไปคำนวณความดัน |
| **Start/Stop IO**| Arduino **D3** (`PB13`) | PMOD 1 **Pin 3** (`H11`) | สัญญาณดิจิทัลสั่งเริ่ม/หยุดการทำงานของระบบ |
| **Solenoid Valve**| Arduino **D4** (`PE11`)| PMOD 1 **Pin 2** (`E10`) | สัญญาณดิจิทัลสั่งเปิดวาล์วระบายลม (Purge Valve) |
| **E-Stop Cutoff**| Arduino **D5** (`PE9`)  | PMOD 1 **Pin 4** (`J10`) | สัญญาณตัดไฟและหยุดการทำงานฉุกเฉินระดับฮาร์ดแวร์ |
| **Leak Audio AC**| Arduino **A2** (`PA4`)  | PMOD 2 **Pin 1** (ADC In)| สัญญาณเสียงลมรั่ว Sine Wave 3 kHz จาก DAC1 Channel 1 |
| **Video Stream** | -                      | RJ45 Ethernet (`eth0`)   | ท่อส่งสตรีมวิดีโอจำลอง UDP 5000 จาก Host Laptop |
| **Common GND**   | Arduino **GND**        | PMOD Pin 5/11 หรือ RPi Pin 6 | **ต้องต่อกราวด์ร่วมกันเสมอ** |
