"""
tests/conftest.py
การตั้งค่าส่วนกลางของ Pytest สำหรับระบบ HIL Testbench
รองรับการส่งออกรายงานผลการทดสอบในรูปแบบ CSV (CSV Test Reporting & Telemetry)
"""

import os
import csv
import json
from datetime import datetime
import pytest


def pytest_addoption(parser):
    """เพิ่ม command-line option สำหรับกำหนด path ของไฟล์รายงานผล CSV"""
    group = parser.getgroup("csv report", "CSV test report generation")
    group.addoption(
        "--csv",
        action="store",
        default="reports/test_results.csv",
        help="Path สำหรับสร้างรายงานผลการทดสอบแบบ CSV (ค่าเริ่มต้น: reports/test_results.csv)",
    )


# เก็บข้อมูลผลการทดสอบทั้งหมดของ session
_test_records = {}


@pytest.fixture
def csv_record(request):
    """
    Fixture สำหรับให้แต่ละ Test Case สามารถแนบข้อมูลผลลัพธ์ (Telemetry / Measurements)
    ลงในรายงานผลแบบ CSV ได้โดยตรง
    """
    def _record(data: dict):
        if not hasattr(request.node, "_csv_telemetry"):
            request.node._csv_telemetry = {}
        if isinstance(data, dict):
            request.node._csv_telemetry.update(data)
        else:
            request.node._csv_telemetry["info"] = str(data)

    return _record


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook ดักจับสถานะของแต่ละขั้นตอนการทดสอบ (setup, call, teardown)"""
    outcome = yield
    report = outcome.get_result()

    nodeid = item.nodeid
    if nodeid not in _test_records:
        module_name = item.module.__name__ if item.module else os.path.basename(str(item.path))
        _test_records[nodeid] = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "suite": module_name,
            "test_name": item.name,
            "status": "UNKNOWN",
            "duration_sec": 0.0,
            "message": "",
            "item": item,
        }

    record = _test_records[nodeid]
    record["duration_sec"] += report.duration

    # ดักจับข้อความ error หรือ skip
    error_msg = ""
    if report.longrepr:
        if hasattr(report.longrepr, "reprcrash"):
            error_msg = str(report.longrepr.reprcrash.message)
        else:
            # ดึงเฉพาะบรรทัดแรกเพื่อให้อ่านง่ายในตาราง CSV
            lines = str(report.longrepr).strip().splitlines()
            error_msg = lines[-1] if lines else str(report.longrepr)
        error_msg = error_msg.replace("\n", " ").replace("\r", " ").strip()

    # ตรวจสอบสถานะตาม phase
    if report.when == "setup":
        if report.failed:
            record["status"] = "ERROR"
            record["message"] = error_msg
        elif report.skipped:
            record["status"] = "SKIPPED"
            # หาข้อความ skip จาก wasxfail หรือ longrepr
            skip_msg = getattr(report, "wasxfail", "")
            if not skip_msg and isinstance(report.longrepr, tuple) and len(report.longrepr) >= 3:
                skip_msg = report.longrepr[2]
            record["message"] = str(skip_msg or error_msg).replace("\n", " ").strip()

    elif report.when == "call":
        if report.passed:
            record["status"] = "PASSED"
        elif report.failed:
            record["status"] = "FAILED"
            record["message"] = error_msg
        elif report.skipped:
            record["status"] = "SKIPPED"
            record["message"] = error_msg

    elif report.when == "teardown":
        if report.failed and record["status"] == "PASSED":
            record["status"] = "ERROR"
            record["message"] = f"Teardown failed: {error_msg}"


def pytest_sessionfinish(session, exitstatus):
    """เมื่อรัน Test Suite เสร็จสิ้น ทำการเขียนข้อมูลทั้งหมดลงไฟล์ CSV"""
    csv_option = session.config.getoption("--csv", default="reports/test_results.csv")
    if not csv_option or csv_option.strip().lower() in ("none", "false", "0"):
        return

    csv_path = os.path.abspath(csv_option)
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    fieldnames = [
        "timestamp",
        "suite",
        "test_name",
        "status",
        "duration_sec",
        "message",
        "telemetry_data",
    ]

    rows = []
    for nodeid, record in _test_records.items():
        item = record.get("item")
        telemetry = {}
        if item and hasattr(item, "_csv_telemetry"):
            telemetry = item._csv_telemetry

        rows.append({
            "timestamp": record["timestamp"],
            "suite": record["suite"],
            "test_name": record["test_name"],
            "status": record["status"],
            "duration_sec": f"{record['duration_sec']:.4f}",
            "message": record["message"],
            "telemetry_data": json.dumps(telemetry, ensure_ascii=False) if telemetry else "",
        })

    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n[HIL CSV Report] Saved {len(rows)} test results to: {csv_path}")
