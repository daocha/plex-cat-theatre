<div align="center">
  <img width="700" alt="7844F597-CBA9-4EAD-80DE-19991552F906" src="https://github.com/user-attachments/assets/2f1fc4cf-8b63-47d0-aebf-53355dd8f032" />

  <h1>Cat Theatre Movies Server 🐱</h1>
  <p>
    <a href="https://github.com/daocha/plex-cat-theatre/blob/main/README.md">English</a> |
    <a href="https://github.com/daocha/plex-cat-theatre/blob/main/README.de.md">Deutsch</a> |
    <a href="https://github.com/daocha/plex-cat-theatre/blob/main/README.fr.md">Français</a> |
    <a href="https://github.com/daocha/plex-cat-theatre/blob/main/README.ja.md">日本語</a> |
    <a href="https://github.com/daocha/plex-cat-theatre/blob/main/README.ko.md">한국어</a> |
    <a href="https://github.com/daocha/plex-cat-theatre/blob/main/README.nl.md">Nederlands</a> |
    <a href="https://github.com/daocha/plex-cat-theatre/blob/main/README.th.md">ไทย</a> |
    <a href="https://github.com/daocha/plex-cat-theatre/blob/main/README.vi.md">Tiếng Việt</a> |
    <a href="https://github.com/daocha/plex-cat-theatre/blob/main/README.zh-CN.md">简体中文</a> |
    <a href="https://github.com/daocha/plex-cat-theatre/blob/main/README.zh-HK.md">繁體中文（香港）</a> |
    <a href="https://github.com/daocha/plex-cat-theatre/blob/main/README.zh-TW.md">繁體中文（台灣）</a>
  </p>
  <p><strong>เบามาก, โหมดความเป็นส่วนตัว 🔐, ใช้งานข้ามอุปกรณ์, สตรีมอัจฉริยะ</strong></p>
  <p>ไม่ต้องใช้แอป ติดตั้งเซิร์ฟเวอร์ง่าย อินเทอร์เฟซเหมาะกับมือถือ เชื่อมต่อ NAS ได้จากทุกที่ พร้อมการรวม Plex แบบเลือกใช้</p>
  <p>
    <img src="https://img.shields.io/badge/stability-experimental-orange.svg" alt="Experimental" />
    <a href="https://opensource.org/licenses/MIT">
      <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="MIT License" />
    </a>
    <a href="http://github.com/daocha/plex-cat-theatre/releases/latest">
      <img src="https://img.shields.io/github/v/release/daocha/plex-cat-theatre?label=Latest&color=green" alt="Latest Release" />
    </a>
    <img src="https://img.shields.io/badge/python-3.9+-blue" alt="Python 3.9+" />
  </p>
</div>



> ไม่มี dependency หนัก ทุกอย่างโปร่งใส เซิร์ฟเวอร์แบบ self-hosted สำหรับเรียกดูและสตรีมภาพยนตร์ที่มีน้ำหนักเบา สร้างด้วย Flask, Waitress และ `ffmpeg` พร้อมการผสาน _`Plex`_ แบบเลือกใช้สำหรับเส้นทางการเล่นที่เน้นความเข้ากันได้

---

