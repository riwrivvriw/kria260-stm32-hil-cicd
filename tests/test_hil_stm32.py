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
            time.sleep(0.04)
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
                time.sleep(0.02)
                continue

            if not raw_line:
                continue

            clean_line = ANSI_REGEX.sub('', raw_line).strip()
            if not clean_line or clean_line == cmd:
                continue

            lines.append(clean_line)

            # ตรวจสอบว่าได้รับผลลัพธ์ของคำสั่ง (JSON หรือ OK/Error/FAIL) แล้วจึงปิดท้ายเมื่อพบ Prompt
            has_response = any("{" in l or "OK" in l or "Error" in l or "FAIL" in l or "Usage" in l for l in lines)
            if has_response and ("hil:~$" in clean_line or "}" in clean_line):
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
    try:
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
    finally:
        hil.send_cmd("hil reset")


def test_03_state_machine_transitions(hil, csv_record):
    """ทดสอบการเปลี่ยนสถานะ State Machine ผ่านคำสั่ง API (hil set_state) เมื่อแพทย์เริ่มการตรวจ (Start=1)"""
    hil.send_cmd("hil reset")
    # 0. แพทย์กดปุ่ม Start เพื่อเข้าสู่กระบวนการตรวจก่อน
    hil.send_cmd("hil button start")

    try:
        # 1. ทดสอบเปลี่ยนเป็น INSUFFLATE (ที่ความดันบรรยากาศ เริ่มสูบลมขยายโพรง)
        hil.send_cmd("hil set_state INSUFFLATE")
        data_insuf = hil.send_cmd_json("hil status")
        assert data_insuf["state"] == "INSUFFLATION"
        assert data_insuf["camera_scene"] == "LUMEN_EXPANDING_INSUFFLATION"

        # 2. ความดันถึงเป้าหมายการตรวจ (125 kPa) ก่อนเข้าสู่โหมดส่องตรวจคงที่ (INSPECT)
        # หากความดันต่ำกว่า 117 kPa ตัว FSM จะตัดกลับไปเร่งปั๊ม (INSUFFLATION) อัตโนมัติเพื่อความปลอดภัย
        hil.send_cmd("hil set_pressure 125.00")
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
    finally:
        hil.send_cmd("hil reset")


def test_03b_safety_interlock_when_stopped(hil, csv_record):
    """
    ทดสอบระบบนิรภัย (Safety Interlock):
    หากแพทย์ยังไม่ได้กด Start (Start = 0) และไม่มีการปั๊มลม
    ระบบจะต้องไม่อนุญาตให้อัดลม (ห้ามเป็น INSUFFLATION) และต้องตัดไประบายลม (DEFLATION_STOP หรือ IDLE เมื่อระบายหมดแล้ว)
    """
    hil.send_cmd("hil reset")
    hil.send_cmd("hil set_state INSUFFLATE")
    data = hil.send_cmd_json("hil status")
    assert data["state"] in ("DEFLATION_STOP", "IDLE"), (
        f"Safety Interlock Violated: System allowed INSUFFLATION when start=0! (State: {data['state']})"
    )
    assert data["state"] != "INSUFFLATION"
    csv_record({"safety_interlock_stop_rule": "PASSED", "safe_state": data["state"]})


def test_04_leak_injection_and_audio(hil, csv_record):
    """ทดสอบการฉีดลมรั่ว และตรวจสอบว่าสถานะเสียง AC Audio Leak เปิดทำงานพร้อมกัน"""
    # แพทย์เริ่มตรวจก่อน จากนั้นเกิดเหตุลมรั่ว
    hil.send_cmd("hil button start")

    try:
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
    finally:
        hil.send_cmd("hil reset")


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


# @pytest.mark.skip(
#     reason="รอต่อสาย I2C เข้ากับบอร์ด Kria KR260 (ฮาร์ดแวร์บอร์ด Nucleo ไม่มีตัวต้านทาน Pull-up บนสายสัญญาณ)"
# )
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


def test_07_test_interfaces(hil, csv_record):
    """ทดสอบคำสั่ง hil test_interfaces ตรวจสอบสถานะ Loopback ทุก Interface พร้อมกัน"""
    data = hil.send_cmd_json("hil test_interfaces")
    csv_record(data)

    assert "interface_loopback_test" in data, "interface_loopback_test key missing in response"
    diag = data["interface_loopback_test"]
    assert diag.get("status") == "READY", f"Interfaces not READY: {diag}"
    assert "io_lines" in diag, "io_lines missing from diagnostics"
    assert "pwm_capture" in diag, "pwm_capture missing from diagnostics"
    assert "i2s_audio_leak" in diag or "dac_audio_leak" in diag, "audio_leak missing from diagnostics"


