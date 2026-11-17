# คู่มือระบบสตรีมวิดีโอเสมือนซิงค์ข้อมูลผ่านสายแลน (Virtual Video Stream & Sensor Sync)

เอกสารฉบับนี้อธิบายหลักการทำงานของระบบสร้างและส่งสัญญาณวิดีโอกล้องเอนโดสโคปจำลอง (Synthetic Endoscopy Video) จาก Host Laptop ไปยังบอร์ด Kria KR260 ผ่านสายแลน Ethernet (UDP/RTP H.264) ควบคู่ไปกับการซิงโครไนซ์ข้อมูลเซนเซอร์แบบเรียลไทม์

---

## 1. หลักการทำงานภายใน (Internal Architecture)

ในการทดสอบระบบเครื่องมือแพทย์ HIL การทดสอบเซนเซอร์วัดแรงดันและปั๊มลมเพียงอย่างเดียวยังไม่เพียงพอ อัลกอริทึม AI บน KR260 (Vitis AI) ต้องการภาพวิดีโอจากกล้องเอนโดสโคปเพื่อตรวจหาพยาธิสภาพ (Polyp Detection) และประเมินความนิ่งของโพรงทางเดินอาหาร

```
+-----------------------------------------------------------------------------------+
|                        HOST LAPTOP / CI TESTBENCH SERVER                          |
|                                                                                   |
|  [tools/video_stream_mock.py]                                                     |
|  1. Synthetic Endoscopy Visual Generator:                                         |
|     - วาดโพรงทางเดินอาหาร (GI Lumen & Mucosal Wall Textures)                     |
|     - เปลี่ยนทัศนียภาพตาม State Machine และความดันแบบเรียลไทม์                   |
|  2. Real-time OSD Overlay:                                                        |
|     - แสดงข้อมูล Pressure (kPa), Pump Duty (%), FSM State, Leak Warning          |
|  3. Video Compression & RTP Streaming:                                            |
|     - H.264 Hardware/Software Encoder                                            |
|     - สตรีมออกผ่านท่อ UDP/RTP ไปยังพอร์ต 5000 ทางสายแลน Ethernet                   |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          | Ethernet Cable (UDP/RTP H.264 Port 5000)
                                          v
+-----------------------------------------------------------------------------------+
|                            TARGET UNDER TEST: KRIA KR260                          |
|                                                                                   |
|  1. Network Receiver:                                                             |
|     - GStreamer Receiver Pipeline รับ RTP H.264 Packet จากพอร์ต 5000              |
|  2. Virtual V4L2 Device Node:                                                     |
|     - ดีโค้ดและส่งภาพเข้า /dev/video10 (v4l2loopback Virtual Camera)             |
|  3. Vitis AI / Computer Vision Application:                                       |
|     - แอพพลิเคชันบน KR260 เปิดอ่าน /dev/video10 เสมือนต่อกล้องจริง                |
+-----------------------------------------------------------------------------------+
```

---

### 1.1 การปรับเปลี่ยนภาพตาม Finite State Machine

เอนจิน [tools/video_stream_mock.py](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/tools/video_stream_mock.py) จะเปลี่ยนคุณลักษณะของภาพตามสถานะการทำงาน:

| สถานะ (GI State) | พฤติกรรมของภาพวิดีโอ (Visual Behavior) | ทัศนียภาพจำลอง |
|---|---|---|
| **`IDLE`** | โพรงแฟบสนิท (Collapsed Lumen) มืดสลัว แสงสว่างต่ำ | ก่อนเริ่มกระบวนการส่องกล้อง |
| **`INSUFFLATION`** | รัศมีโพรงขยายตัวกว้างขึ้นตามแรงดัน ($dP/dt$) มีคลื่นการเคลื่อนที่ช้าๆ | กำลังอัดก๊าซขยายกระเพาะอาหาร |
| **`STABLE_INSPECTION`** | โพรงเปิดเต็มที่ นิ่ง เสถียร ลวดลายผนังเยื่อบุ (Mucosa) คมชัด | สภาพแวดล้อมที่เหมาะสมที่สุดสำหรับ AI Vision |
| **`LEAK_EVENT`** | โพรงเริ่มยุบตัว มีการสั่นไหวของภาพ (Camera Jitter) และมีละอองก๊าซ/ไอหมอกรบกวน | เกิดลมรั่ว ความดันตก พร้อมเสียงหวีด |
| **`DEFLATION_STOP`** | โพรงยุบตัวลงอย่างต่อเนื่อง ความสว่างค่อยๆ หรี่ลง | กำลังเปิดวาล์วระบายก๊าซทิ้ง |
| **`EMERGENCY_STOP`** | กระพริบขอบจอสีแดงเตือน (Red Border Warning) และแสดงข้อความ Safety Lock | ระบบหยุดฉุกเฉินระดับฮาร์ดแวร์ |

