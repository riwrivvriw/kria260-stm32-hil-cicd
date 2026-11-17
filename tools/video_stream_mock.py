#!/usr/bin/env python3
"""
tools/video_stream_mock.py
โมดูลสร้างและสตรีมวิดีโอกล้องส่องตรวจจำลอง (Mock Camera Inside GI)
สตรีมภาพวิดีโอผ่านสาย Ethernet LAN (GStreamer UDP/RTP) พร้อมกับข้อมูลเซนเซอร์แบบ Real-Time

สอดคล้องกับ Finite State Machine บน STM32:
- IDLE: ภาพ Standby ก่อนเริ่มการส่องตรวจ
- INSUFFLATION: โพรงกระเพาะค่อยๆ ขยายตัวตามแรงดันก๊าซ dP/dt
- STABLE_INSPECTION: โพรงกระเพาะคงที่ แสดงเยื่อบุทางเดินอาหารและรอยโรค (Polyp) สำหรับ Vitis AI
- LEAK_EVENT: โพรงกระเพาะยุบตัว มีฟองอากาศและแจ้งเตือนการรั่ว (ตรงกับเสียง AC Leak Audio)
- DEFLATION_STOP: ระบายก๊าซออก ถอยหัวกล้อง
- EMERGENCY_STOP: หน้าจอหยุดฉุกเฉิน E-Stop Alert
"""

import sys
import time
import math
import json
import argparse
import subprocess
import numpy as np

# ลอง import cv2 หากมีติดตั้งในเครื่อง
try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False


