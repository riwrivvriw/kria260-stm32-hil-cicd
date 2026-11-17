"""
tests/conftest.py
การตั้งค่าส่วนกลางของ Pytest สำหรับระบบ HIL Testbench
(ใช้สำหรับแชร์ Fixtures และการตั้งค่าระหว่าง Test Suites)
"""

import pytest

# หมายเหตุ: Pytest รองรับการส่งออกรายงาน JUnit XML ไปยัง Azure DevOps แบบ Native Built-in
# ผ่านคำสั่ง: pytest tests/ --junitxml=reports/test_results.xml
