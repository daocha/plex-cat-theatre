# Cat Theatre Movies Server

> เซิร์ฟเวอร์ดูและสตรีมภาพยนตร์แบบโฮสต์เองที่สร้างด้วย Flask, Waitress และ `ffmpeg` พร้อมการรวม Plex แบบเลือกใช้สำหรับการเล่นที่เน้นความเข้ากันได้

**ภาษา**

[English](./README.md) | `ไทย`

---

## ภาพรวม

Cat Theatre ถูกออกแบบให้เบา:

- ใช้ dependency Python น้อย
- ไม่ต้องมีฐานข้อมูล
- ใช้ระบบไฟล์เป็นหลัก
- สแกนแบบ polling ที่พกพาได้
- Plex เป็นตัวเลือกเสริม

เหมาะสำหรับ:

- ไลบรารีสื่อท้องถิ่นหลายโฟลเดอร์
- การสร้างภาพย่อและภาพพรีวิว
- การควบคุมโฟลเดอร์ส่วนตัวตามอุปกรณ์
- การใช้งานหลัง reverse proxy ใต้ path เช่น `/movie/`
- direct play, local transcoding และ Plex HLS

---

## ความสามารถ

- สแกนหลาย root
- ภาพย่อโปสเตอร์และเฟรมพรีวิว
- โฟลเดอร์ส่วนตัว
- direct play แบบ native
- local transcoding สำหรับ `.mkv` และ `.ts`
- การรวม Plex
- รองรับ reverse proxy แบบ subpath
- cache รูปภาพของเบราว์เซอร์และ cache IndexedDB

---

## โครงสร้างโปรเจกต์

- `movies_server.py`
- `movies_server_core.py`
- `movies_catalog.py`
- `movies_server_plex.py`
- `movies.js`
- `movies.min.js`
- `movies.css`
- `passcode.py`

---

## สิ่งที่ต้องมี

```bash
pip install -r requirements.txt
which ffmpeg
which ffprobe
```

---

## เริ่มต้นอย่างรวดเร็ว

```bash
cp movies_config.sample.json movies_config.json
python3 movies_server.py --config movies_config.json
```

เปิด:

```text
http://localhost:9245
```

---

## การตั้งค่า

ฟิลด์สำคัญ:

- `root`
- `thumbs_dir`
- `private_folder`
- `private_passcode`
- `mount_script`
- `auto_scan_on_start`
- `on_demand_transcode`
- `on_demand_hls`
- `enable_plex_server`
- `plex.base_url`
- `plex.token`
- `debug_enabled`
- `direct_playback`

---

## โหมดการเล่น

- direct play: `/video/<id>`
- local transcoding: `/hls/<id>/index.m3u8` หรือ `/video/<id>?fmp4=1`
- Plex playback: Plex สร้าง HLS แล้วแอปนี้ทำ proxy ให้

### ตรรกะการเลือกโหมดเล่นเริ่มต้น

- ระบบจะเลือก `Direct` สำหรับ `.mp4`, `.m4v`, `.webm`, `.avi` เมื่อ direct URL เป็นไฟล์จริงและ codec เสียงอยู่ใน whitelist
- หากไฟล์กลุ่มที่ถือว่าปลอดภัยกับเบราว์เซอร์เหล่านี้ไม่มี metadata ของเสียง แอปก็ยังคงเลือก `Direct`
- ระบบจะเลือก `Plex` สำหรับ `.mkv`, `.ts`, direct URL แบบ HLS/fMP4 และไฟล์ที่มี codec เสียงที่ทราบว่าอยู่นอก whitelist
- หากไม่มี Plex match ระบบจะ fallback ไปที่ `Direct`

---

## แคชและการสแกน

- รูปภาพใช้แคชระยะยาว
- IndexedDB snapshot มี TTL 1 วัน
- สูงสุด 8 snapshot
- ขนาดรวมประมาณ 18 MB
- `/rescan?full=1` ใช้บังคับ revalidate แบบเต็ม

---

## โหมดส่วนตัวและดีบัก

- โฟลเดอร์ส่วนตัวถูกซ่อนโดยค่าเริ่มต้น
- การปลดล็อกผูกกับอุปกรณ์
- `passcode.py` ใช้หมุนรหัสผ่านได้
- `debug_enabled` แสดง overlay ดีบัก

---

## การแก้ปัญหา

- หาก Plex เล่นไม่ได้ ให้ตรวจ `plex.base_url` และ token
- หาก local transcoding ล้มเหลว ให้ตรวจ `ffmpeg`, `ffprobe`, `on_demand_transcode`
