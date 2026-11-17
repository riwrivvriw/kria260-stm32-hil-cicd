# ==============================================================================
# Makefile for GI Detect & HIL System (RTL Simulation)
# Directory: hil/Makefile
# ==============================================================================

# เครื่องมือที่ใช้
IVERILOG = iverilog
VVP      = vvp
GTKWAVE  = gtkwave
SURFER   = surfer

# แฟล็กสำหรับ SystemVerilog (IEEE 1800-2012)
IVFLAGS  = -g2012 -Wall

# โครงสร้างโฟลเดอร์และไฟล์
RTL_DIR  = hardware/rtl
SIM_DIR  = hardware/sim

RTL_SRCS = $(RTL_DIR)/pwm_controller.sv
TB_SRCS  = $(SIM_DIR)/tb_pwm_controller.sv

# ไฟล์เอาต์พุต
SIM_OUT  = $(SIM_DIR)/sim.out
VCD_FILE = $(SIM_DIR)/pwm_wave.vcd

# Phony targets ป้องกันชื่อซ้ำกับไฟล์จริง
.PHONY: all compile sim wave surfer clean help

# คำสั่งเริ่มต้น (เมื่อพิมพ์ make เฉยๆ จะทำการคอมไพล์และรันจำลอง)
all: sim

# 1. คอมไพล์ไฟล์ SystemVerilog ทั้งหมดเป็นไฟล์ไบนารี sim.out
compile: $(SIM_OUT)

$(SIM_OUT): $(RTL_SRCS) $(TB_SRCS)
	@echo "=== [1/2] Compiling SystemVerilog RTL & Testbench ==="
	$(IVERILOG) $(IVFLAGS) -o $(SIM_OUT) $(RTL_SRCS) $(TB_SRCS)

# 2. รัน Simulation ด้วย vvp เพื่อสร้างไฟล์คลื่นสัญญาณ .vcd
sim: $(SIM_OUT)
	@echo "=== [2/2] Running Simulation (vvp) ==="
	$(VVP) $(SIM_OUT)

# 3. เปิดดูกราฟใน GTKWave (ถ้ารัน sim ยังไม่เสร็จ จะสั่งรันให้อัตโนมัติ)
wave: $(VCD_FILE)
	@echo "=== Opening Waveform in GTKWave ==="
	$(GTKWAVE) $(VCD_FILE) &

# ทางเลือกเสริม: เปิดดูกราฟด้วย Surfer บน macOS
surfer: $(VCD_FILE)
	@echo "=== Opening Waveform in Surfer ==="
	$(SURFER) $(VCD_FILE) &

# สร้างไฟล์ .vcd หากยังไม่มีหรือโค้ดมีการแก้ไข
$(VCD_FILE): $(RTL_SRCS) $(TB_SRCS)
	$(MAKE) sim

# 4. ลบไฟล์ที่สร้างจากการจำลองทั้งหมด
clean:
	@echo "=== Cleaning simulation artifacts ==="
	rm -f $(SIM_OUT) $(VCD_FILE)

# แสดงรายการคำสั่งที่ใช้ได้
help:
	@echo "Available targets:"
	@echo "  make          - คอมไพล์และรัน Simulation (สร้างไฟล์ .vcd)"
	@echo "  make compile  - คอมไพล์โค้ดอย่างเดียวเพื่อเช็ก Syntax"
	@echo "  make sim      - คอมไพล์และรัน vvp"
	@echo "  make wave     - รัน Simulation (ถ้าโค้ดเปลี่ยน) และเปิด GTKWave"
	@echo "  make surfer   - รัน Simulation (ถ้าโค้ดเปลี่ยน) และเปิด Surfer"
	@echo "  make clean    - ลบไฟล์ sim.out และ .vcd"