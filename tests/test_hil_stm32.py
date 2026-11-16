"""
test_hil_stm32.py
ตัวอย่างชุดทดสอบ Pytest บน Host Laptop ควบคุม STM32 HIL ผ่าน USB Serial (Zephyr Shell)
"""

import pytest
import serial
import json
import time

# กำหนด Serial Port ของ ST-Link / USB-C บน Mac (แก้ตาม port จริง เช่น /dev/tty.usbmodem...)
SERIAL_PORT = "/dev/tty.usbmodem14103"
BAUDRATE = 115200


class STM32HILClient:
    def __init__(self, port, baudrate):
        self.ser = serial.Serial(port, baudrate, timeout=2)
        time.sleep(0.5)
        # เคลียร์ buffer เริ่มต้น
        self.ser.reset_input_buffer()
        self.ser.write(b"\n")

    def send_cmd(self, cmd: str) -> str:
        """ส่งคำสั่งไปยัง Zephyr Shell และรอรับบรรทัดผลลัพธ์"""
        self.ser.reset_input_buffer()
        self.ser.write(f"{cmd}\n".encode())
        time.sleep(0.1)

        output = []
        while self.ser.in_waiting > 0:
            line = self.ser.readline().decode(errors="ignore").strip()
            if line and not line.startswith("hil:~$") and cmd not in line:
                output.append(line)
        return "\n".join(output)

    def close(self):
        self.ser.close()


@pytest.fixture(scope="module")
def hil():
    client = STM32HILClient(SERIAL_PORT, BAUDRATE)
    yield client
    client.close()


def test_01_read_hil_status(hil):
    """ทดสอบอ่านสถานะ JSON จาก STM32"""
    raw_output = hil.send_cmd("hil status")
    data = json.loads(raw_output)

    assert data["chip_id"] == "0x58", f"Chip ID mismatch: {data['chip_id']}"
    assert (
        70.0 <= data["pressure_kpa"] <= 150.0
    ), f"Pressure out of range: {data['pressure_kpa']}"


def test_02_set_manual_pressure(hil):
    """ทดสอบสั่งปรับค่าความดันคงที่ และตรวจสอบว่าค่าอัปเดตจริง"""
    hil.send_cmd("hil set_pressure 125.50")

    raw_output = hil.send_cmd("hil status")
    data = json.loads(raw_output)

    assert abs(data["pressure_kpa"] - 125.50) < 0.1, "Pressure set value mismatch"
    assert data["auto"] is False, "Auto simulation should be disabled"


def test_03_i2c_loopback_self_test(hil):
    """
    ทดสอบ I2C Master-to-Slave Loopback บนบอร์ด STM32
    (เมื่อต่อสายจิ้ม SCL/SDA ของ I2C1 เข้ากับ I2C2)
    """
    raw_output = hil.send_cmd("hil loopback")
    data = json.loads(raw_output)

    assert data["loopback"] == "PASS", f"I2C Loopback test failed: {data}"
    assert data["read_chip_id"] == "0x58"
