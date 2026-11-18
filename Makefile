# ==============================================================================
# Makefile for HIL Testbench & Firmware Project
# 1. Zephyr RTOS STM32H563ZI Firmware (Build & Flash)
# 2. KR260 SystemVerilog RTL Simulation (Icarus Verilog & GTKWave/Surfer)
# 3. Python HIL Pytest Testbench & CSV Reporting
# ==============================================================================

SHELL := /bin/bash

# ------------------------------------------------------------------------------
# การตั้งค่า Zephyr RTOS สำหรับ STM32 Nucleo-H563ZI
# ------------------------------------------------------------------------------
BOARD           ?= nucleo_h563zi
ZEPHYR_ENV_SH   ?= ~/stm32/zephyr/zephyr-env.sh
ZEPHYR_VENV     ?= ~/stm32/.venv/bin/activate

# คำสั่งโหลด Environment และ Virtual Environment สำหรับ Zephyr
ZEPHYR_ENV_CMD  = source $(ZEPHYR_ENV_SH) && source $(ZEPHYR_VENV)

# ------------------------------------------------------------------------------
# การตั้งค่า Python Pytest HIL Testbench
# ------------------------------------------------------------------------------
PYTHON          ?= python3
VENV_DIR        ?= .venv
VENV_ACTIVATE   = source $(VENV_DIR)/bin/activate
REQUIREMENTS    = requirements.txt
REPORTS_DIR     = reports
CSV_REPORT      = $(REPORTS_DIR)/test_results.csv

# ------------------------------------------------------------------------------
# การตั้งค่า SystemVerilog Simulation (KR260 FPGA Fabric)
# ------------------------------------------------------------------------------
IVERILOG = iverilog
VVP      = vvp
GTKWAVE  = gtkwave
SURFER   = surfer
IVFLAGS  = -g2012 -Wall

RTL_DIR  = hardware/rtl
SIM_DIR  = hardware/sim
RTL_SRCS = $(RTL_DIR)/pwm_controller.sv
TB_SRCS  = $(SIM_DIR)/tb_pwm_controller.sv
SIM_OUT  = $(SIM_DIR)/sim.out
VCD_FILE = $(SIM_DIR)/pwm_wave.vcd

# ------------------------------------------------------------------------------
# Phony Targets
# ------------------------------------------------------------------------------
.PHONY: all help build build-inc flash build-flash clean-build \
        compile sim wave surfer clean-sim clean \
        venv install-deps test test-setup clean-test

# คำสั่งเริ่มต้น: แสดง Help เมนู
all: help

# ==============================================================================
# 1. Zephyr RTOS / STM32 Firmware Commands
# ==============================================================================

# คอมไพล์เฟิร์มแวร์แบบ Clean Build (Pristine: -p always)
build:
	@echo "=== [Zephyr] Building Firmware for $(BOARD) (Pristine Always) ==="
	@$(SHELL) -c "$(ZEPHYR_ENV_CMD) && west build -p always -b $(BOARD) ."

# คอมไพล์แบบ Incremental (เร็วขึ้น ไม่ล้างแคชเดิม)
build-inc:
	@echo "=== [Zephyr] Incremental Building for $(BOARD) ==="
	@$(SHELL) -c "$(ZEPHYR_ENV_CMD) && west build -b $(BOARD) ."

# แฟลชเฟิร์มแวร์ลงบอร์ด Nucleo-H563ZI ผ่าน ST-Link
flash:
	@echo "=== [Zephyr] Flashing Firmware to $(BOARD) ==="
	@$(SHELL) -c "$(ZEPHYR_ENV_CMD) && west flash"

# คอมไพล์แบบ Clean Build แล้วแฟลชลงบอร์ดทันที
build-flash: build flash

# ลบโฟลเดอร์ build ของ Zephyr
clean-build:
	@echo "=== [Zephyr] Removing build directory ==="
	rm -rf build/

# ==============================================================================
# 2. Python HIL Pytest Automation & CSV Reporting Commands
# ==============================================================================

# 1. สร้าง Virtual Environment (.venv) หากยังไม่มี
venv:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "=== [Pytest] Creating Python Virtual Environment ($(VENV_DIR)) ==="; \
		$(PYTHON) -m venv $(VENV_DIR); \
	else \
		echo "=== [Pytest] Virtual environment '$(VENV_DIR)' already exists. ==="; \
	fi

