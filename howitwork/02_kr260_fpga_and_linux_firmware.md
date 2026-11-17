# คู่มือการทำงานของเฟิร์มแวร์ Kria KR260 (FPGA RTL & Embedded Linux)

เอกสารฉบับนี้อธิบายหลักการทำงานระดับฮาร์ดแวร์ FPGA (Programmable Logic - PL) และระบบซอฟต์แวร์ควบคุมบนฝั่งประมวลผล (Processing System - PS) ของบอร์ด **AMD Xilinx Kria KR260 Robotics Starter Kit**

---

## 1. หลักการทำงานภายใน (Internal Architecture)

Kria KR260 ใช้สถาปัตยกรรม Zynq UltraScale+ MPSoC แบ่งการทำงานออกเป็น 2 ชั้นหลัก:
1. **FPGA Hardware Fabric (PL):** ขับสัญญาณ PWM ความแม่นยำสูง และมีวงจรตัดไฟฉุกเฉิน (Hardware Interlock)
2. **Embedded Linux Stack (PS):** รัน PetaLinux/Ubuntu ประมวลผล PID Control Loop, อ่าน I2C Telemetry จาก STM32 และรัน AI Vision

```
+-----------------------------------------------------------------------------------+
|                            KRIA KR260 ARCHITECTURE                               |
|                                                                                   |
|  [PS: Quad-Core ARM Cortex-A53 @ 1.2 GHz]                                        |
|  • Linux Kernel 5.15 / Ubuntu 22.04 LTS                                          |
|  • Closed-Loop PID Controller (software/control/closed_loop_runner.py)           |
|  • I2C Telemetry Client (SMBus /dev/i2c-1)                                       |
|  • Memory-Mapped AXI Driver (/dev/mem or UIO)                                    |
|                                     │                                             |
|                                     │ AXI4-Lite Interconnect (0xA0000000)         |
|                                     ▼                                             |
|  [PL: FPGA Fabric RTL Firmware]                                                   |
|  • axi_pwm_controller.sv: Address Decoder & Control Registers                    |
|  • pwm_controller.sv: 10-bit PWM Core + HW Clock Prescaler                        |
|  • Hardware E-Stop Gate: Latency < 10 ns (ตัดไฟปั๊มเป็น 0% ทันทีในระดับเกต)         |
|                                     │                                             |
|                                     ├────────► PMOD1 Pin 1: Airpump PWM Out       |
|                                     ├────────► PMOD1 Pin 2: Solenoid Valve Out    |
|                                     ├────────► PMOD1 Pin 3: Start/Stop Out        |
|                                     └────────► PMOD1 Pin 4: Emergency Stop Out    |
+-----------------------------------------------------------------------------------+
```

---

### 1.1 โมดูล SystemVerilog ขับปั๊มลม (`hardware/rtl/pwm_controller.sv`)

* **ความละเอียด 10-bit (0 - 1023 ระดับ):** ปรับความเร็วรอบของมอเตอร์ปั๊มลมได้ละเอียดถึง 0.097% ต่อสเต็ป
* **Clock Prescaler:** แปลงความถี่หลัก AXI Clock (100 MHz) ลงมาเป็นความถี่สวิตชิ่งของปั๊ม (ค่าเริ่มต้น 9.76 kHz ปรับแต่งได้ 1 kHz - 50 kHz):
  $$f_{pwm} = \frac{f_{clk}}{(\text{prescaler} + 1) \times 1024}$$
* **ระบบความปลอดภัยระดับเครื่องมือแพทย์ (Medical Safety Hardware Cutoff):**
  * ขา `emergency_stop` เป็นสัญญาณอะซิงโครนัสเข้าสู่วงจร Combinational Gate โดยตรง
  * หากเกิดเหตุฉุกเฉิน สัญญาณจะตัด Duty Cycle เหลือ 0 และดึงขา PWM ลงกราวด์ (0V) ภายในเวลา **น้อยกว่า 10 นาโนวินาที** โดยไม่ต้องรอคำสั่งจาก CPU หรือซอฟต์แวร์ Linux

---

### 1.2 วงจร AXI4-Lite Wrapper (`hardware/rtl/axi_pwm_controller.sv`)

เชื่อมต่อวงจร PWM เข้ากับบัสหน่วยความจำของ CPU ผ่าน Memory Map Address (Base Address เช่น `0xA0000000`):

| Address Offset | รีจิสเตอร์ (Register) | ขนาด | รายละเอียดการควบคุม |
|---|---|---|---|
| `0x00` | **PWM_CTRL** | 32-bit | • Bit 0: `Enable` (1 = สั่งเริ่มทำงาน, 0 = ปิด)<br>• Bit 1: `Soft E-Stop` (1 = บังคับหยุดฉุกเฉิน)<br>• Bit 2: `Reset Counter` |
| `0x04` | **PWM_PRESCALER** | 32-bit | ค่าตัวหารความถี่ (Default = 9) |
| `0x08` | **PWM_DUTY** | 32-bit | ค่า Duty 10-bit (ช่วงค่า `0` ถึง `1023`) |
| `0x0C` | **PWM_STATUS** | 32-bit | • Bit 0: `Running`<br>• Bit 1: `Hardware E-Stop Active`<br>• Bit 2: `Overload Tripped` |

---

### 1.3 สแตกซอฟต์แวร์บน Embedded Linux (PS Control Stack)

ฝั่ง Linux มีซอฟต์แวร์หลัก 3 โมดูล:

