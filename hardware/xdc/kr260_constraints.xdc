# ==============================================================================
# File: kr260_constraints.xdc
# Project: GI Detect & HIL System
# Target Board: AMD Kria KR260 Robotics Starter Kit
# Description: กำหนดตำแหน่งขาพินจริง (Physical Pinout) และระดับแรงดันไฟ (I/O Standard)
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. บัส I2C สำหรับเชื่อมต่อกับ STM32H5 (Address 0x58)
# ตำแหน่ง: Raspberry Pi 40-pin Header (J10)
#   - Pin 3 (SDA) ต่อเข้ากับ STM32 Arduino Header D14 (PB9)
#   - Pin 5 (SCL) ต่อเข้ากับ STM32 Arduino Header D15 (PB8)
# ------------------------------------------------------------------------------
set_property PACKAGE_PIN AC14 [get_ports IIC_0_scl_io]
set_property IOSTANDARD LVCMOS33 [get_ports IIC_0_scl_io]
set_property PULLUP true [get_ports IIC_0_scl_io]

set_property PACKAGE_PIN AD14 [get_ports IIC_0_sda_io]
set_property IOSTANDARD LVCMOS33 [get_ports IIC_0_sda_io]
set_property PULLUP true [get_ports IIC_0_sda_io]

# ------------------------------------------------------------------------------
# 2. สัญญาณ Airpump PWM Output (จาก AXI Timer หรือ Custom PWM)
# ตำแหน่ง: คอนเนกเตอร์ PMOD 1 (J21)
#   - Pin 1 (H12) ต่อเข้าวงจรขับมอเตอร์ปั๊มลม (และต่อเข้า STM32 D2 สำหรับ HIL Loop)
# ------------------------------------------------------------------------------
set_property PACKAGE_PIN H12 [get_ports airpump_pwm]
set_property IOSTANDARD LVCMOS33 [get_ports airpump_pwm]
set_property SLEW SLOW [get_ports airpump_pwm]
set_property DRIVE 8 [get_ports airpump_pwm]

# ------------------------------------------------------------------------------
# 3. สัญญาณ Solenoid Valve Control Output (จาก AXI GPIO)
# ตำแหน่ง: คอนเนกเตอร์ PMOD 1 (J21)
#   - Pin 2 (E10) ต่อเข้าวงจรขับรีเลย์/MOSFET เปิด-ปิดวาล์วระบายลม
# ------------------------------------------------------------------------------
set_property PACKAGE_PIN E10 [get_ports solenoid_valve_en]
set_property IOSTANDARD LVCMOS33 [get_ports solenoid_valve_en]
set_property SLEW SLOW [get_ports solenoid_valve_en]
set_property DRIVE 8 [get_ports solenoid_valve_en]
