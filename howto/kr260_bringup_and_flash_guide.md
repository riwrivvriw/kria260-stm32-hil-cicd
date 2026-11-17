# คู่มือการ Bring-up บอร์ด Kria KR260 ด้วย PetaLinux และกลยุทธ์การ Flash ใน CI/CD

> **เอกสารคู่มือเชิงวิศวกรรมสำหรับโครงการ:** HIL Testbench & GI Detect System  
> **เนื้อหาครอบคลุม:** ตั้งแต่การเริ่มต้นออกแบบ Hardware ใน Vivado, การบิลด์ PetaLinux OS, จนถึงกลยุทธ์การ Flash อัตโนมัติจาก Self-hosted CI/CD Agent (เปรียบเทียบ PL vs PS vs Full Boot Image)

---

## สารบัญ
1. [แนวคิดพื้นฐานของ Kria KR260 (Kria SOM Architecture)](#1-แนวคิดพื้นฐานของ-kria-kr260)
2. [ขั้นตอนการ Bring-up บอร์ดด้วย PetaLinux (Step-by-Step)](#2-ขั้นตอนการ-bring-up-บอร์ดด้วย-petalinux)
   - [Step 1: ออกแบบฮาร์ดแวร์ใน Vivado และ Export XSA](#step-1-ออกแบบฮาร์ดแวร์ใน-vivado-และ-export-xsa)
   - [Step 2: สร้างและคอนฟิก PetaLinux Project](#step-2-สร้างและคอนฟิก-petalinux-project)
   - [Step 3: บิลด์และเตรียม Image สำหรับ MicroSD Card](#step-3-บิลด์และเตรียม-image-สำหรับ-microsd-card)
   - [Step 4: บูตเครื่องและทดสอบการทำงานเบื้องต้น](#step-4-บูตเครื่องและทดสอบการทำงานเบื้องต้น)
3. [กลยุทธ์การ Flash บอร์ด KR260 จาก Self-Hosted CI/CD Agent](#3-กลยุทธ์การ-flash-บอร์ด-kr260-จาก-self-hosted-cicd-agent)
   - [ตารางเปรียบเทียบ: Flash แค่ PL vs แค่ PS vs ทั้ง Boot Image](#ตารางเปรียบเทียบ-flash-แต่ละประเภท)
   - [กรณีที่ 1: Flash แค่ PL (FPGA Bitstream Hot-Reload ด้วย xmutil)](#กรณีที่-1-flash-แค่-pl-fpga-bitstream-hot-reload)
   - [กรณีที่ 2: Flash แค่ PS (Application / Linux Software Update)](#กรณีที่-2-flash-แค่-ps-application-software-update)
   - [กรณีที่ 3: Flash ทั้งระบบ (Full Boot Image via JTAG / TFTP Network Boot)](#กรณีที่-3-flash-ทั้งระบบ-full-boot-image)
4. [ตัวอย่างสคริปต์ CI/CD อัตโนมัติบน Azure DevOps](#4-ตัวอย่างสคริปต์-cicd-อัตโนมัติบน-azure-devops)

---

## 1. แนวคิดพื้นฐานของ Kria KR260

Kria KR260 แตกต่างจากบอร์ด Zynq / Zynq UltraScale+ ทั่วไปอย่างมีนัยสำคัญ:
* ตัวประมวลผลอยู่บน **SOM (System-on-Module: K26)** ซึ่งมีชิป Zynq UltraScale+ MPSoC (xck26), DDR4 4GB, และ QSPI Flash 512Mb
* บอร์ดด้านล่างคือ **Carrier Card (KR260)** ที่ดึงพอร์ตเชื่อมต่อออกมา (Ethernet 4 พอร์ต, DisplayPort, USB 3.0, PMOD, Raspberry Pi Header)
* **Kria App Architecture:** AMD/Xilinx ออกแบบให้ KR260 รองรับ **FPGA Dynamic Overlays** หมายความว่าเราไม่จำเป็นต้องปิดเครื่องหรือรีบูต Linux เพื่อเปลี่ยน Bitstream ของ PL แต่สามารถสลับฮาร์ดแวร์บน FPGA สดๆ ได้ผ่านคำสั่ง `xmutil`

---

## 2. ขั้นตอนการ Bring-up บอร์ดด้วย PetaLinux

### สรุป Workflow ภาพรวม:
```
[Vivado: Block Design] ➔ [Export .xsa] ➔ [PetaLinux Config & Build] ➔ [Flash MicroSD] ➔ [Boot KR260]
```

---

### Step 1: ออกแบบฮาร์ดแวร์ใน Vivado และ Export XSA

ต้องเขียน Vivado หรือไม่? **"ต้องทำครับ"** เพราะเรามีวงจรเฉพาะใน PL ดังนี้:
* ขา PWM Generator สำหรับ Airpump
* ขา GPIO Driver สำหรับ Solenoid Valve
* ADC Interface / I2S Interface สำหรับต่อรับเสียง Mic
* บัส I2C สำหรับเชื่อมต่อกับเซนเซอร์ (และเชื่อมกับ STM32)

#### ขั้นตอนใน Vivado (แนะนำเวอร์ชัน 2022.2 หรือ 2023.2):
1. **ติดตั้ง Board Definition Files (BDF):**
   * ดาวน์โหลดและติดตั้ง Board Files ของ **Kria KR260 Robotics Starter Kit** ใน Vivado เพื่อให้มี Preset พินและคอนฟิกของ SOM อัตโนมัติ
2. **สร้าง Vivado Project:**
   * เลือกประเภทเป็น **RTL Project**
   * เลือกบอร์ดเป้าหมายเป็น **Kria KR260 Starter Kit**
3. **สร้าง Block Design (`Diagram`):**
   * วาง IP **Zynq UltraScale+ MPSoC** แล้วกด `Run Block Automation` (Vivado จะตั้งค่า DDR4, MIO, และ Clock ของ KR260 ให้ถูกต้องทันที)
   * **ใส่ IP สำหรับระบบ GI Detect:**
     * **AXI IIC:** สำหรับเชื่อมต่อเซนเซอร์ I2C (PB8/PB9 ของ STM32)
     * **AXI Timer / AXI PWM:** สำหรับสร้างสัญญาณ PWM ไปขับ Airpump
     * **AXI GPIO:** สำหรับสั่งตัด/ต่อไฟ Solenoid Valve
     * **AXI I2S Receiver / Audio Interface:** สำหรับรับสัญญาณเสียงจาก Mic
     * *(ทางเลือก)* **DPU (Deep Learning Processing Unit):** หากต้องการให้ Vitis AI รันบน PL
4. **กำหนด Constraints File (`.xdc`):**
   * กำหนดตำแหน่งขาและระดับแรงดัน (เช่น 3.3V LVCMOS) ของ Airpump PWM, Solenoid GPIO, และ I2C ขาเข้า
5. **สร้าง Bitstream & Export Hardware:**
   * คลิก `Generate Bitstream`
   * เมนู `File` $\rightarrow$ `Export` $\rightarrow$ `Export Hardware...`
   * เลือก **Include bitstream**
   * จะได้ไฟล์ **`system_wrapper.xsa`** ออกมา

---

### Step 2: สร้างและคอนฟิก PetaLinux Project

รันบนเครื่อง Host PC (Ubuntu 20.04 / 22.04 LTS):

```bash
# 1. Source สภาพแวดล้อม PetaLinux Toolchain
source /tools/Xilinx/PetaLinux/2023.2/settings.sh

# 2. สร้างโปรเจกต์ PetaLinux จาก KR260 BSP (แนะนำที่สุด) หรือสร้างเปล่า
# ดาวน์โหลด xilinx-kr260-starterkit-v2023.2-final.bsp จากเว็บ AMD
petalinux-create -t project -s xilinx-kr260-starterkit-v2023.2-final.bsp -n kr260_hil_os

cd kr260_hil_os

# 3. นำเข้าฮาร์ดแวร์ XSA ที่ได้จาก Vivado
petalinux-config --get-hw-description=/path/to/system_wrapper.xsa
```

#### การตั้งค่า Packages สำคัญใน Rootfs (`petalinux-config -c rootfs`):
เปิดใช้งาน Packages เหล่านี้เพื่อรองรับ HIL และ AI:
* **Filesystem Packages:**
  * `v4l2loopback` & `v4l-utils` (สำหรับสร้างกล้องจำลองรับสตรีมวิดีโอผ่าน LAN)
  * `i2c-tools` (สำหรับรันคำสั่ง `i2cdetect`, `i2cget`, `i2cset`)
  * `gstreamer1.0` และปลั๊กอินทั้งหมด (สำหรับรับส่งวิดีโอสตรีม)
  * `openssh`, `openssh-sftp-server` (สำหรับให้ CI/CD เจาะเข้ามาสั่งงาน)
* **Xilinx Packages:**
  * `xrt` (Xilinx Runtime)
  * `vitis-ai-library` & `vitis-ai-library-dev` (สำหรับรัน AI DPU)
  * `xmutil` (สำหรับสลับ FPGA Overlays สดๆ)

---

### Step 3: บิลด์และเตรียม Image สำหรับ MicroSD Card

```bash
# 1. บิลด์ทั้งระบบ (ใช้เวลาประมาณ 20 - 45 นาทีขึ้นกับ CPU)
petalinux-build

# 2. สร้าง Boot Image (BOOT.BIN)
petalinux-package --boot --u-boot --fpga --force

# 3. ไฟล์เอาต์พุตที่ได้ในโฟลเดอร์ images/linux/:
# - BOOT.BIN        (FSBL, PMUFW, ATF, U-Boot, และ Bitstream เริ่มต้น)
# - boot.scr        (U-Boot Boot Script)
# - image.ub        (Linux Kernel + Flattened Device Tree)
# - rootfs.wic      (Full SD Card Disk Image)
```

#### การเขียนลง MicroSD Card:
ใช้โปรแกรม **Balena Etcher** หรือคำสั่ง `dd` เขียนไฟล์ `rootfs.wic` ลงในการ์ด MicroSD (แนะนำขนาด $\ge 32\text{GB}$ Class 10 / U3):
```bash
sudo dd if=images/linux/rootfs.wic of=/dev/sdX bs=4M status=progress conv=fsync
```

---

### Step 4: บูตเครื่องและทดสอบการทำงานเบื้องต้น

1. เสียบการ์ด MicroSD เข้าสล็อตด้านล่างของบอร์ด KR260
2. เสียบสาย LAN จาก Router / Laptop เข้าพอร์ต Ethernet บน KR260
3. เสียบสาย Micro-USB เข้ากับพอร์ต UART ของ KR260 แล้วเปิด Serial Monitor บน Laptop (Baudrate `115200`)
4. เสียบสายไฟ Power Adapter (12V) เพื่อเปิดเครื่อง
5. ระบบจะบูตเข้าสู่ PetaLinux Login:
   * **Username:** `petalinux`
   * **Password:** ตั้งรหัสผ่านใหม่ในการบูตครั้งแรก

---

## 3. กลยุทธ์การ Flash บอร์ด KR260 จาก Self-Hosted CI/CD Agent

เมื่อเรามี CI/CD รันอยู่บน Azure DevOps คำถามสำคัญคือ: **"เวลา Dev แก้โค้ด เราต้อง Flash อะไรบ้าง และทำอย่างไรให้เร็วที่สุด?"**

### ตารางเปรียบเทียบ: Flash แต่ละประเภท

| ลักษณะการ Flash | สิ่งที่ส่งไปเปลี่ยน | ความเร็วในการทำ | ต้อง Reboot เครื่องไหม? | เหมาะสำหรับจังหวะไหนใน CI/CD? |
|---|---|---|---|---|
| **1. Flash แค่ PL** | FPGA Bitstream (`.bit.bin`) + Device Tree Overlay (`.dtbo`) | **เร็วมาก (1 - 3 วินาที)** | ❌ **ไม่ต้อง Reboot** (Hot-reload) | เมื่อมีการแก้เฉพาะวงจรใน FPGA (เช่น แก้วงจร PWM, เพิ่มพิน Sensor, เปลี่ยน Architecture DPU) |
| **2. Flash แค่ PS** | Application Binary (`gi_detect_app`), โมเดล Vitis AI (`.xmodel`), Python Script | **เร็วมากที่สุด (< 1 วินาที)** | ❌ **ไม่ต้อง Reboot** (Restart Service) | เมื่อ Dev แก้ Algorithm การตรวจจับ, ปรับเกณฑ์ PID, หรือเทรนโมเดล AI ใหม่ |
| **3. Flash ทั้งระบบ (Full Boot Image)** | `BOOT.BIN`, Linux Kernel (`image.ub`), Root Filesystem | **ช้า (2 - 5 นาที)** | ⚠️ **ต้อง Reboot เครื่อง** | เมื่อมีการอัปเดต Linux Kernel, ลง Driver ระดับ OS ใหม่, หรือเปลี่ยนโครงสร้าง BSP |

---

### กรณีที่ 1: Flash แค่ PL (FPGA Bitstream Hot-Reload ด้วย `xmutil`)

นี่คือ **ท่าไม้ตายของ Kria KR260** ที่ทำให้ CI/CD รันได้เร็วระดับวินาที โดยไม่ต้องเขียนทับ SD Card หรือเปิด-ปิดบอร์ดใหม่

#### 1. เตรียมไฟล์ 3 ไฟล์บนเครื่อง Host / CI:
* `gi_detect.bit.bin`: ไฟล์ Bitstream ที่แปลงเป็น binary format
* `gi_detect.dtbo`: Device Tree Overlay ที่บอก Linux ว่ามี IP อะไรอยู่ใน PL บ้าง
* `shell.json`: ไฟล์ Metadata อธิบายชื่อแอป

#### 2. คำสั่งที่ Self-hosted CI ยิงผ่าน SSH เข้าไปที่ KR260:
```bash
# 1. ส่งไฟล์ Overlay ขึ้นไปวางในโฟลเดอร์เฟิร์มแวร์ของ Linux
ssh petalinux@192.168.1.120 "sudo mkdir -p /lib/firmware/xilinx/gi_detect"
scp gi_detect.bit.bin gi_detect.dtbo shell.json petalinux@192.168.1.120:/lib/firmware/xilinx/gi_detect/

# 2. ปลด App เก่าออกจาก FPGA Fabric
ssh petalinux@192.168.1.120 "sudo xmutil unloadapp"

# 3. โหลด Bitstream ใหม่เข้าสู่ PL ทันที (FPGA Reconfig เสร็จใน 1-2 วินาที!)
ssh petalinux@192.168.1.120 "sudo xmutil loadapp gi_detect"
```

---

### กรณีที่ 2: Flash แค่ PS (Application / Software Update)

เมื่อ Dev แก้โค้ด C/C++ หรือ Python ของ GI Detect ไม่จำเป็นต้องแตะต้อง FPGA:

```bash
# 1. Compile โปรแกรมบน Host หรือ Self-hosted Agent
# 2. ส่งไฟล์ Binary ตัวใหม่ไปทับที่ /usr/bin/ บน KR260 ผ่าน SCP
scp build/gi_detect_app petalinux@192.168.1.120:/usr/bin/gi_detect_app
scp models/gi_detector.xmodel petalinux@192.168.1.120:/home/petalinux/models/

# 3. สั่ง Restart Background Service ให้เริ่มรันเวอร์ชันใหม่ทันที
ssh petalinux@192.168.1.120 "sudo systemctl restart gi_detect_service"
```

---

### กรณีที่ 3: Flash ทั้งระบบ (Full Boot Image)

หากมีการเปลี่ยน Linux Kernel หรือ Rootfs ขนาดใหญ่ จะต้องเขียนทับ Image หลัก มี 2 วิธีที่ทำได้ใน CI/CD:

#### วิธี A: ใช้ Network Boot (TFTP + NFS) — *วิธีที่ดีที่สุดสำหรับ CI/CD Lab*
* ตั้งค่า U-Boot บน KR260 ให้บูตผ่านสาย LAN โดยดึง `image.ub` ผ่าน **TFTP Server** และเมานต์ Rootfs ผ่าน **NFS Server** บน Laptop
* เมื่อ CI บิลด์ Image ใหม่เสร็จ ให้เอาไฟล์ไปวางในโฟลเดอร์ TFTP แล้วส่งคำสั่ง `sudo reboot` ไปที่ KR260
* บอร์ดจะรีบูตและโหลด OS ตัวใหม่ผ่านสาย LAN ทันทีโดยไม่ต้องแตะต้อง SD Card

#### วิธี B: Remote Partition Flashing
หากบูตจาก MicroSD Card สามารถเขียนไฟล์ Kernel ตัวใหม่ทับลงใน Boot Partition ของ SD Card ผ่าน SSH:
```bash
scp images/linux/image.ub petalinux@192.168.1.120:/boot/
scp images/linux/boot.scr petalinux@192.168.1.120:/boot/
ssh petalinux@192.168.1.120 "sudo reboot"
```

---

## 4. ตัวอย่างสคริปต์ CI/CD อัตโนมัติบน Azure DevOps

นี่คือตัวอย่างการนำกลยุทธ์ด้านบนไปเขียนเป็น Stage ในไฟล์ `azure-pipelines.yml`:

```yaml
# ตัวอย่าง Stage การเลือกระดับการ Flash ใน Azure Pipelines
stages:
- stage: Deploy_To_KR260
  displayName: 'Deploy Hardware & Software to KR260'
  jobs:
  - job: Selective_Deploy
    steps:
    
    # ถ้ามีการเปลี่ยนแปลงในโฟลเดอร์ hardware/ (PL เปลี่ยน) ให้โหลด bitstream ใหม่
    - script: |
        echo "=== Updating PL Bitstream via xmutil ==="
        ssh petalinux@$(KR260_IP) "sudo xmutil unloadapp"
        scp hardware/output/gi_detect.* petalinux@$(KR260_IP):/lib/firmware/xilinx/gi_detect/
        ssh petalinux@$(KR260_IP) "sudo xmutil loadapp gi_detect"
      displayName: 'Hot-Reload FPGA Bitstream (PL Only)'
      condition: eq(variables['UPDATE_PL'], 'true')

    # ถ้ามีการเปลี่ยนแปลงเฉพาะ software/ (PS เปลี่ยน) ให้ส่ง Binary ตัวใหม่
    - script: |
        echo "=== Updating PS Application Binary ==="
        scp software/build/gi_detect_app petalinux@$(KR260_IP):/usr/bin/gi_detect_app
        ssh petalinux@$(KR260_IP) "sudo systemctl restart gi_detect_service"
      displayName: 'Update Software Binary (PS Only)'

- stage: Execute_HIL_Tests
  displayName: 'Execute Pytest on HIL'
  dependsOn: Deploy_To_KR260
  jobs:
  - job: Run_Tests
    steps:
    - script: |
        source .venv/bin/activate
        pytest tests/ -v --csv=reports/test_results.csv
      displayName: 'Run Pytest Framework'
```

---

## สรุปคำแนะนำสำหรับทีมพัฒนา

1. **ในช่วงเริ่มโปรเจกต์:** สร้าง Vivado Block Design ขั้นต่ำที่มีพิน I2C, PWM, GPIO ให้เสร็จก่อน แล้วบิลด์ PetaLinux Base OS ลง MicroSD ให้บอร์ดบูตติดและเปิด SSH ได้
2. **ในวงรอบ CI/CD ประจำวัน (Daily CI/CD):** 
   * **90% ของงาน** จะเป็นการแก้โค้ด PS (AI / PID / Logic) ให้ใช้วิธี **Flash แค่ PS ผ่าน SCP** ซึ่งใช้เวลาไม่ถึง 2 วินาที
   * **10% ของงาน** เมื่อมีการปรับวงจร FPGA ให้ใช้วิธี **Hot-reload PL ด้วย `xmutil loadapp`**
   * หลีกเลี่ยงการ Flash ทั้ง Boot Image ใน CI ประจำวัน เพื่อลดเวลาและถนอมอายุการใช้งานของการ์ด MicroSD ครับ
