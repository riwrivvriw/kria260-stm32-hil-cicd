"""
test_hil_stm32.py
ตัวอย่างชุดทดสอบ Pytest บน Host Laptop ควบคุม STM32 HIL ผ่าน USB Serial (Zephyr Shell)
บันทึกผลการทดสอบและค่า Telemetry เป็นรูปแบบ CSV ผ่าน Fixture ใน conftest.py
"""

import pytest
import serial
import json
import time
import re
import glob
import os
import sys


def find_stm32_port() -> str:
    """
    ฟังก์ชันค้นหาพอร์ต USB Serial ของ STM32 แบบ Cross-platform
    รองรับทั้ง macOS (/dev/tty.usbmodem*), Linux (/dev/ttyACM*), และ Windows (COM*)
    """
    # 1. ตรวจสอบจาก Environment Variable ก่อน
    env_port = os.environ.get("HIL_PORT") or os.environ.get("STM32_PORT")
    if env_port:
        return env_port

    # 2. ค้นหาผ่าน PySerial list_ports
    try:
        from serial.tools import list_ports
        com_ports = list(list_ports.comports())
        for p in com_ports:
            desc = (p.description or "").lower()
            mfg = (p.manufacturer or "").lower()
            hwid = (p.hwid or "").lower()
            # ตรวจจับชิปเซ็ต ST-Link / STMicroelectronics
            if any(k in desc or k in mfg or k in hwid for k in ("stlink", "st-link", "stm", "stmicroelectronics")):
                return p.device
            if "usbmodem" in p.device.lower() or "ttyacm" in p.device.lower():
                return p.device

        if com_ports and sys.platform.startswith("win"):
            return com_ports[0].device
    except Exception:
        pass

    # 3. Fallback ผ่าน glob สำหรับ macOS / Linux
    ports = glob.glob("/dev/tty.usbmodem*") + glob.glob("/dev/ttyACM*")
    if ports:
        return sorted(ports)[0]

    return "COM3" if sys.platform.startswith("win") else "/dev/tty.usbmodem11103"


SERIAL_PORT = find_stm32_port()
BAUDRATE = 115200

# Regex สำหรับลบ ANSI Escape Sequences (รหัสสีของ Terminal)
ANSI_REGEX = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


class STM32HILClient:
    def __init__(self, port, baudrate):
        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.baudrate = baudrate
        self.ser.timeout = 1.0
        self.ser.rtscts = False
        self.ser.dsrdtr = False

        try:
            self.ser.open()
        except serial.SerialException as e:
            raise RuntimeError(
                f"ไม่สามารถเปิดพอร์ต {port} ได้! กรุณาตรวจสอบว่ามีโปรแกรมอื่น "
                f"(เช่น Serial Monitor, screen, minicom) เปิดพอร์ตนี้ค้างอยู่หรือไม่: {e}"
            )

        # ป้องกันไม่ให้ DTR/RTS ไปกระตุกรีเซ็ตบอร์ด
        try:
            self.ser.dtr = False
            self.ser.rts = False
        except Exception:
            pass

        time.sleep(0.3)
        self.ser.reset_input_buffer()
        # ส่ง Enter ปลุก Shell
        self.ser.write(b"\r\n")
        time.sleep(0.2)
        self.ser.reset_input_buffer()

    def send_cmd(self, cmd: str, timeout: float = 2.0) -> str:
        """ส่งคำสั่งไปยัง Zephyr Shell และรออ่านผลลัพธ์แบบ Robust Timeout Loop"""
        try:
            self.ser.reset_input_buffer()
            self.ser.write(f"{cmd}\r\n".encode())
        except Exception as e:
            raise RuntimeError(f"ไม่สามารถส่งคำสั่งไปยังบอร์ดได้: {e}")

        start_time = time.time()
        lines = []

        while time.time() - start_time < timeout:
            try:
                raw_line = self.ser.readline().decode(errors="ignore")
            except serial.SerialException:
                time.sleep(0.05)
                continue

            if not raw_line:
                continue

            clean_line = ANSI_REGEX.sub('', raw_line).strip()
            if clean_line and cmd not in clean_line:
                lines.append(clean_line)
                # เมื่อพบ JSON หรือ Prompt แล้ว แปลว่าบอร์ดตอบเสร็จสิ้น
                if "}" in clean_line or "hil:~$" in clean_line:
                    break

        return "\n".join(lines)

    def send_cmd_json(self, cmd: str) -> dict:
        """ส่งคำสั่งและค้นหา JSON Object ในข้อความตอบกลับโดยเฉพาะ"""
        raw_output = self.send_cmd(cmd)

        # ค้นหาข้อความที่อยู่ในรูปแบบ JSON {...}
        json_match = re.search(r'\{.*\}', raw_output)
        if not json_match:
            raise ValueError(f"No JSON found in response:\n{raw_output}")

        return json.loads(json_match.group(0))

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()