---

### 1.2 แถบแสดงข้อมูลแบบเรียลไทม์ (Dynamic On-Screen Display: OSD)

ทุกเฟรมภาพวิดีโอจะถูกวาดทับด้วยข้อมูล Telemetry จาก STM32:
* **Header Bar:** แสดงชื่อระบบ `[GI Endoscopy HIL Mock Video]`
* **State Pill:** ป้ายสถานะปัจจุบันพร้อมสีระบุระดับความปลอดภัย (เขียว = INSPECT, เหลือง = INSUFFLATE, ส้ม = LEAK, แดง = ESTOP)
* **Live Telemetry:** ค่าความดันปัจจุบัน `Press: 120.45 kPa (Target: 120.00 kPa)`
* **Actuator Info:** `Pump Duty: 45.2% | Vent Valve: CLOSED`
* **Audio Indicator:** `Audio Leak: ACTIVE (3 kHz Sine)` เมื่อมีรอยรั่ว

---

## 2. ขั้นตอนการเปิดใช้งานและรันสตรีมวิดีโอ (How to Run)

### 2.1 ขั้นตอนบน Kria KR260 (ตัวรับภาพ - Video Receiver)

#### 1. โหลดโมดูล Virtual Camera (`v4l2loopback`)
```bash
# ตรวจสอบหรือโหลดโมดูล v4l2loopback กำหนดให้เป็น /dev/video10
sudo modprobe v4l2loopback devices=1 video_nr=10 card_label="GI_Virtual_Cam" exclusive_caps=1
```

#### 2. เปิด GStreamer Pipeline รอรับสัญญาณวิดีโอจากพอร์ต UDP 5000
```bash
gst-launch-1.0 -v udpsrc port=5000 caps="application/x-rtp, media=video, encoding-name=H264" ! \
  rtph264depay ! \
  h264parse ! \
  avdec_h264 ! \
  videoconvert ! \
  video/x-raw,format=YUY2 ! \
  v4l2sink device=/dev/video10
```
*ระบบจะเปิด Device Node `/dev/video10` รอรับข้อมูลเฟรมภาพและพร้อมให้อัลกอริทึม AI เปิดอ่าน*

---

### 2.2 ขั้นตอนบน Host Laptop (ตัวส่งภาพ - Video Sender)

รันสคริปต์ [tools/video_stream_mock.py](file:///c:/Users/th62034660/Desktop/kria260-stm32-hil-cicd/tools/video_stream_mock.py) ผ่าน Python:

#### วิธีที่ 1: สตรีมไปยัง KR260 ข้ามระบบเครือข่ายแลน
```bash
# กำหนด IP ของ KR260 (เช่น 192.168.1.120)
python tools/video_stream_mock.py --target-ip 192.168.1.120 --port 5000 --fps 30 --state STABLE_INSPECTION --pressure 120.0
```

#### วิธีที่ 2: สตรีมและแสดงผลพรีวิวบนหน้าจอคอมพิวเตอร์พร้อมกัน
```bash
python tools/video_stream_mock.py --target-ip 192.168.1.120 --port 5000 --show-preview
```

#### วิธีที่ 3: จำลองสถานะลมรั่ว (Leak Event)
```bash
python tools/video_stream_mock.py --target-ip 192.168.1.120 --state LEAK_EVENT --pressure 95.0 --leak
```

---

### 2.3 การตรวจสอบความถูกต้องบน KR260

เปิด Terminal อีกหน้าต่างหนึ่งบน KR260 เพื่อทดสอบว่ากล้องเสมือนได้รับภาพหรือไม่:

```bash
# ตรวจสอบการรองรับของอุปกรณ์กล้องเสมือน
v4l2-ctl --device=/dev/video10 --all

# หรือเขียนสคริปต์ Python สั้นๆ เพื่ออ่าน Frame จาก OpenCV บน KR260
python3 -c "
import cv2
cap = cv2.VideoCapture(10)
ret, frame = cap.read()
if ret:
    print('SUCCESS: Captured frame size:', frame.shape)
else:
    print('ERROR: Cannot capture frame')
cap.release()
"
```
*หากได้ค่า `SUCCESS: Captured frame size: (480, 640, 3)` แสดงว่าระบบสตรีมวิดีโอสมบูรณ์ 100%*
