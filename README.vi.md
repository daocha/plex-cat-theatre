# Máy chủ phim Cat Theatre

> Máy chủ duyệt và phát phim tự lưu trữ, gọn nhẹ, dùng Flask, Waitress và `ffmpeg`.

[English](./README.md)

---

## Tính năng chính

- quét thư viện nhiều thư mục gốc
- tạo thumbnail và khung xem trước
- mở khóa thư mục riêng tư theo thiết bị
- phát trực tiếp, chuyển mã cục bộ, hoặc phát qua Plex
- hỗ trợ prefix reverse proxy như `/movie/`

---

## Khởi động nhanh

```bash
cp movies_config.sample.json movies_config.json
python3 movies_server.py --config movies_config.json
```

Mở:

```text
http://localhost:9245
```

---

## Cấu hình quan trọng

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

## Chế độ phát

### Phát trực tiếp

- phù hợp với `.mp4`, `.m4v`, `.webm`
- đường dẫn: `/video/<id>`

### Chuyển mã cục bộ

- HLS: `/hls/<id>/index.m3u8`
- fMP4: `/video/<id>?fmp4=1`

### Plex

- Plex HLS
- poster Plex
- phụ đề Plex

---

## Lệnh kiểm tra

```bash
python3 -m py_compile movies_server.py movies_server_core.py movies_server_plex.py movies_catalog.py
node --check movies.js
```