# 2. ติดตั้ง Dependencies จาก requirements.txt
install-deps: venv
	@echo "=== [Pytest] Installing dependencies from $(REQUIREMENTS) ==="
	@$(SHELL) -c "$(VENV_ACTIVATE) && pip install --upgrade pip && pip install -r $(REQUIREMENTS)"

# 3. รันการทดสอบ Pytest และสร้างรายงานผล CSV
test: venv
	@echo "=== [Pytest] Running HIL Testbench & Generating CSV Report ==="
	@mkdir -p $(REPORTS_DIR)
	@$(SHELL) -c "$(VENV_ACTIVATE) && pytest tests/ -v --csv=$(CSV_REPORT)"

# 4. คำสั่ง All-in-One: ติดตั้ง Dependencies และรัน Test ต่อเนื่อง
test-setup: install-deps test

# ลบแคชของ Pytest และรายงานผล
clean-test:
	@echo "=== [Pytest] Cleaning pytest cache and reports ==="
	rm -rf .pytest_cache/ $(REPORTS_DIR)/*.csv tests/__pycache__/

# ==============================================================================
# 3. RTL SystemVerilog Simulation Commands
# ==============================================================================

compile: $(SIM_OUT)

$(SIM_OUT): $(RTL_SRCS) $(TB_SRCS)
	@echo "=== [RTL] Compiling SystemVerilog RTL & Testbench ==="
	$(IVERILOG) $(IVFLAGS) -o $(SIM_OUT) $(RTL_SRCS) $(TB_SRCS)

sim: $(SIM_OUT)
	@echo "=== [RTL] Running Simulation (vvp) ==="
	$(VVP) $(SIM_OUT)

wave: $(VCD_FILE)
	@echo "=== [RTL] Opening Waveform in GTKWave ==="
	$(GTKWAVE) $(VCD_FILE) &

surfer: $(VCD_FILE)
	@echo "=== [RTL] Opening Waveform in Surfer ==="
	$(SURFER) $(VCD_FILE) &

$(VCD_FILE): $(RTL_SRCS) $(TB_SRCS)
	$(MAKE) sim

clean-sim:
	@echo "=== [RTL] Cleaning simulation artifacts ==="
	rm -f $(SIM_OUT) $(VCD_FILE)

# ลบไฟล์ Build, Simulation และ Test ทั้งหมด
clean: clean-build clean-sim clean-test

# ==============================================================================
# 4. Help Menu
# ==============================================================================
help:
	@echo "=================================================================="
	@echo " HIL Project Makefile - Commands Overview"
	@echo "=================================================================="
	@echo " [Zephyr RTOS / STM32H563ZI Firmware]"
	@echo "   make build        : คอมไพล์แบบ Pristine (west build -p always -b $(BOARD) .)"
	@echo "   make build-inc    : คอมไพล์แบบ Incremental (west build -b $(BOARD) .)"
	@echo "   make flash        : แฟลชเฟิร์มแวร์ลงบอร์ด (west flash)"
	@echo "   make build-flash  : คอมไพล์ Pristine แล้วแฟลชลงบอร์ดทันที"
	@echo "   make clean-build  : ลบโฟลเดอร์ build/"
	@echo ""
	@echo " [Python HIL Pytest Automation]"
	@echo "   make venv         : สร้างโฟลเดอร์ .venv สำหรับทดสอบ"
	@echo "   make install-deps : ติดตั้ง dependencies จาก requirements.txt"
	@echo "   make test         : รัน pytest tests/ -v --csv=reports/test_results.csv"
	@echo "   make test-setup   : ติดตั้ง deps พร้อมรันการทดสอบทันที"
	@echo "   make clean-test   : ลบ .pytest_cache และรายงาน CSV"
	@echo ""
	@echo " [KR260 RTL SystemVerilog Simulation]"
	@echo "   make sim          : คอมไพล์และรัน Simulation (vvp -> pwm_wave.vcd)"
	@echo "   make wave         : รัน Simulation และเปิดดูคลื่นสัญญาณใน GTKWave"
	@echo "   make surfer       : รัน Simulation และเปิดดูคลื่นสัญญาณใน Surfer"
	@echo "   make clean-sim    : ลบไฟล์ sim.out และ pwm_wave.vcd"
	@echo ""
	@echo " [General]"
	@echo "   make clean        : ลบทั้ง build/, simulation artifacts และ test cache"
	@echo "=================================================================="
