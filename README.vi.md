# Cat Theatre Movies Server

> Máy chủ duyệt và phát phim tự lưu trữ được xây dựng bằng Flask, Waitress và `ffmpeg`, với tích hợp Plex tùy chọn cho khả năng phát tương thích hơn.

**Ngôn ngữ**

[English](./README.md) | `Tiếng Việt`

---

## Tổng quan

Cat Theatre được giữ nhẹ:

- ít phụ thuộc Python
- không cần cơ sở dữ liệu
- quản lý thư viện theo hệ thống tệp
- quét kiểu polling, dễ di chuyển
- Plex là tùy chọn

Phù hợp cho:

- thư viện media nội bộ nằm ở nhiều thư mục
- tạo ảnh thu nhỏ và ảnh xem trước
- thư mục riêng tư theo thiết bị
- triển khai sau reverse proxy với tiền tố như `/movie/`
- direct play, transcoding cục bộ và Plex HLS

---

## Tính năng

- quét nhiều thư mục gốc
- ảnh poster thu nhỏ và khung xem trước
- thư mục riêng tư
- direct play gốc
- transcoding cục bộ cho `.mkv` và `.ts`
- tích hợp Plex
- hỗ trợ subpath qua reverse proxy
- cache ảnh trình duyệt và cache IndexedDB

---

## Cấu trúc dự án

- `movies_server.py`
- `movies_server_core.py`
- `movies_catalog.py`
- `movies_server_plex.py`
- `movies.js`
- `movies.min.js`
- `movies.css`
- `passcode.py`

---

## Yêu cầu

```bash
pip install -r requirements.txt
which ffmpeg
which ffprobe
```

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

## Cấu hình

Các trường quan trọng:

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

## Chế độ phát

- direct play: `/video/<id>`
- transcoding cục bộ: `/hls/<id>/index.m3u8` hoặc `/video/<id>?fmp4=1`
- phát qua Plex: Plex tạo HLS, ứng dụng này proxy lại

### Logic phát mặc định

- `Direct` được ưu tiên cho `.mp4`, `.m4v`, `.webm` và `.avi` khi direct URL là đường dẫn tệp thật và codec âm thanh nằm trong whitelist
- nếu metadata âm thanh bị thiếu với các phần mở rộng an toàn cho trình duyệt này, ứng dụng vẫn ưu tiên `Direct`
- `Plex` được ưu tiên cho `.mkv`, `.ts`, direct URL kiểu HLS/fMP4 và các tệp có codec âm thanh đã biết nằm ngoài whitelist
- nếu không có Plex match, ứng dụng sẽ fallback sang `Direct`

---

## Cache và quét

- ảnh dùng cache dài hạn
- snapshot IndexedDB có TTL 1 ngày
- tối đa 8 snapshot
- khoảng 18 MB tổng dung lượng
- `/rescan?full=1` để ép xác thực lại toàn bộ

---

## Chế độ riêng tư và debug

- thư mục riêng tư bị ẩn mặc định
- trạng thái mở khóa gắn với thiết bị
- `passcode.py` có thể đổi passcode
- `debug_enabled` hiển thị bảng debug

---

## Khắc phục sự cố

- nếu Plex lỗi, kiểm tra `plex.base_url` và token
- nếu transcoding cục bộ lỗi, kiểm tra `ffmpeg`, `ffprobe`, `on_demand_transcode`
