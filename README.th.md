# Cat Theatre Movies Server

> เซิร์ฟเวอร์แบบ self-hosted สำหรับเรียกดูและสตรีมภาพยนตร์ที่มีน้ำหนักเบา สร้างด้วย Flask, Waitress และ `ffmpeg` พร้อมการผสาน _`Plex`_ แบบเลือกใช้สำหรับเส้นทางการเล่นที่เน้นความเข้ากันได้

---

![Screenshot 2026-03-22 at 9 39 12 PM](https://github.com/user-attachments/assets/124f21b7-71b0-46fc-9d76-c73f700c25f3)

---

**ภาษา**

[English](./README.md) | [简体中文](./README.zh-CN.md) | [繁體中文（香港）](./README.zh-HK.md) | [繁體中文（台灣）](./README.zh-TW.md) | [Français](./README.fr.md) | [한국어](./README.ko.md) | [日本語](./README.ja.md) | [Deutsch](./README.de.md) | `ไทย` | [Tiếng Việt](./README.vi.md) | [Nederlands](./README.nl.md)

---

## ภาพรวม

Cat Theatre ถูกออกแบบให้เบาโดยตั้งใจ:

- พื้นที่พึ่งพา Python น้อย
- ไม่ต้องใช้ฐานข้อมูล
- จัดทำแคตตาล็อกโดยยึดระบบไฟล์เป็นหลัก
- ใช้กระบวนการสแกนแบบ polling ที่พกพาได้ แทนการพึ่ง watcher เฉพาะระบบปฏิบัติการ
- การรวม Plex เป็นชั้นเสริมแบบเลือกได้ ไม่ใช่สิ่งจำเป็นสำหรับการเล่นหลัก

ออกแบบมาสำหรับ:

- ไลบรารีสื่อในเครื่องที่กระจายอยู่ในหนึ่งหรือหลายโฟลเดอร์
- การสร้างภาพขนาดย่อและเฟรมพรีวิว
- การควบคุมการเข้าถึงโฟลเดอร์ส่วนตัวตามอุปกรณ์
- การติดตั้งหลัง reverse proxy ภายใต้ prefix เช่น `/movie/`
- กลยุทธ์การเล่นแบบผสม: เล่นไฟล์ตรง, แปลงรหัสในเครื่องแบบในตัว, หรือ HLS ผ่าน Plex

---

## คุณสมบัติ

- สแกนสื่อจากหลาย root
- สร้างภาพย่อโปสเตอร์และเฟรมพรีวิว
- โฟลเดอร์ส่วนตัวพร้อมการปลดล็อกตามอุปกรณ์
- direct playback แบบเนทีฟสำหรับฟอร์แมตที่ปลอดภัยต่อเบราว์เซอร์
- แปลงรหัสในเครื่องแบบในตัวสำหรับ `.mkv` และ `.ts` เมื่อเปิดใช้งาน
- การรวม Plex สำหรับการเล่น โปสเตอร์ คำบรรยาย และ HLS proxy
- routing ที่รับรู้ context path สำหรับ reverse proxy
- แคชรูปภาพของเบราว์เซอร์และแคชข้อมูลเมตาใน IndexedDB

### หมายเหตุด้าน UX และการเล่น

- แผง debug แบบในตัวอยู่มุมขวาล่าง และสามารถเลื่อนไปยังขอบที่ใกล้ที่สุดได้
- การเล่นจะเลือกเส้นทางที่ปลอดภัยกว่าสำหรับไฟล์และอุปกรณ์ปัจจุบันโดยอัตโนมัติ
- การบังคับ Direct/Plex แบบแมนนวลจะถูกเก็บแยกตามวิดีโอใน IndexedDB
- ภาพย่อและข้อมูลเมตาที่แคชไว้จะอยู่ภายในขีดจำกัดพื้นที่จัดเก็บของเบราว์เซอร์

---

## ข้อกำหนด

### Python

```bash
pip install -r requirements.txt
```

แพ็กเกจ Python ปัจจุบัน:

- `Flask`
- `waitress`

### ไบนารีของระบบ

จำเป็นสำหรับการตรวจสอบข้อมูลเมตา พรีวิว ภาพย่อ และการแปลงรหัสในเครื่อง:

- `ffmpeg`
- `ffprobe`

ตรวจสอบว่าพร้อมใช้งาน:

```bash
which ffmpeg
which ffprobe
```

---

## เริ่มต้นอย่างรวดเร็ว

วิธีเริ่มต้นที่แนะนำ:

```bash
./startup.sh
```

สคริปต์บูตสแตรปนี้สามารถ:

- สร้าง `movies_config.json` จาก config ตัวอย่างในการรันครั้งแรก
- สร้าง `.venv` ภายในเครื่อง
- ติดตั้ง dependency ของ Python ลงใน virtual environment ภายในเครื่องนั้น
- ตรวจสอบ `ffmpeg` และ `ffprobe`
- ช่วยสร้างแฮชรหัสผ่านสำหรับโหมดส่วนตัวได้แบบเลือกทำ
- เริ่มเซิร์ฟเวอร์ด้วย config ภายในเครื่องของคุณ

คุณยังคงใช้ขั้นตอนแบบแมนนวลด้านล่างได้:

1. คัดลอกไฟล์ config ตัวอย่าง:

```bash
cp movies_config.sample.json movies_config.json
```

2. แก้ไข `movies_config.json` ให้เหมาะกับสภาพแวดล้อมของคุณ

3. เริ่มเซิร์ฟเวอร์:

```bash
python3 movies_server.py --config movies_config.json
```

4. เปิด UI:

```text
http://localhost:9245
```

หากคุณติดตั้งแอปไว้หลัง reverse proxy ภายใต้ prefix เช่น `/movie/` ให้เปิด URL ที่มี prefix นั้นแทน

---

## โครงสร้างโปรเจกต์

- `movies_server.py`: entrypoint ของ Flask และการผูก route
- `movies_server_core.py`: helper ฝั่งเซิร์ฟเวอร์ที่ใช้ร่วมกันสำหรับ auth, config, cookie และการจัดการ mount path
- `movies_catalog.py`: การสแกนแคตตาล็อก การสร้างภาพย่อ การดึงคำบรรยาย และ helper สำหรับการแปลงรหัสในเครื่อง
- `movies_server_plex.py`: ตัวเชื่อม Plex, การแมปโปสเตอร์/คำบรรยาย และ Plex HLS proxy
- `movies.js`: ซอร์สฝั่ง frontend
- `movies.min.js`: bundle frontend แบบ minified
- `movies.css`: สไตล์ของแกลเลอรีและตัวเล่น
- `passcode.py`: helper สำหรับหมุนรหัสผ่านโหมดส่วนตัว

---

## การตั้งค่า

config ตัวอย่างถูกล้างข้อมูลสำคัญออกโดยตั้งใจ และจะไม่มี:

- path ของระบบไฟล์จริง
- Plex token จริง
- passcode จริง
- ค่าที่เฉพาะกับอุปกรณ์

### ฟิลด์สำคัญ

- `root`: root ของสื่อที่จะสแกน
- `thumbs_dir`: ไดเรกทอรีสำหรับภาพย่อและเฟรมพรีวิว
- `private_folder`: prefix ของโฟลเดอร์ที่ถือว่าเป็นส่วนตัว
- `private_passcode`: hash ของ passcode สำหรับโหมดส่วนตัว
- `mount_script`: คำสั่งเสริมที่จะเรียกเมื่อการเล่นพบโฟลเดอร์สื่อที่หายไป
- `transcode`: เปิดใช้ worker แปลงรหัสแบบเบื้องหลังฝั่งแคตตาล็อกสำหรับ source container เช่น `.mkv` และ `.ts` ซึ่งอาจสร้างไฟล์ทรานส์โค้ดแยกเพิ่มเติมไว้ข้างไลบรารีสื่อ ดังนั้นโดยทั่วไปควรปล่อยเป็น `false` โดยเฉพาะเมื่อเปิดใช้ Plex integration
- `auto_scan_on_start`: สแกนสื่อใหม่เมื่อเริ่มต้น
- `on_demand_transcode`: เปิดใช้การแปลงรหัสขณะเล่นจริงในตัวเล่นสำหรับ source container โดยจะพยายามใช้ฮาร์ดแวร์เข้ารหัสก่อน และ fallback เป็นซอฟต์แวร์เมื่อจำเป็น
- `on_demand_hls`: เปิดใช้ HLS playlist แบบในตัวสำหรับ source container
- `enable_plex_server`: เปิดใช้การรวม Plex
- `plex.base_url`: URL หลักของเซิร์ฟเวอร์ Plex
- `plex.token`: Plex token
- `debug_enabled`: แสดง debug overlay แบบในตัว
- `direct_playback`: object ที่มี `enabled` และ `audio_whitelist`

### ตัวอย่างขั้นต่ำแบบ local-only

```json
{
  "root": [
    "~/Movies"
  ],
  "thumbs_dir": "./cache/thumbs",
  "mount_script": "",
  "private_folder": [],
  "private_passcode": "",
  "on_demand_transcode": true,
  "on_demand_hls": true,
  "enable_plex_server": false,
  "auto_scan_on_start": true
}
```

### ตัวอย่างแบบรวม Plex

```json
{
  "root": [
    "~/Movies"
  ],
  "thumbs_dir": "./cache/thumbs",
  "mount_script": "",
  "private_folder": [],
  "private_passcode": "",
  "on_demand_transcode": true,
  "on_demand_hls": true,
  "enable_plex_server": true,
  "plex": {
    "base_url": "http://127.0.0.1:32400",
    "token": "REPLACE_WITH_YOUR_PLEX_TOKEN"
  },
  "auto_scan_on_start": true
}
```

### พฤติกรรมการสแกน Plex

- จะข้ามการสร้างภาพย่อโปสเตอร์ในเครื่องเมื่อมีโปสเตอร์จาก Plex
- ภาพย่อในเครื่องที่ถูกแคชไว้ก่อนหน้ายังสามารถนำกลับมาใช้ได้
- การสร้างเฟรมพรีวิวยังคงเปิดใช้งานอยู่
- การรวม Plex ยังคงเป็นทางเลือก และโหมด local-only ยังทำงานได้

### วิธีรับ Plex Token

#### วิธีที่ 1: ใช้ Plex Web Session ที่มีอยู่

1. เปิด Plex Web และลงชื่อเข้าใช้
2. เปิด developer tools ของเบราว์เซอร์
3. ไปที่แท็บ Network
4. รีเฟรชหน้า
5. ตรวจสอบคำขอที่ส่งไปยังเซิร์ฟเวอร์ Plex
6. หา `X-Plex-Token` ใน URL หรือ header

#### วิธีที่ 2: Browser Storage

ตรวจสอบ:

- Local Storage
- Session Storage
- URL และ header ของคำขอใน DevTools

#### วิธีที่ 3: Direct Local Request

ถ้าคุณมี Plex Web session ที่ยัง active บนเครื่องเดียวกันอยู่แล้ว ให้ตรวจสอบคำขอ Plex ใน DevTools และมองหา:

```text
X-Plex-Token=...
```

ข้อควรระวังด้านความปลอดภัย:

- ให้ถือ Plex token เหมือนรหัสผ่าน
- อย่าคอมมิตลง git
- เก็บไว้เฉพาะใน `movies_config.json`

---

## โหมดการเล่น

### 1. Native Direct Playback

ใช้สำหรับไฟล์ที่ปลอดภัยต่อเบราว์เซอร์ เช่น `.mp4`, `.m4v`, `.webm`

พฤติกรรม:

- ให้บริการไฟล์ในเครื่องโดยตรงจาก `/video/<id>`
- รองรับ HTTP range requests
- ลด overhead จากการแปลงรหัสเมื่อเบราว์เซอร์เล่นไฟล์ได้โดยตรง

เหมาะที่สุดสำหรับ:

- ไฟล์สไตล์ MP4/H.264
- เบราว์เซอร์ที่รองรับไฟล์นั้นโดยตรงอยู่แล้ว
- ไฟล์ที่ codec เสียงตรงกับ direct-play whitelist

### 2. การแปลงรหัสในเครื่องแบบในตัวโดยไม่ใช้ Plex

นี่คือเส้นทาง fallback เมื่อไม่ได้เปิด Plex หรือเมื่อคุณต้องการคงความเป็น local ทั้งหมดโดยตั้งใจ

การทำงานปัจจุบัน:

- `.mkv` และ `.ts` สามารถเปิดเป็น HLS ภายในเครื่องที่ `/hls/<id>/index.m3u8`
- ไฟล์เดียวกันยังสามารถสตรีมเป็น fragmented MP4 ได้ที่ `/video/<id>?fmp4=1`
- HLS segments ถูกสร้างตามต้องการด้วย `ffmpeg`
- สามารถลอง hardware encode ก่อนแล้วค่อย fallback ไป `libx264`
- เอาต์พุต fMP4 ถูกสร้างด้วย `libx264` และ AAC

### 3. การเล่นผ่าน Plex

เมื่อเปิดใช้งานการรวม Plex:

- frontend สามารถใช้ `plex_stream_url` สำหรับการเล่นที่เน้นความเข้ากันได้
- Plex จะสร้าง HLS playlist ต้นทาง
- เซิร์ฟเวอร์นี้จะเขียน playlist ใหม่และ proxy คำขอ playlist และ segment ที่ซ้อนกัน
- เบราว์เซอร์ยังคุยกับแอปนี้ ไม่ได้คุยกับ Plex โดยตรง

เหมาะที่สุดสำหรับ:

- เนื้อหา MKV หรือ TS บนอุปกรณ์ที่รองรับ codec หรือ container ได้ไม่ดี
- กรณีที่ต้องการให้ Plex จัดการการเลือกคำบรรยายหรือการปรับสตรีมให้เป็นมาตรฐาน

### นโยบายการเลือกการเล่น

- direct playback จะชนะสำหรับไฟล์ที่ปลอดภัยต่อเบราว์เซอร์และมี codec เสียงตรงกับ `direct_playback.audio_whitelist`
- Plex ยังคงถูกเลือกก่อนสำหรับ `.mkv`, `.ts`, HLS, fMP4 หรือ codec เสียงที่ไม่รองรับ
- เวลา fallback ของ HLS แบบเนทีฟบน iOS จะนานกว่า เพื่อให้สตรีม Plex มีเวลา warm up

### ตรรกะการเล่นเริ่มต้น

- `Direct` จะถูกเลือกก่อนสำหรับ `.mp4`, `.m4v`, `.webm`, `.avi` เมื่อ direct URL เป็น path ของไฟล์จริงและ codec เสียงปลอดภัยตาม whitelist
- หากข้อมูลเมตา codec เสียงหายไปสำหรับหนึ่งในนามสกุลที่ปลอดภัยต่อเบราว์เซอร์ แอปก็ยังเลือก `Direct`
- `Plex` จะถูกเลือกก่อนสำหรับ `.mkv`, `.ts`, direct URL แบบ HLS/fMP4 และไฟล์ที่ codec เสียงที่ทราบอยู่นอก whitelist
- หากไม่มี Plex match แอปจะ fallback ไปที่ `Direct`

---

## Debug Overlay

เปิด `debug_enabled` ใน `movies_config.json` เพื่อให้มี debug overlay ถาวรที่มุมขวาล่าง

แผงนี้รายงาน:

- เซิร์ฟเวอร์กำลังเอนเอียงไปทาง direct playback หรือ Plex
- direct-play audio whitelist ที่ตั้งค่าไว้
- candidate การเล่นปัจจุบันและ video ID
- metric ความคืบหน้าการสแกนล่าสุด

ตรวจสอบค่าคอนฟิกที่ใช้งานจริงด้วย:

```bash
curl -s http://localhost:9245/api/config | python3 -m json.tool
```

ถ้าคุณให้บริการแอปภายใต้ `/movie/` ให้ใช้ path ที่มี prefix

---

## โมเดลการยืนยันตัวตน

แอปใช้วิธีส่งข้อมูลต่างกันตามชนิดของคำขอ:

- คำขอ API ใช้ header `X-Device-Id`
- คำขอ HLS และ Plex proxy ใช้ header `X-Device-Id`
- คำขอสื่อแบบ direct เนทีฟใช้ cookie `movies_device_id` เป็น fallback

การแยกเช่นนี้มีอยู่เพราะคำขอ `<video src="...">` แบบเนทีฟไม่สามารถแนบ custom header ใด ๆ ได้

---

## รองรับ Reverse Proxy และ Context Path

แอปรองรับการติดตั้งภายใต้ subpath เช่น:

- `https://example.com/movie/`
- `https://example.com/cinema/`

ระบบ routing จะเก็บ prefix การ mount ที่ใช้งานอยู่สำหรับ:

- สื่อแบบ direct
- HLS ภายในเครื่อง
- คำขอ Plex HLS proxy
- asset ของโปสเตอร์และคำบรรยาย

---

## การเข้าถึง Plex ระยะไกลด้วย Tailscale

หาก UI แบบกำหนดเองเข้าถึงได้จากระยะไกล แต่ Plex เข้าถึงได้เฉพาะใน LAN ส่วนตัว โฮสต์ที่รัน movies server ก็ยังต้องเข้าถึง backend ของ Plex ได้โดยตรง

### โฮสต์เดียวกัน

```json
"plex": {
  "base_url": "http://127.0.0.1:32400"
}
```

### Plex อยู่บนเครื่องอื่นใน LAN

โฆษณา route จากโหนด Tailscale ที่เข้าถึง Plex ได้:

```bash
sudo tailscale up --advertise-routes=192.168.50.0/24
```

จากนั้นตรวจสอบการเข้าถึงจากโฮสต์ของ movies server:

```bash
curl http://192.168.50.10:32400/identity
```

หมายเหตุ:

- เบราว์เซอร์ไม่จำเป็นต้องเข้าถึง Plex โดยตรง
- โปรเซส movies server ต้องเข้าถึง `plex.base_url` ได้
- reverse proxy หรือชื่อ MagicDNS ของ UI ไม่ได้ทำให้ Plex เข้าถึงได้เองโดยอัตโนมัติ

---

## กลยุทธ์การแคช

### การแคชรูปภาพ

ภาพย่อ เฟรมพรีวิว และภาพโปสเตอร์ของ Plex จะถูกเสิร์ฟพร้อม immutable cache headers แบบอายุยาว

### การแคชข้อมูลเมตา

snapshot ข้อมูลเมตาของแกลเลอรีถูกแคชใน IndexedDB โดยมีขอบเขตการใช้พื้นที่:

- TTL 1 วัน
- snapshot records สูงสุด 8 รายการ
- ขนาดรวมโดยประมาณสูงสุดประมาณ 18 MB
- ลบรายการเก่าเมื่อเกินขีดจำกัด

แต่ละ snapshot ที่แคชไว้จะเก็บ:

- `catalogStatus` ของเซิร์ฟเวอร์
- แคชรายการโฟลเดอร์
- `videos` ที่โหลดแล้ว
- ตัวนับหน้าอย่าง `serverTotal`, `serverOffset`, `serverExhausted`

การลบเกิดขึ้นแบบตามโอกาส ไม่ใช่ตามตาราง:

- รายการที่หมดอายุจะถูกลบตอนอ่านหรือในการ prune ภายหลัง
- prune จะทำงานหลังจากบันทึก snapshot ใหม่
- แรงกดดันจากพื้นที่จัดเก็บของเบราว์เซอร์หรือการลบ site data ด้วยมือก็อาจลบข้อมูล IndexedDB ได้เช่นกัน

---

## พฤติกรรมการสแกน

การสแกนแคตตาล็อกถูกออกแบบให้ยังคงมีต้นทุนแบบ incremental แม้ว่าจะยังต้องเดินทุก root ที่กำหนดไว้

พฤติกรรมปัจจุบัน:

- ไฟล์ที่ไม่เปลี่ยนจะใช้ signature `mtime + size` ที่แคชไว้ซ้ำ
- การสแกนเป็นช่วง ๆ จะไม่ sort รายการ path ทั้งหมดก่อนประมวลผลอีกต่อไป
- ไฟล์ที่ถูกลบจะถูกนำออกจากแคตตาล็อกในหน่วยความจำและ index ที่ถูกบันทึกไว้
- ไฟล์ที่ถูกลบจะกระตุ้นการล้าง thumbnail และ preview artifact ที่สร้างไว้
- การบันทึก index จะใช้ข้อมูล signature ของไฟล์ที่แคชไว้ แทนการ stat ไฟล์ทุกไฟล์อีกครั้ง

สิ่งที่การสแกนยังทำอยู่:

- เดิน root สื่อที่กำหนดไว้เพื่อตรวจจับไฟล์ที่เพิ่ม เปลี่ยน หรือลบ
- เข้าคิวการสร้าง preview เมื่อไม่มีภาพ preview

สิ่งที่มันไม่ทำ:

- ไม่คำนวณ checksum ของไฟล์สื่อขนาดใหญ่ระหว่างการสแกนตามรอบ
- ไม่สร้าง thumbnail หรือ metadata ใหม่สำหรับไฟล์ที่ไม่เปลี่ยน เว้นแต่ artifact ที่แคชไว้จะหายไป

### บังคับ Full Rescan

ใช้:

```text
/rescan?full=1
```

สิ่งนี้มีประโยชน์เมื่อ:

- มีคนลบโฟลเดอร์ cache ของ thumbnail หรือ preview ด้วยมือ
- คุณสงสัยว่า manifest การสแกนที่บันทึกไว้ล้าสมัย
- คุณต้องการบังคับตรวจสอบสถานะที่ได้มาจากการสแกนใหม่ทั้งหมด

### ตรวจสอบสถานะการสแกน

```bash
curl -s http://localhost:9245/api/status | python3 -m json.tool
```

หากคุณให้บริการแอปภายใต้ `/movie/` ให้ใช้ path ที่มี prefix

### เรียกการสแกนใหม่

Incremental rescan ปกติ:

```bash
curl -s http://localhost:9245/rescan | python3 -m json.tool
```

Forced full rescan:

```bash
curl -s "http://localhost:9245/rescan?full=1" | python3 -m json.tool
```

### UI การสแกนใหม่

ปุ่ม `Rescan` จะเปิด action dialog แทนที่จะเริ่ม incremental scan ทันที

การกระทำที่มี:

- `Rescan`: incremental scan สำหรับไฟล์ใหม่หรือไฟล์ที่เปลี่ยน
- `Full Scan`: ล้างสถานะการสแกนที่บันทึกไว้และบังคับตรวจสอบข้อมูลเมตาใหม่ทั้งหมด
- `Refresh Database`: ล้าง snapshot ใน IndexedDB ของเบราว์เซอร์และโหลดข้อมูลแคตตาล็อกใหม่

### การกู้คืนเมื่อ mount หาย

หากตั้งค่า `mount_script` ไว้และมีคำขอสื่อไปเจอโฟลเดอร์ที่หายไป เซิร์ฟเวอร์จะ:

1. ตรวจพบว่าโฟลเดอร์แม่ไม่มีอยู่
2. เรียก mount script ที่ตั้งค่าไว้หนึ่งครั้ง
3. ตรวจสอบ path เป้าหมายอีกครั้ง
4. ส่งกลับ `Media folder is not mounted` พร้อม HTTP 404 ก็ต่อเมื่อโฟลเดอร์ยังไม่พร้อมใช้งาน

ฝั่ง frontend จะถือว่า playback 404 เป็นสถานะจบสำหรับความพยายามครั้งนั้น และจะแสดงข้อความให้ลองใหม่แทนการยิงซ้ำไปที่เซิร์ฟเวอร์เรื่อย ๆ

---

## หมายเหตุการพัฒนา Frontend

ปัจจุบันแอปโหลด `movies.js` โดยตรงจาก `index.html` ดังนั้นการเปลี่ยนแปลงฝั่ง frontend จะมีผลทันทีโดยไม่ต้อง rebuild `movies.min.js`

---

## โหมดส่วนตัว

- โฟลเดอร์ส่วนตัวจะถูกซ่อนจนกว่าอุปกรณ์จะได้รับอนุญาต
- สถานะการปลดล็อกผูกกับ device ID
- อุปกรณ์ที่ได้รับอนุญาตจะถูกเก็บไว้ฝั่งเซิร์ฟเวอร์
- `passcode.py` สามารถหมุน passcode ของโหมดส่วนตัวและล้างการอนุมัติได้

ตัวอย่าง:

```bash
python3 passcode.py mynewpasscode
```

---

## ไฟล์ที่สร้างขึ้น

ไฟล์เหล่านี้ถูกสร้างขึ้นขณะรันและไม่ควรถูกคอมมิต:

- `movies_config.json`
- `movies_state.json`
- `movies_auth_state.json`
- `movies_catalog_index.json`
- `cache/`

---

## การแก้ปัญหา

### การเปลี่ยนแปลง UI ไม่ปรากฏ

- รีเฟรชหน้าตามปกติก่อน
- หาก JS bundle เปลี่ยน ให้ยืนยันว่า `index.html` อ้างอิง bundle version ที่ถูกต้อง

### Direct Playback ของเนื้อหาส่วนตัวล้มเหลว

- ปลดล็อกโหมดส่วนตัวอีกครั้งเพื่อให้ cookie `movies_device_id` ถูกรีเฟรช

### Plex Playback ล้มเหลวแต่ Direct Playback ใช้งานได้

- ตรวจสอบว่าโฮสต์ของ movies server เข้าถึง `plex.base_url` ได้
- ตรวจสอบว่าเปิดใช้ Plex ใน config แล้ว
- ตรวจสอบว่า token ที่ตั้งค่าไว้ถูกต้อง

### Direct Playback ล้มเหลวแต่ Plex ใช้งานได้

- container หรือ codec นั้นอาจไม่ปลอดภัยสำหรับการเล่นแบบเนทีฟในเบราว์เซอร์บนอุปกรณ์นั้น
- ให้เปิดใช้ Plex สำหรับไฟล์เหล่านั้นต่อไป หรือบังคับใช้เส้นทางแบบ compatible ผ่าน local transcode หรือ Plex

### Local Transcoding ใช้งานไม่ได้

- ตรวจสอบว่าติดตั้ง `ffmpeg` และ `ffprobe` แล้ว
- ตรวจสอบว่าเปิดใช้ `on_demand_transcode` แล้ว
- ตรวจสอบว่าไฟล์ต้นทางอยู่ใน container ที่รองรับในปัจจุบัน: `.mkv` หรือ `.ts`

---

## ใบอนุญาต

รีโพซิทอรีนี้ยังไม่ได้ประกาศใบอนุญาตซอฟต์แวร์ หากคุณวางแผนจะเผยแพร่ต่อ ควรเพิ่มใบอนุญาตอย่างชัดเจน
