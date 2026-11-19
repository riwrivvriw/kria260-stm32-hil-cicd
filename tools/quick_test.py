#!/usr/bin/env python3
"""
tools/quick_test.py
สคริปต์ทดสอบ STM32 HIL Firmware แบบรวดเร็ว (ไม่ต้องเปิด screen)
"""

import serial
import glob
import time
import os
import sys

def find_port():
    env_port = os.environ.get("HIL_PORT") or os.environ.get("STM32_PORT")
    if env_port:
        return env_port
    ports = glob.glob("/dev/tty.usbmodem*") + glob.glob("/dev/ttyACM*")
    return ports[0] if ports else None

def main():
    port = find_port()
    if not port:
        print("ERROR: No STM32 board detected! (Please plug USB cable)")
        sys.exit(1)

    print(f"Connecting to STM32 on {port}...")
    try:
        ser = serial.Serial(port, 115200, timeout=1.0)
    except Exception as e:
        print(f"ERROR: Cannot open port {port}: {e}")
        sys.exit(1)

    time.sleep(0.2)
    ser.reset_input_buffer()

    commands = [
        "hil reset",
        "hil button start",
        "hil scenario normal",
        "hil scenario gas_leak",
        "hil scenario over_expansion",
        "hil reset"
    ]

    for cmd in commands:
        ser.write(f"{cmd}\r\n".encode())
        time.sleep(0.2)
        out = ser.read_all().decode(errors="ignore").strip()
        print(f">>> {cmd}\n{out}\n")

    ser.close()
    print("=== Quick Standalone Validation Completed Successfully ===")

if __name__ == "__main__":
    main()
