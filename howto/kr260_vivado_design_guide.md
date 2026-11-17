# คู่มือการสร้าง Vivado Hardware Design เริ่มต้นสำหรับ Kria KR260 (kr260_vivado_design_guide.md)
## โครงการ: GI Detect System & HIL Testbench (AMD Xilinx Vivado)

เอกสารฉบับนี้เป็นคู่มือเชิงปฏิบัติการ (Hands-on Step-by-Step Guide) สำหรับการสร้าง **Hardware Block Design บน Vivado** ตั้งแต่ศูนย์ เพื่อรองรับการทำงานของระบบ **GI Detect** (คุมปั๊มลม PWM, คุมโซลินอยด์วาล์ว GPIO, สื่อสาร I2C กับ STM32, และเตรียมรับเสียง Mic)

---

## สารบัญ
1. [สิ่งที่ต้องเตรียมล่วงหน้า (Prerequisites & Board Files)](#1-สิ่งที่ต้องเตรียมล่วงหน้า)
2. [การสร้างโปรเจกต์ Vivado สำหรับ KR260](#2-การสร้างโปรเจกต์-vivado-สำหรับ-kr260)
3. [การสร้าง Block Design และการวาง IP สำคัญ](#3-การสร้าง-block-design-และการวาง-ip-สำคัญ)
   - [3.1 Zynq UltraScale+ MPSoC IP Core](#31-zynq-ultrascale-mpsoc-ip-core)
   - [3.2 AXI IIC (สำหรับคุยกับ STM32)](#32-axi-iic-สำหรับคุยกับ-stm32)
   - [3.3 AXI Timer / PWM Generator (สำหรับขับ Airpump)](#33-axi-timer--pwm-generator-สำหรับขับ-airpump)
   - [3.4 AXI GPIO (สำหรับคุม Solenoid Valve)](#34-axi-gpio-สำหรับคุม-solenoid-valve)
   - [3.5 การต่อวงจร Clock, Reset และ Concat Interrupt](#35-การต่อวงจร-clock-reset-และ-concat-interrupt)
4. [การเขียนพินคอนฟิก Constraints (`kr260_pins.xdc`)](#4-การเขียนพินคอนฟิก-constraints-kr260_pinsxdc)
5. [การตรวจสอบ, สร้าง Bitstream และ Export XSA](#5-การตรวจสอบ-สร้าง-bitstream-และ-export-xsa)
6. [ทางเลือก: รันอัตโนมัติผ่าน Vivado TCL Script](#6-ทางเลือก-รันอัตโนมัติผ่าน-vivado-tcl-script)

---

## 1. สิ่งที่ต้องเตรียมล่วงหน้า

* **โปรแกรม:** Xilinx Vivado (แนะนำเวอร์ชัน **2022.2** หรือ **2023.2**)
* **Board Definition Files (BDF):** บอร์ด Kria KR260 มีพินและค่าคอนฟิกเฉพาะ ต้องติดตั้ง Board Files ก่อน:
  1. เปิด Vivado $\rightarrow$ ไปที่แถบ **Tools** $\rightarrow$ **Vivado Store...**
  2. เลือกแท็บ **Boards** ค้นหาคำว่า `KR260`
  3. คลิกขวาที่ **Kria KR260 Robotics Starter Kit** แล้วกด **Install**
  *(หรือดาวน์โหลดจาก GitHub `Xilinx/board_store` แล้วนำไปวางใน `<Vivado_Path>/data/boards/board_files/`)*

---

## 2. การสร้างโปรเจกต์ Vivado สำหรับ KR260

1. เปิดโปรแกรม Vivado เลือก **Create Project**
2. ตั้งชื่อโปรเจกต์ เช่น `kr260_hil_hardware`
3. ในหน้า **Project Type**:
   * เลือก **RTL Project**
   * ติ๊กถูกหน้า *Do not specify sources at this time*
4. ในหน้า **Default Part**:
   * สลับไปที่แท็บ **Boards**
   * ค้นหา `KR260`
   * เลือก **Kria KR260 Robotics Starter Kit** (เวอร์ชันล่าสุด) แล้วกด **Next** $\rightarrow$ **Finish**

---

## 3. การสร้าง Block Design และการวาง IP สำคัญ

กดที่เมนูด้านซ้าย **Create Block Design** ตั้งชื่อว่า `design_1`

```
+---------------------------------------------------------------------------------------------------------+
|                                        Vivado Block Design (`design_1`)                                  |
|                                                                                                         |
| +------------------------------------+                +------------------+     +----------------------+ |
| |      Zynq UltraScale+ MPSoC        |  M_AXI_HPM0    |  AXI SmartConnect| --> | AXI IIC (to STM32)   | |
| |                                    | =============> |                  | --> | AXI Timer (PWM Pump) | |
| | - DDR4 Controller (4GB)            |                +------------------+ --> | AXI GPIO (Solenoid)  | |
| | - DisplayPort / USB 3.0 / GEM      |                                                                  |
| | - pl_clk0 (100 MHz), pl_resetn0    | --------+                                                        |
| | - pl_ps_irq0 (Interrupt Input)     | <----+  | (Clock & Reset Network)                                |
| +------------------------------------+      |  v                                                        |
|                                         +---+----+                                                      |
|                                         | Concat | <--- (Interrupts from I2C, Timer, GPIO)              |
|                                         +--------+                                                      |
+---------------------------------------------------------------------------------------------------------+
```

### 3.1 Zynq UltraScale+ MPSoC IP Core
1. กดปุ่ม `+` (Add IP) ค้นหา **Zynq UltraScale+ MPSoC** แล้ววางลงใน Diagram
2. ด้านบนแถบสีเขียวจะขึ้นข้อความ:  
   `Designer Assistance available. Run Block Automation`
   * **กดคลิก "Run Block Automation" ทันที**
   * ติ๊กถูกเลือกบอร์ด preset ของ KR260 แล้วกด OK
   *(Vivado จะโหลดคอนฟิกพิน DDR4 4GB, MIO Ethernet, USB, SD Card, และ I/O มาตรฐานของ Kria SOM ให้ถูกต้อง 100% โดยอัตโนมัติ)*
3. ดับเบิลคลิกที่ตัว IP เพื่อตรวจเช็คการตั้งค่า:
   * **Clock Configuration:** ตรวจสอบว่า `PL Fabric Clocks` มี `pl_clk0` เปิดอยู่ (ความถี่เริ่มต้นคือ **100 MHz**)
   * **PS-PL Configuration:** ตรวจสอบว่าเปิดพอร์ต `M_AXI_HPM0_FPD` หรือ `M_AXI_HPM0_LPD` (ความกว้าง 32-bit หรือ 64-bit) เพื่อใช้คุยกับวงจรใน PL
   * **General:** เปิดพอร์ต `pl_ps_irq0` (Interrupt ขาเข้าจาก PL)

---

### 3.2 AXI IIC (สำหรับคุยกับ STM32)
ใช้สำหรับให้ Linux บน KR260 อ่านค่าความดันจำลองจาก STM32 (Address `0x58`):
1. กด `+` ค้นหา **AXI IIC** แล้ววางลงไป
2. ดับเบิลคลิกเข้าไปตั้งค่า:
   * **Mode:** Master
   * **I2C Rate:** 100 kHz (Standard Mode)
3. คลิกขวาที่พอร์ต `IIC` บนตัว IP เลือก **Make External** (จะได้พอร์ตภายนอกชื่อ `IIC_0`)

---

### 3.3 AXI Timer / PWM Generator (สำหรับขับ Airpump)
ใช้สำหรับส่งสัญญาณ PWM (0 - 100% Duty Cycle) ไปขับปั๊มลมทางฮาร์ดแวร์:
1. กด `+` ค้นหา **AXI Timer** แล้ววางลงไป
2. ดับเบิลคลิกเข้าไปตั้งค่า:
   * ติ๊กถูกเปิดใช้งาน **Generate PWM**
3. คลิกขวาที่ขาพอร์ต **`pwm0`** เลือก **Make External** (ตั้งชื่อพอร์ตภายนอกว่า `airpump_pwm`)

---

### 3.4 AXI GPIO (สำหรับคุม Solenoid Valve)
ใช้สั่งเปิด/ปิดวาล์วระบายลมฉุกเฉิน (High = เปิดวาล์ว, Low = ปิดวาล์ว):
1. กด `+` ค้นหา **AXI GPIO** แล้ววางลงไป
2. ดับเบิลคลิกเข้าไปตั้งค่า:
   * **GPIO Width:** `1` (ใช้แค่ 1 บิต)
   * ติ๊กถูก **All Outputs**
3. คลิกขวาที่ขาพอร์ต **`gpio_io_o`** เลือก **Make External** (ตั้งชื่อพอร์ตภายนอกว่า `solenoid_valve_en`)

---

### 3.5 การต่อวงจร Clock, Reset และ Concat Interrupt

1. **เชื่อมต่อ AXI Bus:**
   * สังเกตแถบสีเขียวด้านบน กด **Run Connection Automation**
   * ติ๊กเลือกเชื่อมต่อทุกตัว (Vivado จะสร้าง **AXI SmartConnect** และ **Processor System Reset** เชื่อมต่อสัญญาณ `pl_clk0` และ `pl_resetn0` ให้ครบทุกบล็อกโดยอัตโนมัติ)
2. **เชื่อมต่อ Interrupt:**
   * กด `+` เพิ่ม IP ชื่อ **Concat**
   * ปรับขนาด `Number of Ports` เป็น **3**
   * ลากสาย:
     * `In0`: ต่อกับขา `iic2intc_irpt` ของ AXI IIC
     * `In1`: ต่อกับขา `interrupt` ของ AXI Timer
     * `In2`: ต่อกับขา `ip2intc_irpt` ของ AXI GPIO
   * ลากขาเอาต์พุต `dout` ของ Concat ไปเสียบเข้าขา **`pl_ps_irq0`** ของ Zynq MPSoC

---

## 4. การเขียนพินคอนฟิก Constraints (`kr260_pins.xdc`)

สร้างไฟล์ Constraints เพื่อแมปสายสัญญาณจาก Block Design ออกสู่พินจริงบนคอนเนกเตอร์ของ KR260:

ไปที่เมนู **Sources** $\rightarrow$ คลิกขวา **Constraints** $\rightarrow$ **Add Sources...** $\rightarrow$ **Create File** ตั้งชื่อว่า `kr260_pins.xdc` แล้วใส่โค้ดดังนี้:

```tcl
# ==============================================================================
# Constraints file สำหรับ KR260 Robotics Starter Kit (GI Detect & HIL)
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. บัส I2C (AXI IIC ต่อไปหา STM32 PB8/PB9)
# แมปออก Raspberry Pi Header พิน 3 (SDA) และ พิน 5 (SCL)
# ------------------------------------------------------------------------------
set_property PACKAGE_PIN AC14 [get_ports IIC_0_scl_io]
set_property IOSTANDARD LVCMOS33 [get_ports IIC_0_scl_io]
set_property PULLUP true [get_ports IIC_0_scl_io]

set_property PACKAGE_PIN AD14 [get_ports IIC_0_sda_io]
set_property IOSTANDARD LVCMOS33 [get_ports IIC_0_sda_io]
set_property PULLUP true [get_ports IIC_0_sda_io]

# ------------------------------------------------------------------------------
# 2. Airpump PWM Output (ต่อไปยังวงจรขับมอเตอร์ปั๊มลม)
# แมปออก PMOD 1 (พิน 1)
# ------------------------------------------------------------------------------
set_property PACKAGE_PIN H12 [get_ports airpump_pwm]
set_property IOSTANDARD LVCMOS33 [get_ports airpump_pwm]
set_property SLEW SLOW [get_ports airpump_pwm]

# ------------------------------------------------------------------------------
# 3. Solenoid Valve Control Output (ต่อไปยัง Relay / Mosfet คุมวาล์ว)
# แมปออก PMOD 1 (พิน 2)
# ------------------------------------------------------------------------------
set_property PACKAGE_PIN E10 [get_ports solenoid_valve_en]
set_property IOSTANDARD LVCMOS33 [get_ports solenoid_valve_en]
set_property SLEW SLOW [get_ports solenoid_valve_en]
```

> [!TIP]
> บน KR260 คอนเนกเตอร์ **Raspberry Pi Header** และ **PMOD Headers** ใช้ไฟระดับ **3.3V (LVCMOS33)** ซึ่งแมตช์กับระดับแรงดันไฟของบอร์ด STM32H5 ได้พอดีโดยไม่ต้องใช้วงจรแปลงระดับแรงดัน (Logic Level Shifter) ครับ

---

## 5. การตรวจสอบ, สร้าง Bitstream และ Export XSA

1. **ตรวจสอบความถูกต้องของวงจร (Validate Design):**
   * ในหน้า Diagram ให้กดปุ่ม **F6** หรือไอคอนเครื่องหมายถูก (*Validate Design*)
   * ต้องขึ้นข้อความ: `Validation successful. There are no errors or critical warnings in this design.`
2. **สร้าง HDL Wrapper:**
   * ในหน้าต่าง **Sources** $\rightarrow$ คลิกขวาที่ `design_1.bd`
   * เลือก **Create HDL Wrapper...** $\rightarrow$ เลือก *Let Vivado manage wrapper and auto-update* $\rightarrow$ กด OK
3. **สั่งคอมไพล์ FPGA (Generate Bitstream):**
   * ที่เมนูด้านซ้ายล่าง กด **Generate Bitstream**
   * ยืนยันการรัน Synthesis และ Implementation (ขั้นตอนนี้ใช้เวลาประมาณ 10 - 20 นาที)
4. **ส่งออกไฟล์ฮาร์ดแวร์ XSA (Export Hardware):**
   * เมื่อ Generate Bitstream เสร็จสมบูรณ์ ให้ไปที่เมนู:  
     `File` $\rightarrow$ `Export` $\rightarrow$ `Export Hardware...`
   * ในหน้าต่าง Export ให้เลือก: **Include bitstream** *(สำคัญมาก)*
   * บันทึกไฟล์เป็นชื่อ **`system_wrapper.xsa`**

*(ไฟล์ `system_wrapper.xsa` นี้คือไฟล์ที่จะนำไปโยนให้คำสั่ง `petalinux-config --get-hw-description` ในคู่มือ [kr260_bringup_and_flash_guide.md](file:///Users/pongpipat/hil/howto/kr260_bringup_and_flash_guide.md) ครับ)*

---

## 6. ทางเลือก: รันอัตโนมัติผ่าน Vivado TCL Script

หากคุณต้องการให้ Vivado สร้าง Block Design นี้ขึ้นมาอัตโนมัติทั้งหมดโดยไม่ต้องคลิกด้วยมือใน GUI คุณสามารถเปิด Vivado Tcl Shell แล้วรันสคริปต์นี้ได้ทันที:

```tcl
# build_kr260_hardware.tcl
create_project kr260_hil ./kr260_hil -part xck26-sfvc784-2LV-c
set_property board_part xilinx.com:kr260_som:part0:1.1 [current_project]

# สร้าง Block Design
create_bd_design "design_1"

# 1. วาง MPSoC
create_bd_cell -type ip -vlnv xilinx.com:ip:zynq_ultra_ps_e zynq_ultra_ps_e_0
apply_bd_automation -rule xilinx.com:bd_rule:zynq_ultra_ps_e -config {apply_board_preset "1"} [get_bd_cells zynq_ultra_ps_e_0]

# 2. วาง I2C, Timer, GPIO
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_iic axi_iic_0
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_timer axi_timer_0
set_property -dict [list CONFIG.enable_timer2 {0} CONFIG.mode_64bit {0}] [get_bd_cells axi_timer_0]
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_gpio axi_gpio_0
set_property -dict [list CONFIG.C_GPIO_WIDTH {1} CONFIG.C_ALL_OUTPUTS {1}] [get_bd_cells axi_gpio_0]

# 3. ทำการเชื่อมต่ออัตโนมัติ
apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config {Master "/zynq_ultra_ps_e_0/M_AXI_HPM0_FPD" Clk "Auto"} [get_bd_intf_pins axi_iic_0/S_AXI]
apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config {Master "/zynq_ultra_ps_e_0/M_AXI_HPM0_FPD" Clk "Auto"} [get_bd_intf_pins axi_timer_0/S_AXI]
apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config {Master "/zynq_ultra_ps_e_0/M_AXI_HPM0_FPD" Clk "Auto"} [get_bd_intf_pins axi_gpio_0/S_AXI]

# 4. สร้างพอร์ตภายนอก
make_bd_intf_pins_external [get_bd_intf_pins axi_iic_0/IIC]
make_bd_pins_external [get_bd_pins axi_timer_0/pwm0]
make_bd_pins_external [get_bd_pins axi_gpio_0/gpio_io_o]

# ตรวจสอบและบันทึก
validate_bd_design
save_bd_design
```

---

## 7. เช็คลิสต์ตรวจสอบความพร้อมก่อนขยับไป PetaLinux
* [ ] Block Design มี AXI IIC, AXI Timer (PWM), และ AXI GPIO ครบถ้วน
* [ ] ผ่านการ Validate Design (ไม่มี Error สีแดง)
* [ ] มีไฟล์ `.xdc` แมปพิน I2C (Raspberry Pi Header) และ PWM/Valve (PMOD) ถูกต้อง
* [ ] สั่ง Generate Bitstream สำเร็จ 100%
* [ ] Export ไฟล์ `.xsa` โดยเลือก **Include bitstream** เรียบร้อยแล้ว