1. **ไดรเวอร์อ่านเซนเซอร์ความดัน I2C (`software/drivers/pressure_sensor.py`):**
   * ใช้ไลบรารี `smbus2` อ่านบล็อกข้อมูล 8 ไบต์จาก STM32 (I2C-1 Address `0x58`)
   * แปลงข้อมูลดิบ MSB/LSB เป็นแรงดันจริง (kPa) พร้อมอ่านสถานะ GI State และ Warning Flags
2. **ไดรเวอร์ควบคุมฮาร์ดแวร์ PWM (`software/drivers/pwm_driver.py`):**
   * ใช้ฟังก์ชัน `mmap` แมปหน่วยความจำกายภาพของ FPGA (`/dev/mem` Offset `0xA0000000`)
   * แปลงเปอร์เซ็นต์คำสั่ง 0-100% เป็นค่า 10-bit และเขียนลงรีจิสเตอร์ทันที
3. **ระบบควบคุมวงปิด Closed-Loop PID Runner (`software/control/closed_loop_runner.py`):**
   * นำค่า Feedback ความดันปัจจุบันและค่า Target Setpoint (เช่น 120 kPa) เข้าสู่สมการ PID:
     $$u(t) = K_p e(t) + K_i \int_0^t e(\tau) d\tau + K_d \frac{de(t)}{dt}$$
   * ปรับค่า Duty Cycle ส่งกลับไปยังปั๊มลมทุกๆ 50 ms รักษาความดันให้นิ่งเสถียรแม้มีลมรั่ว

---

## 2. ขั้นตอนการคอมไพล์ สังเคราะห์ และรันบน KR260 (Step-by-Step Operations)

### 2.1 การจำลองการทำงาน RTL บนคอมพิวเตอร์ (Vivado Simulation)

ก่อนนำไปสังเคราะห์จริง ให้ทดสอบความถูกต้องผ่าน Vivado Testbench:

```bash
# รัน Simulation ผ่าน Vivado xsim
xvlog -sv hardware/rtl/pwm_controller.sv hardware/sim/tb_pwm_controller.sv
xelab -debug typical tb_pwm_controller -s sim_snapshot
xsim sim_snapshot -R
```

*เกณฑ์ที่ผ่าน:* Testbench จะตรวจสอบว่าเมื่อจ่าย E-Stop ขา PWM ต้องลดลงเหลือ 0 ทันที

---

### 2.2 การสร้าง Bitstream และ Device Tree Overlay บน Vivado

1. เปิด Vivado และสร้างโปรเจกต์สำหรับบอร์ด **Kria KR260 Robotics Starter Kit**
2. เพิ่มโมดูล `axi_pwm_controller.sv`, `pwm_controller.sv`, และไฟล์ขา `hardware/xdc/kr260_constraints.xdc`
3. เชื่อมต่อเข้ากับ Block Design ของ Zynq UltraScale+ MPSoC ผ่าน AXI Interconnect
4. สั่ง **Run Synthesis & Implementation** $\rightarrow$ **Generate Bitstream**
5. จะได้ไฟล์ `bitstream.bit` นำไปแปลงเป็น Device Tree Overlay (`pl.dtbo`) ด้วยคำสั่ง:
   ```bash
   createdts -hw system_wrapper.xsa -zocl -platform-name kr260_custom -git-branch xilinx-v2022.2 -overlay
   ```

---

### 2.3 การโหลด Bitstream เข้าสู่ FPGA บน KR260 (Runtime Loading)

เมื่อบูตระบบปฏิบัติการ PetaLinux หรือ Ubuntu บน KR260:

```bash
# 1. คัดลอกไฟล์ bitstream.bit.bin และ pl.dtbo ไปยังบอร์ด KR260
scp bitstream.bit.bin pl.dtbo petalinux@192.168.1.120:/lib/firmware/xilinx/pwm_core/

# 2. โหลด Firmware เข้า FPGA ผ่าน fpgautil
sudo fpgautil -b /lib/firmware/xilinx/pwm_core/bitstream.bit.bin -o /lib/firmware/xilinx/pwm_core/pl.dtbo
```

---

### 2.4 การรันและทดสอบระบบควบคุม Closed-Loop บน KR260

```bash
# 1. เชื่อมต่อ SSH เข้าสู่ KR260
ssh petalinux@192.168.1.120

# 2. ตรวจสอบว่าพอร์ต I2C มองเห็น STM32 (Address 0x58)
sudo i2cdetect -y -r 1

# 3. รันสคริปต์ควบคุมความดันแบบวงปิด (เป้าหมาย 120 kPa รันต่อเนื่อง 30 วินาที)
python3 software/control/closed_loop_runner.py --target 120.0 --duration 30
```

*ผลลัพธ์บนหน้าจอ:*
```
[*] Starting Closed-Loop Control to Target: 120.00 kPa
[Loop 0.05s] Target: 120.0 kPa | Measured: 101.32 kPa | Duty: 80.0% | State: INSUFFLATION
[Loop 0.50s] Target: 120.0 kPa | Measured: 110.15 kPa | Duty: 55.4% | State: INSUFFLATION
[Loop 1.20s] Target: 120.0 kPa | Measured: 119.98 kPa | Duty: 24.1% | State: STABLE_INSPECTION
[Loop 2.00s] Target: 120.0 kPa | Measured: 120.02 kPa | Duty: 23.8% | State: STABLE_INSPECTION
[*] Target pressure locked within +/- 0.5 kPa. System stable.
```