@pytest.fixture(scope="module")
def hil():
    port = find_stm32_port()
    client = STM32HILClient(port, BAUDRATE)
    yield client
    client.close()


def test_01_read_hil_status(hil, csv_record):
    """ทดสอบอ่านสถานะ JSON จาก STM32 และบันทึกค่าลง CSV"""
    data = hil.send_cmd_json("hil status")

    # บันทึกข้อมูล Telemetry ลงในรายงานผล CSV
    csv_record({
        "chip_id": data.get("chip_id"),
        "pressure_kpa": data.get("pressure_kpa"),
        "pump_duty": data.get("pump_duty", 0.0),
        "pwm_freq_hz": data.get("pwm_freq_hz", 0),
        "leak": data.get("leak"),
        "auto": data.get("auto"),
    })

    assert data["chip_id"] == "0x58", f"Chip ID mismatch: {data['chip_id']}"
    assert (
        70.0 <= data["pressure_kpa"] <= 150.0
    ), f"Pressure out of range: {data['pressure_kpa']}"


def test_02_set_manual_pressure(hil, csv_record):
    """ทดสอบสั่งปรับค่าความดันคงที่ ตรวจสอบว่าค่าอัปเดตจริง และบันทึกลง CSV"""
    hil.send_cmd("hil set_pressure 125.50")

    data = hil.send_cmd_json("hil status")

    # บันทึกข้อมูล Telemetry ลงในรายงานผล CSV
    csv_record({
        "target_pressure": 125.50,
        "measured_pressure_kpa": data.get("pressure_kpa"),
        "auto": data.get("auto"),
    })

    assert (
        abs(data["pressure_kpa"] - 125.50) < 0.1
    ), f"Pressure set value mismatch: {data['pressure_kpa']}"
    assert data["auto"] is False, "Auto simulation should be disabled"


@pytest.mark.skip(
    reason="รอต่อสาย I2C เข้ากับบอร์ด Kria KR260 (ฮาร์ดแวร์บอร์ด Nucleo ไม่มีตัวต้านทาน Pull-up บนสายสัญญาณ)"
)
def test_03_i2c_loopback_self_test(hil, csv_record):
    """
    ทดสอบ I2C Master-to-Slave Loopback บนบอร์ด STM32
    (ต้องต่อสาย Jumper: I2C1 PB8/PB9 เข้ากับ I2C2 PF1/PF0 พร้อมตัวต้านทาน Pull-up)
    """
    data = hil.send_cmd_json("hil loopback")
    csv_record(data)

    if data.get("loopback") == "FAIL" and data.get("error_code") == -5:
        pytest.fail(
            "I2C Loopback Failed with Error -5 (-EIO / NACK): "
            "กรุณาตรวจสอบว่าได้นำสาย Jumper เชื่อมพิน I2C1 (PB8/PB9) เข้ากับ I2C2 (PF1/PF0) แล้วหรือยัง"
        )

    assert data["loopback"] == "PASS", f"I2C Loopback test failed: {data}"
    assert data["read_chip_id"] == "0x58"