![Screenshot 2026-03-22 at 9 39 12 PM](https://github.com/user-attachments/assets/124f21b7-71b0-46fc-9d76-c73f700c25f3)

---

## ✨ ทำไมถึงควรใช้

Cat Theatre ถูกออกแบบให้เบาโดยตั้งใจ:

- 🩷 _การเข้าถึงจากระยะไกล_ ไม่ต้องใช้ Plex subscription 💰
- ✅ พื้นที่พึ่งพา Python น้อย
- ✅ ไม่ต้องใช้ฐานข้อมูล
- ✅ จัดทำแคตตาล็อกโดยยึดระบบไฟล์เป็นหลัก
- ✅ ใช้งานได้กับ 🖥️ เดสก์ท็อป, 📱 มือถือ และแท็บเล็ต
- ✅ ใช้กระบวนการสแกนแบบ polling ที่พกพาได้ แทนการพึ่ง watcher เฉพาะระบบปฏิบัติการ
- 🔶 การรวม Plex เป็นชั้นเสริมแบบเลือกได้ ไม่ใช่สิ่งจำเป็นสำหรับการเล่นหลัก

## ✴️ คุณสมบัติ

- 🎬 ไลบรารีสื่อแบบ local / NAS ที่กระจายอยู่ในหลายโฟลเดอร์
- 🌄 การสร้าง thumbnail / poster และเฟรมพรีวิว
- 🔐 โฟลเดอร์ส่วนตัวพร้อมการปลดล็อกตามอุปกรณ์
- 🔗 รองรับการใช้งานหลัง reverse proxy ภายใต้ path prefix เช่น `http://192.168.1.100/movie/`
- 📽️ กลยุทธ์การเล่นแบบผสม: เล่นตรง, แปลงรหัสในเครื่องแบบในตัวสำหรับ `.mkv` และ `.ts`, หรือ HLS proxy ผ่าน Plex สลับได้ง่ายรายสื่อ
- 🌐 แคชรูปภาพของเบราว์เซอร์และแคชเมทาดาทาใน IndexedDB

---
→ ติดตั้งแบบวันไลเนอร์:
```
curl -fsSL https://raw.githubusercontent.com/daocha/plex-cat-theatre/main/install.sh | bash
```
---

## 🟢 ข้อกำหนด

### Python 3.9 หรือใหม่กว่า

แพ็กเกจ Python ปัจจุบัน:

- `Flask`
- `waitress`

### ไบนารีของระบบที่ต้องมีสำหรับการตรวจสอบข้อมูลเมตา พรีวิว ภาพย่อ และการแปลงรหัสในเครื่อง:

- `ffmpeg`
- `ffprobe`

ตรวจสอบว่าพร้อมใช้งาน:

```bash
which ffmpeg
which ffprobe
```

---

## 🚀 เริ่มต้นอย่างรวดเร็ว


### → ตัวเลือก A: ติดตั้งแบบวันไลเนอร์:
```
curl -fsSL https://raw.githubusercontent.com/daocha/plex-cat-theatre/main/install.sh | bash
```

### → ตัวเลือก B: ติดตั้งจาก PyPI ด้วย pip

```bash
pip install plex-cat-theatre
plex-cat-theatre-init
plex-cat-theatre --config ~/movies_config.json
```

### → ตัวเลือก C: วิธีเริ่มต้นที่แนะนำ

```bash
git clone https://github.com/daocha/plex-cat-theatre
cd plex-cat-theatre
./startup.sh
```

สคริปต์บูตสแตรปนี้สามารถ:

- สร้าง `movies_config.json` จาก config ตัวอย่างในการรันครั้งแรก
- สร้าง `.venv` ภายในเครื่อง
- ติดตั้ง dependency ของ Python ลงใน virtual environment ภายในเครื่องนั้น
- สร้างโฟลเดอร์ `cache/thumbnails` และ `logs` แบบอ้างอิงตามตำแหน่งไฟล์ config เมื่อจำเป็น
- ตรวจสอบ `ffmpeg` และ `ffprobe`
- ช่วยสร้างแฮชรหัสผ่านสำหรับโหมดส่วนตัวได้แบบเลือกทำ
- เริ่มเซิร์ฟเวอร์ด้วย config ภายในเครื่องของคุณ

คุณยังสามารถใช้ขั้นตอนแบบแมนนวลด้านล่างได้:

1. คัดลอก config ตัวอย่าง:

```bash
cp movies_config.sample.json movies_config.json
```

2. แก้ไข `movies_config.json` ให้เหมาะกับสภาพแวดล้อมของคุณ

### 🌐 เริ่มเซิร์ฟเวอร์:

```bash
# ถ้าคุณใช้ตัวเลือก A หรือ B ให้รัน
plex-cat-theatre --config ~/movies_config.json

# ถ้าคุณใช้ตัวเลือก C ให้รัน
python3 movies_server.py --config movies_config.json
```

เปิดหน้าจอ:

```text
http://localhost:9245
```
### 🔑 เปลี่ยน passcode
```bash
# ถ้าคุณใช้ตัวเลือก A หรือ B ให้รัน
plex-cat-theatre-passcode newpasscode

# ถ้าคุณใช้ตัวเลือก C ให้รัน
python3 passcode.py newpasscode
```
- โฟลเดอร์ส่วนตัวจะถูกซ่อนไว้จนกว่าอุปกรณ์จะได้รับอนุญาต
- สถานะการปลดล็อกผูกกับ device ID
- อุปกรณ์ที่ได้รับอนุมัติจะถูกเก็บฝั่งเซิร์ฟเวอร์
- สคริปต์นี้สามารถหมุนเปลี่ยน passcode ของโหมดส่วนตัวและล้างการอนุมัติเดิมได้

---

## 🗂️ โครงสร้างโปรเจกต์

- `movies_server.py`: จุดเข้า Flask และการเชื่อม route
- `movies_server_core.py`: ตัวช่วยร่วมของเซิร์ฟเวอร์สำหรับ auth, config, cookie และการจัดการ mount path
- `movies_catalog.py`: การสแกนแคตตาล็อก การสร้าง thumbnail การดึง subtitle และตัวช่วย local transcode
- `movies_server_plex.py`: ตัวเชื่อม Plex การแมป poster / subtitle และ Plex HLS proxy
- `movies.js`: ซอร์สโค้ด frontend
- `movies.min.js`: frontend bundle แบบ minified
- `movies.css`: สไตล์ของแกลเลอรีและตัวเล่น
- `passcode.py`: ตัวช่วยสำหรับหมุนเปลี่ยน passcode ของโหมดส่วนตัว

---

## ⚙️ การตั้งค่า

config ตัวอย่างถูกทำให้ปลอดข้อมูลจริงโดยตั้งใจ และไม่รวม:

- path ของระบบไฟล์จริง
- โทเค็น Plex จริง
- passcode hash จริง
- ค่าที่ผูกกับอุปกรณ์

### 📍 ฟิลด์สำคัญ

<table>
  <tr>
    <td width="200"><code>root</code></td>
    <td>media root ที่ต้องการสแกน (รองรับหลายโฟลเดอร์)</td>
  </tr>
  <tr>
    <td><code>thumbs_dir</code></td>
    <td>ไดเรกทอรีสำหรับ thumbnail และเฟรมพรีวิว ค่าเริ่มต้น: <code>./cache/thumbnails</code></td>
  </tr>
  <tr>
    <td><code>private_folder</code></td>
    <td>คำนำหน้าของโฟลเดอร์ที่ถือว่าเป็นส่วนตัว ตัวอย่าง <code>Personal</code> ทุกอย่างภายใต้โฟลเดอร์ <code>Personal</code> จะถูกล็อกจนกว่าคุณจะปลดล็อกจากหน้าจอใช้งาน</td>
  </tr>
  <tr>
    <td><code>private_passcode</code></td>
    <td>แฮช passcode ของโหมดส่วนตัว ไม่ควรอัปเดตตรงด้วย plain text หากต้องการเปลี่ยนให้ดูส่วน <code>เปลี่ยน passcode</code></td>
  </tr>
  <tr>
    <td><code>mount_script</code></td>
    <td>[ทางเลือก] คำสั่งที่ใช้เมื่อการเล่นไปเจอโฟลเดอร์สื่อที่หายไปเพราะ mount ถูกถอดออกโดยไม่ตั้งใจ</td>
  </tr>
  <tr>
    <td><code>transcode</code></td>
    <td>เปิด worker แปลงรหัสเบื้องหลังฝั่งแคตตาล็อกสำหรับคอนเทนเนอร์ต้นทางอย่าง `.mkv` และ `.ts`; สิ่งนี้อาจสร้างไฟล์สื่อ sidecar ที่ผ่านการแปลงรหัสแยกไว้ข้างไลบรารีต้นทาง จึงมักควรปล่อยไว้เป็น <code>false</code> โดยเฉพาะเมื่อเปิด Plex integration ค่าเริ่มต้น: <code>false</code></td>
  </tr>
  <tr>
    <td><code>auto_scan_on_start</code></td>
    <td>สแกนสื่อใหม่ตอนเริ่มระบบ ค่าเริ่มต้น: <code>false</code></td>
  </tr>
  <tr>
    <td><code>on_demand_transcode</code></td>
    <td>เปิดการแปลงรหัสตอนรันจริงใน player สำหรับคอนเทนเนอร์ต้นทาง โดยพยายามใช้ฮาร์ดแวร์เข้ารหัสก่อน และ fallback เป็นซอฟต์แวร์เมื่อจำเป็น ค่าเริ่มต้น: <code>true</code></td>
  </tr>
  <tr>
    <td><code>on_demand_hls</code></td>
    <td>เปิด playlist HLS แบบในตัวสำหรับคอนเทนเนอร์ต้นทาง ค่าเริ่มต้น: <code>true</code></td>
  </tr>
  <tr>
  <td><code>enable_plex_server</code></td>
  <td>📍 [ทางเลือก] เปิดการรวม Plex ค่าเริ่มต้น: <code>false</code> กรุณาตรวจสอบให้แน่ใจว่าได้ติดตั้งและตั้งค่า Plex Server อย่างถูกต้องก่อนเปิดใช้<br> เซิร์ฟเวอร์นี้รองรับ subtitle แบบ native แต่ถ้าคุณต้องการดึง subtitle อัตโนมัติ โดยมากควรใช้ Plex จะเหมาะกว่า
  <br> หากต้องการประสบการณ์ transcoding แบบ on-demand ที่ดีกว่า ขอแนะนำอย่างยิ่งให้ติดตั้ง Plex server เพื่อให้การสตรีมสื่อราบรื่นขึ้น<br>
  แม้ไม่มี Plex server เซิร์ฟเวอร์นี้ก็ยังทำงานได้ดี แต่โปรดทราบว่า:
  <br>→ สำหรับสื่อที่อุปกรณ์ของคุณเล่นได้ตรง ๆ ฟังก์ชัน seek จะทำงานได้สมบูรณ์
  <br>→ สำหรับสื่อที่อุปกรณ์ของคุณเล่นตรงไม่ได้ เช่น <code>h.265 พร้อมเสียง DTS</code> (h.265 ที่ใช้ AAC หรือ MP3 ไม่ได้รับผลกระทบ), <code>.mkv</code>, <code>.ts</code> หรือ <code>.wmv</code> เซิร์ฟเวอร์นี้ยังสามารถแปลงรหัสแบบ on-the-fly ได้ แต่ฟังก์ชัน seek อาจใช้งานไม่ได้
  </td>
  </tr>
  <tr>
    <td><code>plex.base_url</code></td>
    <td>Base URL ของ Plex server</td>
  </tr>
  <tr>
    <td><code>plex.token</code></td>
    <td>โทเค็น Plex</td>
  </tr>
  <tr>
    <td><code>debug_enabled</code></td>
    <td>แสดง debug overlay แบบในตัว</td>
  </tr>
  <tr>
    <td><code>direct_playback</code></td>
    <td>ออบเจ็กต์ที่มี <code>enabled</code> และ <code>audio_whitelist</code> เมื่อ <code>enabled=true</code> คุณจะเล่นสื่อด้วย native player ได้โดยไม่ต้องแปลงรหัส (เร็วกว่า) แนะนำให้ใช้ค่าปริยาย</td>
  </tr>
</table>

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

### 🅿️ พฤติกรรมการสแกนเมื่อใช้ Plex

- จะข้ามการสร้าง poster thumbnail แบบ local หากมี poster จาก Plex แล้ว
- thumbnail แบบ local ที่แคชไว้ก่อนหน้า ยังสามารถนำกลับมาใช้ต่อได้
- การสร้างเฟรมพรีวิวยังคงเปิดใช้งานอยู่
- การรวม Plex ยังคงเป็นทางเลือก และโหมด local-only ยังใช้งานได้

### → วิธีหาโทเค็น Plex

#### วิธีที่ 1: ใช้ Plex Web session ที่มีอยู่

1. เปิด Plex Web และลงชื่อเข้าใช้
2. เปิด developer tools ของเบราว์เซอร์
3. ไปที่แท็บเครือข่าย
4. รีเฟรชหน้า
5. ตรวจสอบ request ที่ถูกส่งไปยัง Plex server ของคุณ
6. หา `X-Plex-Token` ใน URL หรือ header

#### วิธีที่ 2: ดูจาก browser storage

ตรวจสอบ:

- พื้นที่เก็บข้อมูลในเครื่อง (`Local Storage`)
- พื้นที่เก็บข้อมูลของเซสชัน (`Session Storage`)
- URL และ header ของ request ใน DevTools

#### วิธีที่ 3: request ตรงจากเครื่องเดียวกัน

ถ้าคุณมี Plex Web session ที่ยังใช้งานอยู่บนเครื่องเดียวกัน ให้ตรวจสอบ request ของ Plex ใน DevTools แล้วมองหา:

```text
X-Plex-Token=...
```

‼️ ข้อควรระวังด้านความปลอดภัย:

- ให้ถือว่าโทเค็น Plex มีความสำคัญเหมือนรหัสผ่าน
- อย่า commit มันลง git
- เก็บไว้เฉพาะใน `movies_config.json`

---

## 🎥 โหมดการเล่น

### 1. การเล่นตรงแบบ native

ใช้กับไฟล์ที่ปลอดภัยสำหรับเบราว์เซอร์ เช่น `.mp4`, `.m4v`, `.webm`

พฤติกรรม:

- เสิร์ฟไฟล์ local โดยตรงจาก `/video/<id>`
- รองรับ HTTP range request
- หลีกเลี่ยง overhead จากการแปลงรหัส เมื่อเบราว์เซอร์เล่นไฟล์นั้นแบบ native ได้

เหมาะที่สุดสำหรับ:

- ไฟล์ตระกูล MP4 / H.264
- เบราว์เซอร์ที่รองรับการเล่นไฟล์นั้นได้อยู่แล้ว
- ไฟล์ที่ codec เสียงตรงกับ direct-play whitelist

### 2. การแปลงรหัสในเครื่องแบบในตัวโดยไม่ใช้ Plex

นี่คือเส้นทาง fallback เมื่อ Plex ไม่ได้เปิดใช้ หรือเมื่อคุณต้องการคงระบบให้เป็น local ล้วน ๆ

การทำงานปัจจุบัน:

- `.mkv` และ `.ts` สามารถถูกเปิดเป็น local HLS ที่ `/hls/<id>/index.m3u8`
- ไฟล์เดียวกันยังสามารถสตรีมเป็น fragmented MP4 จาก `/video/<id>?fmp4=1`
- HLS segment จะถูกสร้างตามต้องการด้วย `ffmpeg`
- สามารถลองใช้ hardware encode ก่อน แล้ว fallback ไป `libx264`
- เอาต์พุต fMP4 ถูกสร้างด้วย `libx264` และ AAC

### 3. การเล่นที่พึ่ง Plex

เมื่อเปิด Plex integration:

- frontend สามารถใช้ `plex_stream_url` สำหรับการเล่นที่ให้ความสำคัญกับความเข้ากันได้
- Plex จะสร้าง upstream HLS playlist
- เซิร์ฟเวอร์นี้จะ rewrite playlist และ proxy request ของ playlist และ segment ที่ซ้อนกัน
- เบราว์เซอร์ยังคงคุยกับแอปนี้ ไม่ได้คุยกับ Plex โดยตรง

เหมาะที่สุดสำหรับ:

- เนื้อหา MKV หรือ TS บนอุปกรณ์ที่รองรับ codec หรือ container ได้ไม่ดีนัก
- กรณีที่ต้องการให้ Plex ช่วยเลือก subtitle หรือ normalize stream

### นโยบายการเลือกเส้นทางการเล่น

- direct playback จะถูกเลือกก่อนสำหรับไฟล์ที่ปลอดภัยกับเบราว์เซอร์และมี codec เสียงตรงกับ `direct_playback.audio_whitelist`
- Plex ยังคงเป็นตัวเลือกที่ถูกให้ความสำคัญกว่าสำหรับ `.mkv`, `.ts`, HLS, fMP4 หรือ codec เสียงที่ไม่รองรับ
- จังหวะ fallback HLS แบบ native บน iOS จะรอนานกว่า เพื่อให้ Plex stream มีเวลาวอร์มอัป

### ตรรกะการเล่นเริ่มต้น

- `Direct` จะถูกเลือกก่อนสำหรับ `.mp4`, `.m4v`, `.webm`, `.avi` เมื่อ direct URL เป็น path ของไฟล์จริง และ codec เสียงอยู่ใน whitelist ที่ปลอดภัย
- ถ้าข้อมูล metadata ของ codec เสียงหายไปสำหรับนามสกุลที่ปลอดภัยกับเบราว์เซอร์เหล่านี้ แอปก็ยังคงเลือก `Direct`
- `Plex` จะถูกเลือกก่อนสำหรับ `.mkv`, `.ts`, direct URL แบบ HLS / fMP4 และไฟล์ที่ codec เสียงที่ทราบว่าอยู่นอก whitelist
- ถ้าไม่มีไฟล์ที่ match กับ Plex แอปจะ fallback ไป `Direct`

---

## โมเดลการยืนยันตัวตน

แอปนี้ใช้วิธีส่งข้อมูลต่างกันตามประเภทของ request:

- API request ใช้ header `X-Device-Id`
- HLS และ Plex proxy request ใช้ header `X-Device-Id`
- native direct media request ใช้ cookie fallback `movies_device_id`

การแยกแบบนี้มีขึ้นเพราะ request แบบ native `<video src="...">` ไม่สามารถแนบ custom header ตามต้องการได้

---

## รองรับ Reverse Proxy และ Context Path

แอปรองรับการใช้งานภายใต้ subpath เช่น:

- `https://example.com/movie/`
- `https://example.com/cinema/`

ระบบ routing จะคง mount prefix ปัจจุบันไว้สำหรับ:

- สื่อที่เล่นโดยตรง
- HLS ภายในเครื่อง
- คำขอ Plex HLS proxy
- asset ของ poster และ subtitle

---

## การเข้าถึง Plex ระยะไกลด้วย Tailscale

หากอินเทอร์เฟซที่ปรับแต่งเองเข้าถึงได้จากภายนอก แต่ Plex เข้าถึงได้เฉพาะใน private LAN เครื่องที่รัน movies server ก็ยังต้องเข้าถึง Plex backend ได้โดยตรง

### โฮสต์เดียวกัน

```json
"plex": {
  "base_url": "http://127.0.0.1:32400"
}
```

### Plex อยู่บนเครื่องอื่นใน LAN

โฆษณา route จาก Tailscale node ที่เข้าถึง Plex ได้:

```bash
sudo tailscale up --advertise-routes=192.168.50.0/24
```

จากนั้นตรวจสอบการเข้าถึงจากเครื่องที่รัน movies server:

```bash
curl http://192.168.50.10:32400/identity
```

📌 หมายเหตุ:

- เบราว์เซอร์ไม่จำเป็นต้องเข้าถึง Plex โดยตรง
- process ของ movies server ต้องเข้าถึง `plex.base_url` ได้
- ชื่อ reverse proxy หรือ MagicDNS ของอินเทอร์เฟซไม่ได้ทำให้ Plex เข้าถึงได้เอง

---

## 💾 กลยุทธ์การแคช

### การแคชรูปภาพ

thumbnail, เฟรมพรีวิว และภาพ poster ของ Plex จะถูกเสิร์ฟพร้อม immutable cache header แบบอายุยาว

### การแคชเมทาดาทา

snapshot เมทาดาทาของแกลเลอรีจะถูกแคชไว้ใน IndexedDB พร้อมการจำกัดพื้นที่จัดเก็บ:

- TTL 1 วัน
- สูงสุด 8 snapshot
- ขนาดรวมโดยประมาณไม่เกิน 18 MB
- รายการที่เก่ากว่าจะถูกลบเมื่อเกินขีดจำกัด

ในแต่ละ snapshot ที่ถูกแคช จะเก็บ:

- `catalogStatus` ของเซิร์ฟเวอร์
- แคชรายการโฟลเดอร์
- `videos` ที่โหลดแล้ว
- ตัวนับ pagination เช่น `serverTotal`, `serverOffset`, และ `serverExhausted`

การลบข้อมูลเก่าเป็นแบบ opportunistic ไม่ใช่แบบตามตาราง:

- รายการหมดอายุจะถูกลบตอนอ่าน หรือในการ pruning ภายหลัง
- การ pruning จะรันหลังจากบันทึก snapshot ใหม่
- แรงกดดันด้านพื้นที่จัดเก็บของเบราว์เซอร์ หรือการล้าง site data ด้วยตนเอง ก็อาจลบข้อมูล IndexedDB ได้เช่นกัน

---

## 🔍 พฤติกรรมการสแกน

การสแกนแคตตาล็อกถูกออกแบบให้ต้นทุนเพิ่มแบบ incremental แม้ว่าจะยังคงต้องเดินทุก root ที่ตั้งค่าไว้

พฤติกรรมปัจจุบัน:

- ไฟล์ที่ไม่เปลี่ยนแปลงจะใช้ signature `mtime + size` ที่แคชไว้ซ้ำ
- การสแกนตามรอบจะไม่ sort รายการ path ทั้งหมดก่อนประมวลผลอีกต่อไป
- ไฟล์ที่ถูกลบจะถูกลบออกจากแคตตาล็อกในหน่วยความจำและดัชนีที่บันทึกไว้
- ไฟล์ที่ถูกลบยังทำให้เกิดการ cleanup ของ thumbnail และ preview ที่เคยสร้างไว้
- การบันทึกดัชนีจะใช้ข้อมูล signature ของไฟล์ที่แคชไว้ซ้ำ แทนที่จะ `stat` ทุกไฟล์ใหม่

สิ่งที่การสแกนยังคงทำ:

- เดิน media root ที่ตั้งค่าไว้เพื่อหาไฟล์ที่เพิ่ม เปลี่ยน หรือถูกลบ
- เข้าคิวการสร้าง preview เมื่อภาพพรีวิวหายไป

สิ่งที่การสแกนไม่ทำ:

- ไม่คำนวณ checksum ของไฟล์สื่อขนาดใหญ่ระหว่างการสแกนตามรอบ
- ไม่สร้าง thumbnail หรือ metadata ใหม่ให้ไฟล์ที่ไม่เปลี่ยน หาก artefact ที่แคชไว้ยังอยู่

### → สั่ง Rescan

Rescan แบบ incremental ปกติ:

```bash
curl -s http://localhost:9245/rescan | python3 -m json.tool
```

Rescan แบบเต็มที่บังคับ:

```bash
curl -s "http://localhost:9245/rescan?full=1" | python3 -m json.tool
```

### → หน้าจอ Rescan

ปุ่ม `Rescan` จะเปิด action dialog แทนที่จะเริ่ม incremental scan ทันที

ตัวเลือกที่มี:

- `Rescan`: สแกนแบบ incremental สำหรับไฟล์ใหม่หรือไฟล์ที่เปลี่ยน
- `Full Scan`: ล้างสถานะการสแกนที่บันทึกไว้ และบังคับตรวจสอบ metadata ใหม่ทั้งหมด
- `Refresh Database`: ล้าง snapshot ใน IndexedDB ของเบราว์เซอร์ และโหลดข้อมูลแคตตาล็อกใหม่

### ⛓️‍💥 การกู้คืน mount ที่หายไป

ฟีเจอร์นี้ออกแบบมาสำหรับกรณีที่ NAS บางตัวตั้งค่า sleep อัตโนมัติไว้ ทำให้ SMB mount อาจถูก eject อัตโนมัติโดยบางระบบปฏิบัติการ

ถ้าตั้งค่า `mount_script` ไว้ และ media request ไปเจอโฟลเดอร์ที่หายไป เซิร์ฟเวอร์จะ:

1. ตรวจพบว่าโฟลเดอร์แม่ไม่มีอยู่
2. เรียก mount script ที่ตั้งค่าไว้หนึ่งครั้ง
3. ตรวจสอบ path เป้าหมายอีกครั้ง
4. ส่งกลับ `Media folder is not mounted` พร้อม HTTP 404 ก็ต่อเมื่อโฟลเดอร์ยังใช้งานไม่ได้จริง

ฝั่ง frontend จะถือว่า playback 404 เป็นข้อผิดพลาดสุดท้ายของความพยายามครั้งนั้น และจะแสดงข้อความให้ลองใหม่ แทนการยิงซ้ำไปที่เซิร์ฟเวอร์อย่างต่อเนื่อง

---

## 📄 ไฟล์ที่ถูกสร้างขึ้น

ไฟล์เหล่านี้ถูกสร้างขึ้นตอนรัน และไม่ควร commit:

- `movies_config.json`
- `movies_state.json`
- `movies_auth_state.json`
- `movies_catalog_index.json`
- `cache/`

---

## 🛠️ การแก้ปัญหา


### → Debug Overlay

เปิด `debug_enabled` ใน `movies_config.json` เพื่อให้มี debug overlay แบบถาวรที่มุมล่างขวา

แผงนี้จะแสดง:

- ว่าเซิร์ฟเวอร์กำลังให้ความสำคัญกับ direct playback หรือ Plex
- direct-play audio whitelist ที่ตั้งค่าไว้
- ตัวเลือกการเล่นปัจจุบันและ video ID
- เมตริกความคืบหน้าการสแกนล่าสุด

ตรวจสอบค่าคอนฟิกที่ใช้งานอยู่ด้วย:

```bash
curl -s http://localhost:9245/api/config | python3 -m json.tool
```

### → การเปลี่ยนแปลงหน้าจอไม่แสดงผล

- ตอนนี้แอปโหลด `movies.js` โดยตรงจาก `index.html` ดังนั้นการเปลี่ยน frontend จะมีผลโดยไม่ต้อง build `movies.min.js` ใหม่
- ลองรีเฟรชหน้าแบบปกติก่อน
- ถ้า JS bundle ถูกเปลี่ยน ให้ตรวจสอบว่า `index.html` อ้างอิงเวอร์ชัน bundle ที่ถูกต้อง

### → Direct playback ของโหมดส่วนตัวใช้ไม่ได้

- ปลดล็อกโหมดส่วนตัวอีกครั้งเพื่อรีเฟรช cookie `movies_device_id`

### → Plex playback ใช้ไม่ได้ แต่ direct playback ใช้ได้

- ตรวจสอบว่า host ของ movies server เข้าถึง `plex.base_url` ได้
- ตรวจสอบว่าเปิด Plex ใน config แล้ว
- ตรวจสอบว่า token ที่ตั้งค่าไว้ยังใช้งานได้

### → Direct playback ใช้ไม่ได้ แต่ Plex ใช้ได้

- container หรือ codec นั้นอาจไม่ปลอดภัยสำหรับ native browser playback บนอุปกรณ์นั้น
- ให้ใช้ Plex ต่อสำหรับไฟล์เหล่านั้น หรือบังคับเส้นทางที่เข้ากันได้ผ่าน local transcode หรือ Plex

### → Local transcoding ใช้ไม่ได้

- ตรวจสอบว่าติดตั้ง `ffmpeg` และ `ffprobe` แล้ว
- ตรวจสอบว่าเปิด `on_demand_transcode` แล้ว
- ตรวจสอบว่าไฟล์ต้นทางเป็นหนึ่งใน container ที่รองรับอยู่ตอนนี้: `.mkv` หรือ `.ts`

---

## 📦 การกำหนดเวอร์ชันรีลีส

เวอร์ชันของแพ็กเกจมาจาก Git tag

- TestPyPI / testing: ใช้เวอร์ชันพัฒนา เช่น `2026.3.26.dev1`
- PyPI prerelease: ใช้ release candidate เช่น `2026.3.26rc1`
- PyPI stable: ใช้เวอร์ชันเสถียร เช่น `2026.3.26`
- Git tag ควรเป็น `v2026.3.26.dev1`, `v2026.3.26rc1`, และ `v2026.3.26`
  
---

## ©️ ใบอนุญาต

โปรเจกต์นี้เผยแพร่ภายใต้ MIT License เมื่อเผยแพร่หรือแจกจ่ายต่อ ให้เพิ่มไฟล์ `LICENSE` ที่มีข้อความ MIT ครบถ้วน