class GIMockCameraStreamer:
    def __init__(self, target_ip: str = "192.168.1.120", target_port: int = 5000,
                 width: int = 640, height: int = 480, fps: int = 30):
        self.target_ip = target_ip
        self.target_port = target_port
        self.width = width
        self.height = height
        self.fps = fps
        self.current_state = "IDLE"
        self.pressure_kpa = 101.3
        self.pump_duty = 0.0
        self.frame_idx = 0
        self.gst_process = None

    def start_pipeline(self):
        """เปิด GStreamer Pipeline เพื่อสตรีมวิดีโอ H.264 RTP ผ่าน UDP ไปยัง KR260"""
        cmd = [
            "gst-launch-1.0", "-q",
            "fdsrc", "!",
            f"video/x-raw,format=BGR,width={self.width},height={self.height},framerate={self.fps}/1", "!",
            "videoconvert", "!",
            "x264enc", "tune=zerolatency", "bitrate=1500", "speed-preset=ultrafast", "!",
            "rtph264pay", "!",
            "udpsink", f"host={self.target_ip}", f"port={self.target_port}"
        ]
        try:
            self.gst_process = subprocess.Popen(cmd, stdin=subprocess.PIPE)
            print(f"[*] GStreamer pipeline started -> {self.target_ip}:{self.target_port}")
        except FileNotFoundError:
            print("[!] Warning: gst-launch-1.0 not found on Host. Running in offline/frame-generator mode.")
            self.gst_process = None

    def update_telemetry(self, state: str, pressure: float, duty: float):
        self.current_state = state
        self.pressure_kpa = pressure
        self.pump_duty = duty

    def generate_frame(self) -> np.ndarray:
        """สร้าง Frame ภาพจำลองกระเพาะอาหารตาม State ปัจจุบัน"""
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        cx, cy = self.width // 2, self.height // 2
        t = self.frame_idx * 0.05

        if self.current_state == "IDLE":
            # พื้นหลังเทาเข้ม หน้าจอ Standby
            frame[:] = (30, 30, 30)
            if HAS_OPENCV:
                cv2.putText(frame, "GI ENDOSCOPY SYSTEM - STANDBY", (cx - 190, cy - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
                cv2.putText(frame, "Waiting for Insufflation Start IO...", (cx - 160, cy + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)

        elif self.current_state == "INSUFFLATION":
            # จำลองโพรงสีชมพูเข้มกำลังขยายตัวตามความดัน
            expansion = min(1.0, max(0.2, (self.pressure_kpa - 101.3) / 25.0))
            radius = int(80 + expansion * 120 + 3 * math.sin(t * 5))
            if HAS_OPENCV:
                # วาดเนื้อเยื่อกระเพาะ
                cv2.circle(frame, (cx, cy), radius + 40, (40, 30, 120), -1)
                cv2.circle(frame, (cx, cy), radius, (60, 50, 180), -1)
                cv2.circle(frame, (cx, cy), radius // 2, (30, 20, 80), -1)
                cv2.putText(frame, "INSUFFLATING CAVITY...", (40, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        elif self.current_state == "STABLE_INSPECTION":
            # โพรงเปิดเต็มที่ เห็นเยื่อบุชัดเจน และมี Polyp จำลองสำหรับ AI ตรวจจับ
            radius = int(200 + 2 * math.sin(t * 2))
            if HAS_OPENCV:
                cv2.circle(frame, (cx, cy), radius, (70, 60, 200), -1)
                # วาดติ่งเนื้อ Polyp จำลอง (พิกัด x=380, y=200)
                polyp_x = int(cx + 80 + 5 * math.sin(t))
                polyp_y = int(cy - 60 + 5 * math.cos(t))
                cv2.circle(frame, (polyp_x, polyp_y), 24, (90, 80, 240), -1)
                cv2.circle(frame, (polyp_x, polyp_y), 12, (120, 100, 255), -1)
                cv2.putText(frame, "STABLE INSPECTION (AI SCANNING)", (40, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        elif self.current_state == "LEAK_EVENT":
            # ความดันตก โพรงยุบตัว และมีฟองอากาศสั่นไหว
            radius = int(100 + 15 * math.sin(t * 10))
            if HAS_OPENCV:
                cv2.circle(frame, (cx, cy), radius, (50, 40, 150), -1)
                # วาดฟองก๊าซรั่ว
                for i in range(5):
                    bx = int(cx + 40 * math.cos(t * 3 + i))
                    by = int(cy + 40 * math.sin(t * 4 + i))
                    cv2.circle(frame, (bx, by), 8 + i * 2, (220, 220, 255), 1)
                # กรอบเตือนภัยสีแดง
                cv2.rectangle(frame, (10, 10), (self.width - 10, self.height - 10), (0, 0, 255), 4)
                cv2.putText(frame, "! GAS LEAK DETECTED (AC AUDIO ON) !", (40, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        elif self.current_state == "EMERGENCY_STOP":
            frame[:] = (0, 0, 120)
            if HAS_OPENCV:
                cv2.putText(frame, "EMERGENCY STOP ACTIVE", (cx - 180, cy),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 3)

        # ข้อมูล OSD Telemetry Overlay ด้านล่าง
        if HAS_OPENCV:
            osd = f"P: {self.pressure_kpa:.2f} kPa | Pump: {self.pump_duty*100:.1f}% | State: {self.current_state}"
            cv2.putText(frame, osd, (30, self.height - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)

        self.frame_idx += 1
        return frame

    def send_frame(self, frame: np.ndarray):
        if self.gst_process and self.gst_process.stdin:
            try:
                self.gst_process.stdin.write(frame.tobytes())
            except Exception:
                pass

    def stop(self):
        if self.gst_process:
            self.gst_process.stdin.close()
            self.gst_process.terminate()


def main():
    parser = argparse.ArgumentParser(description="GI Mock Camera Ethernet Streamer")
    parser.add_argument("--ip", default="192.168.1.120", help="Target KR260 IP")
    parser.add_argument("--port", type=int, default=5000, help="Target UDP port")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second")
    args = parser.parse_args()

    streamer = GIMockCameraStreamer(target_ip=args.ip, target_port=args.port, fps=args.fps)
    streamer.start_pipeline()

    print("[*] Streaming GI mock camera frames. Press Ctrl+C to stop.")
    states = ["IDLE", "INSUFFLATION", "STABLE_INSPECTION", "LEAK_EVENT", "INSUFFLATION", "DEFLATION_STOP"]
    state_idx = 0
    p = 101.3

    try:
        while True:
            # จำลอง State หมุนเวียนเพื่อทดสอบ
            current_s = states[(streamer.frame_idx // (30 * 4)) % len(states)]
            if current_s == "INSUFFLATION":
                p = min(125.0, p + 0.3)
            elif current_s == "LEAK_EVENT":
                p = max(103.0, p - 0.5)
            elif current_s == "DEFLATION_STOP":
                p = max(101.3, p - 0.8)

            streamer.update_telemetry(current_s, p, 0.6 if current_s == "INSUFFLATION" else 0.2)
            frame = streamer.generate_frame()
            streamer.send_frame(frame)
            time.sleep(1.0 / args.fps)
    except KeyboardInterrupt:
        print("\nStopping stream...")
    finally:
        streamer.stop()


if __name__ == "__main__":
    main()