def test_08_mock_doctor_button(hil, csv_record):
    """ทดสอบคำสั่ง hil button จำลองปุ่มกดของแพทย์ (Start/Stop) ส่งไปยัง KR260"""
    # 1. จำลองแพทย์กดปุ่ม START เพื่อเริ่มระบบ PID & AI
    res_start = hil.send_cmd("hil button start")
    assert "OK" in res_start or "START" in res_start
    data = hil.send_cmd_json("hil status")
    assert data["start_stop_io"] is True

    # 2. จำลองแพทย์กดปุ่ม STOP เพื่อหยุดระบบเมื่อตรวจเสร็จ
    res_stop = hil.send_cmd("hil button stop")
    assert "OK" in res_stop or "STOP" in res_stop
    data_stop = hil.send_cmd_json("hil status")
    assert data_stop["start_stop_io"] is False

    csv_record({"doctor_button_test": "PASSED", "start_stop_cycle": "OK"})


def load_clinical_scenarios():
    scenarios_path = os.path.join(os.path.dirname(__file__), "clinical_scenarios.json")
    if os.path.exists(scenarios_path):
        with open(scenarios_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

CLINICAL_SCENARIOS = load_clinical_scenarios()


@pytest.mark.parametrize("sc", CLINICAL_SCENARIOS, ids=[s["id"] for s in CLINICAL_SCENARIOS])
def test_09_data_driven_clinical_scenarios(hil, csv_record, sc):
    """
    Data-Driven Test Case Loader & Multi-Step DSL Interpreter:
    โหลดและรัน Test Cases จากไฟล์ tests/clinical_scenarios.json โดยอัตโนมัติ
    รองรับทั้ง Single-Step Scenario ดั้งเดิม และ Multi-Step Sequence Actions
    ช่วยให้ทีมวิศวกรและแพทย์สามารถเพิ่มหรือแก้ไขเงื่อนไขการทดสอบผ่าน JSON ได้โดยไม่ต้องแตะโค้ด Python
    """
    try:
        if "steps" in sc and isinstance(sc["steps"], list):
            # -------------------------------------------------------------
            # โหมด 1: Multi-Step Sequential Actions (Timeline DSL)
            # -------------------------------------------------------------
            last_status = {}
            for idx, step in enumerate(sc["steps"]):
                step_name = step.get("step_name", f"Step_{idx+1}")
                cmd = step.get("command")
                if cmd:
                    res = hil.send_cmd(cmd)
                    assert "OK" in res or "START" in res or "STOP" in res, (
                        f"[{sc['id']} - {step_name}] Failed to execute command '{cmd}': {res}"
                    )

                wait_sec = step.get("wait_sec", 0.0)
                if wait_sec > 0:
                    time.sleep(wait_sec)

                # ดึงค่า Telemetry มาตรวจสอบหากมีการระบุเงื่อนไขใน 'expect'
                expect = step.get("expect")
                if expect:
                    last_status = hil.send_cmd_json("hil status")

                    if "state" in expect:
                        assert last_status["state"] == expect["state"], (
                            f"[{sc['id']} - {step_name}] State mismatch: "
                            f"expected {expect['state']}, got {last_status['state']}"
                        )
                    if "min_pressure" in expect:
                        assert last_status["pressure_kpa"] >= expect["min_pressure"], (
                            f"[{sc['id']} - {step_name}] Pressure too low: "
                            f"{last_status['pressure_kpa']} < {expect['min_pressure']}"
                        )
                    if "max_pressure" in expect:
                        assert last_status["pressure_kpa"] <= expect["max_pressure"], (
                            f"[{sc['id']} - {step_name}] Pressure too high: "
                            f"{last_status['pressure_kpa']} > {expect['max_pressure']}"
                        )
                    if "leak" in expect:
                        assert last_status["leak"] is expect["leak"], (
                            f"[{sc['id']} - {step_name}] Leak mismatch: "
                            f"expected {expect['leak']}, got {last_status['leak']}"
                        )
                    if "audio_active" in expect:
                        assert last_status["audio_active"] is expect["audio_active"], (
                            f"[{sc['id']} - {step_name}] Audio mismatch: "
                            f"expected {expect['audio_active']}, got {last_status['audio_active']}"
                        )
                    if "estop" in expect:
                        assert last_status["estop"] is expect["estop"], (
                            f"[{sc['id']} - {step_name}] Estop mismatch: "
                            f"expected {expect['estop']}, got {last_status['estop']}"
                        )
                    if "solenoid_valve" in expect or "solenoid" in expect:
                        exp_sol = expect.get("solenoid_valve", expect.get("solenoid"))
                        assert last_status["valve_open"] is exp_sol, (
                            f"[{sc['id']} - {step_name}] Solenoid valve mismatch: "
                            f"expected {exp_sol}, got {last_status['valve_open']}"
                        )
                    if "max_pump_duty" in expect:
                        assert last_status.get("pump_duty", 0.0) <= expect["max_pump_duty"], (
                            f"[{sc['id']} - {step_name}] Pump duty exceeded: "
                            f"{last_status.get('pump_duty')} > {expect['max_pump_duty']}"
                        )
                    if "min_pump_duty" in expect:
                        assert last_status.get("pump_duty", 0.0) >= expect["min_pump_duty"], (
                            f"[{sc['id']} - {step_name}] Pump duty below minimum: "
                            f"{last_status.get('pump_duty')} < {expect['min_pump_duty']}"
                        )
                    if "start_stop_io" in expect:
                        assert last_status.get("start_stop_io") is expect["start_stop_io"], (
                            f"[{sc['id']} - {step_name}] Start/Stop IO mismatch: "
                            f"expected {expect['start_stop_io']}, got {last_status.get('start_stop_io')}"
                        )

            # บันทึกผลลัพธ์ของ Multi-Step Scenario ลง CSV Report
            csv_record({
                "scenario_id": sc["id"],
                "scenario_name": sc["name"],
                "execution_type": "MULTI_STEP_DSL",
                "total_steps": len(sc["steps"]),
                "last_step_state": last_status.get("state"),
                "last_step_pressure": last_status.get("pressure_kpa"),
                "estop_active": last_status.get("estop"),
                "valve_open": last_status.get("valve_open"),
                "verdict": "PASSED"
            })

        else:
            # -------------------------------------------------------------
            # โหมด 2: Single-Step Scenario (Backward Compatibility)
            # -------------------------------------------------------------
            cmd = sc["scenario_cmd"]
            res = hil.send_cmd(cmd)
            assert "OK" in res, f"Failed to execute {cmd}: {res}"

            wait_sec = sc.get("wait_sec", 0.0)
            if wait_sec > 0:
                time.sleep(wait_sec)

            status = hil.send_cmd_json("hil status")

            if "expected_state" in sc:
                assert status["state"] == sc["expected_state"], (
                    f"State mismatch for {sc['id']}: expected {sc['expected_state']}, got {status['state']}"
                )

            pressure = status["pressure_kpa"]
            if "expected_min_pressure" in sc and "expected_max_pressure" in sc:
                min_p = sc["expected_min_pressure"]
                max_p = sc["expected_max_pressure"]
                assert min_p <= pressure <= max_p, (
                    f"Pressure out of range for {sc['id']}: {pressure} kPa (expected [{min_p}, {max_p}])"
                )

            if "expected_leak" in sc:
                assert status["leak"] is sc["expected_leak"], (
                    f"Leak flag mismatch for {sc['id']}: expected {sc['expected_leak']}, got {status['leak']}"
                )

            if "expected_audio" in sc:
                assert status["audio_active"] is sc["expected_audio"], (
                    f"Audio active mismatch for {sc['id']}: expected {sc['expected_audio']}, got {status['audio_active']}"
                )

            if "expected_estop" in sc:
                assert status["estop"] is sc["expected_estop"], (
                    f"Estop mismatch for {sc['id']}: expected {sc['expected_estop']}, got {status['estop']}"
                )

            if "expected_solenoid" in sc:
                assert status["valve_open"] is sc["expected_solenoid"], (
                    f"Solenoid mismatch for {sc['id']}: expected {sc['expected_solenoid']}, got {status['valve_open']}"
                )

            csv_record({
                "scenario_id": sc["id"],
                "scenario_name": sc["name"],
                "execution_type": "SINGLE_STEP",
                "tested_pressure": pressure,
                "tested_state": status["state"],
                "leak_active": status["leak"],
                "audio_active": status["audio_active"],
                "estop_active": status.get("estop"),
                "valve_open": status.get("valve_open"),
                "verdict": "PASSED"
            })

    finally:
        # รีเซ็ตระบบกลับสู่สถานะ IDLE เพื่อไม่ให้ส่งผลกระทบต่อ Scenario ถัดไป
        hil.send_cmd("hil reset")
        time.sleep(0.08)



