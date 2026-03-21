# เซิร์ฟเวอร์หนัง Cat Theatre

> เซิร์ฟเวอร์ดูและสตรีมหนังแบบ self-hosted ที่เบา ใช้ Flask, Waitress และ `ffmpeg`

[English](./README.md)

---

## ความสามารถหลัก

- สแกนคลังจากหลายโฟลเดอร์
- สร้างภาพย่อและภาพพรีวิว
- ปลดล็อกโฟลเดอร์ส่วนตัวตามอุปกรณ์
- เล่นตรง, ทรานส์โค้ดในเครื่อง, หรือเล่นผ่าน Plex
- รองรับ reverse proxy prefix เช่น `/movie/`

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

## ค่าตั้งสำคัญ

- `root`
- `thumbs_dir`
- `private_folder`
- `private_passcode`
- `mount_script`
- `enable_plex_server`
- `direct_playback`
- `plex.base_url`
- `plex.token`

---

## โหมดการเล่น

### เล่นตรง

- เหมาะกับ `.mp4`, `.m4v`, `.webm`
- เส้นทาง: `/video/<id>`

### ทรานส์โค้ดในเครื่อง

- HLS: `/hls/<id>/index.m3u8`
- fMP4: `/video/<id>?fmp4=1`

### Plex

- Plex HLS
- โปสเตอร์ Plex
- ซับไตเติล Plex

---

## คำสั่งตรวจสอบ

```bash
python3 -m py_compile movies_server.py movies_server_core.py movies_server_plex.py movies_catalog.py
node --check movies.js
```
