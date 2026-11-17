"""
test_hil_stm32.py
ชุดทดสอบ Pytest บน Host Laptop ควบคุมและตรวจสอบความถูกต้องของ STM32 HIL Firmware
ครอบคลุมการทดสอบ UART Testbench APIs, Finite State Machine (GI & Camera Mock),
การจำลองความดัน (I2C), สัญญาณเสียงลมรั่ว (AC Audio), และคำสั่ง Control IOs
"""

import pytest
import serial
import json
import time
import re
import glob
import os
import sys


def find_stm32_port():
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
            # ตรวจจับ ST-Link / STMicroelectronics / Nucleo
            if any(k in desc or k in mfg or k in hwid for k in ("stlink", "st-link", "stm", "stmicroelectronics", "nucleo")):
                return p.device
            if "usbmodem" in p.device.lower() or "ttyacm" in p.device.lower():
                return p.device
    except Exception:
        pass

    # 3. Fallback ผ่าน glob สำหรับ macOS / Linux
    ports = glob.glob("/dev/tty.usbmodem*") + glob.glob("/dev/ttyACM*")
    if ports:
        return sorted(ports)[0]

    return None


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
    if not port:
        pytest.skip("ไม่พบพอร์ต STM32 ST-Link/Nucleo เชื่อมต่ออยู่บนเครื่อง (กรุณาเสียบสาย USB หรือตั้งค่า HIL_PORT)")

    try:
        client = STM32HILClient(port, BAUDRATE)
    except Exception as e:
        pytest.skip(f"ไม่สามารถเชื่อมต่อ STM32 ผ่าน {port} ได้: {e}")

    # ตรวจสอบการตอบสนอง
    try:
        client.send_cmd("hil reset")
    except Exception as e:
        pytest.skip(f"STM32 ไม่ตอบสนองต่อคำสั่งบน {port}: {e}")

    yield client
    try:
        client.send_cmd("hil reset")
        client.close()
    except Exception:
        pass


def test_01_read_hil_status(hil, csv_record):
    """ทดสอบอ่านสถานะ JSON จาก STM32 และตรวจสอบ Schema ครบถ้วน"""
    data = hil.send_cmd_json("hil status")

    # บันทึกข้อมูล Telemetry ลงในรายงานผล CSV
    csv_record({
        "chip_id": data.get("chip_id"),
        "state": data.get("state"),
        "pressure_kpa": data.get("pressure_kpa"),
        "pump_duty": data.get("pump_duty", 0.0),
        "leak": data.get("leak"),
        "camera_scene": data.get("camera_scene"),
    })

    assert data["chip_id"] == "0x58", f"Chip ID mismatch: {data['chip_id']}"
    assert "state" in data, "FSM state missing from status JSON"
    assert "camera_scene" in data, "Camera scene missing from status JSON"
    assert (
        70.0 <= data["pressure_kpa"] <= 150.0
    ), f"Pressure out of range: {data['pressure_kpa']}"


def test_02_set_manual_pressure(hil, csv_record):
    """ทดสอบสั่งปรับค่าความดันคงที่ ตรวจสอบว่าค่าอัปเดตจริง และบันทึกลง CSV"""
    hil.send_cmd("hil set_pressure 128.50")

    data = hil.send_cmd_json("hil status")

    csv_record({
        "target_pressure": 128.50,
        "measured_pressure_kpa": data.get("pressure_kpa"),
        "auto": data.get("auto"),
    })

    assert (
        abs(data["pressure_kpa"] - 128.50) < 0.2
    ), f"Pressure set value mismatch: {data['pressure_kpa']}"
    assert data["auto"] is False, "Auto simulation should be disabled after manual set"


def test_03_state_machine_transitions(hil, csv_record):
    """ทดสอบการเปลี่ยนสถานะ State Machine ผ่านคำสั่ง API (hil set_state)"""
    # 1. ทดสอบเปลี่ยนเป็น INSUFFLATE
    hil.send_cmd("hil set_state INSUFFLATE")
    data_insuf = hil.send_cmd_json("hil status")
    assert data_insuf["state"] == "INSUFFLATION"
    assert data_insuf["camera_scene"] == "LUMEN_EXPANDING_INSUFFLATION"

    # 2. ทดสอบเปลี่ยนเป็น INSPECT
    hil.send_cmd("hil set_state INSPECT")
    data_insp = hil.send_cmd_json("hil status")
    assert data_insp["state"] == "STABLE_INSPECTION"
    assert data_insp["camera_scene"] == "MUCOSAL_INSPECTION_POLYP_ACTIVE"

    # 3. ทดสอบเปลี่ยนกลับสู่ IDLE
    hil.send_cmd("hil set_state IDLE")
    data_idle = hil.send_cmd_json("hil status")
    assert data_idle["state"] == "IDLE"

    csv_record({
        "fsm_check": "INSUFFLATE -> INSPECT -> IDLE Passed",
        "last_camera_scene": data_idle["camera_scene"]
    })


def test_04_leak_injection_and_audio(hil, csv_record):
    """ทดสอบการฉีดลมรั่ว และตรวจสอบว่าสถานะเสียง AC Audio Leak เปิดทำงานพร้อมกัน"""
    # สั่ง Inject Leak
    hil.send_cmd("hil inject_leak 1")
    data = hil.send_cmd_json("hil status")

    csv_record({
        "leak_state": data.get("leak"),
        "audio_active": data.get("audio_active"),
        "state_after_leak": data.get("state")
    })

    assert data["leak"] is True, "Leak should be active"
    assert data["audio_active"] is True, "AC Audio leak must be active when leak occurs"
    assert data["state"] == "LEAK_EVENT", f"State should be LEAK_EVENT, got: {data['state']}"

    # เคลียร์ลมรั่ว
    hil.send_cmd("hil inject_leak 0")
    data_cleared = hil.send_cmd_json("hil status")
    assert data_cleared["leak"] is False


def test_05_mock_control_ios(hil, csv_record):
    """ทดสอบจำลองสัญญาณ IO (Start/Stop, E-Stop, Solenoid Valve)"""
    # 1. ทดสอบ Start IO
    hil.send_cmd("hil set_start_stop 1")
    data = hil.send_cmd_json("hil status")
    assert data["start_stop_io"] is True

    # 2. ทดสอบ Solenoid Purge Valve
    hil.send_cmd("hil set_solenoid 1")
    data = hil.send_cmd_json("hil status")
    assert data["valve_open"] is True

    # 3. ทดสอบ Emergency Stop IO
    hil.send_cmd("hil set_estop 1")
    data_estop = hil.send_cmd_json("hil status")
    assert data_estop["estop"] is True
    assert data_estop["state"] == "EMERGENCY_STOP"

    # รีเซ็ตระบบ
    hil.send_cmd("hil reset")
    data_reset = hil.send_cmd_json("hil status")
    assert data_reset["state"] == "IDLE"
    assert data_reset["estop"] is False

    csv_record({"io_tests": "Start/Stop, Solenoid, and E-Stop verified"})


@pytest.mark.skip(
    reason="รอต่อสาย I2C เข้ากับบอร์ด Kria KR260 (ฮาร์ดแวร์บอร์ด Nucleo ไม่มีตัวต้านทาน Pull-up บนสายสัญญาณ)"
)
def test_06_i2c_loopback_self_test(hil, csv_record):
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
