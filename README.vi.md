# Cat Theatre Movies Server

> Máy chủ duyệt phim và phát trực tuyến tự lưu trữ gọn nhẹ được xây dựng bằng Flask, Waitress và `ffmpeg`, với tích hợp _`Plex`_ tùy chọn cho lộ trình phát ưu tiên tính tương thích.

---

![Screenshot 2026-03-22 at 9 39 12 PM](https://github.com/user-attachments/assets/124f21b7-71b0-46fc-9d76-c73f700c25f3)

---

**Ngôn ngữ**

[English](./README.md) | [简体中文](./README.zh-CN.md) | [繁體中文（香港）](./README.zh-HK.md) | [繁體中文（台灣）](./README.zh-TW.md) | [Français](./README.fr.md) | [한국어](./README.ko.md) | [日本語](./README.ja.md) | [Deutsch](./README.de.md) | [ไทย](./README.th.md) | `Tiếng Việt` | [Nederlands](./README.nl.md)

---

## Tổng Quan

Cat Theatre được thiết kế có chủ đích để nhẹ:

- bề mặt phụ thuộc Python nhỏ
- không cần cơ sở dữ liệu
- lập danh mục dựa trên hệ thống tệp
- dùng luồng quét polling có thể di chuyển thay vì phụ thuộc vào watcher riêng của hệ điều hành
- tích hợp Plex là một lớp tùy chọn chứ không bắt buộc cho phát lõi

Nó được thiết kế cho:

- thư viện media cục bộ trải trên một hoặc nhiều thư mục
- tạo thumbnail và khung xem trước
- kiểm soát truy cập thư mục riêng tư theo thiết bị
- triển khai sau reverse proxy dưới một tiền tố như `/movie/`
- chiến lược phát hỗn hợp: phát trực tiếp tệp, transcoding cục bộ tích hợp, hoặc HLS dựa trên Plex

---

## Tính Năng

- quét media nhiều thư mục gốc
- tạo thumbnail poster và khung xem trước
- thư mục riêng tư với cơ chế mở khóa theo thiết bị
- phát trực tiếp native cho các định dạng an toàn với trình duyệt
- transcoding cục bộ tích hợp cho `.mkv` và `.ts` khi được bật
- tích hợp Plex cho phát, poster, phụ đề và proxy HLS
- routing nhận biết context path cho reverse proxy
- bộ nhớ đệm ảnh của trình duyệt cùng bộ nhớ đệm metadata trong IndexedDB

### Ghi Chú Về UX Và Phát

- bảng debug tích hợp nằm ở góc dưới bên phải và có thể trượt về cạnh gần nhất
- phát sẽ tự động ưu tiên đường đi an toàn hơn cho tệp và thiết bị hiện tại
- ghi đè Direct/Plex thủ công được lưu theo từng video trong IndexedDB
- thumbnail và metadata được cache sẽ nằm trong giới hạn lưu trữ của trình duyệt

---

## Yêu Cầu

### Python

```bash
pip install -r requirements.txt
```

Các gói Python hiện tại:

- `Flask`
- `waitress`

### Công Cụ Hệ Thống

Cần cho dò metadata, preview, thumbnail và transcoding cục bộ:

- `ffmpeg`
- `ffprobe`

Kiểm tra chúng có sẵn:

```bash
which ffmpeg
which ffprobe
```

---

## Bắt Đầu Nhanh

Cách khởi động được khuyến nghị:

```bash
./startup.sh
```

Script bootstrap này có thể:

- tạo `movies_config.json` từ config mẫu trong lần chạy đầu tiên
- tạo `.venv` cục bộ
- cài đặt các dependency Python vào môi trường ảo cục bộ đó
- kiểm tra `ffmpeg` và `ffprobe`
- tùy chọn hỗ trợ tạo hash passcode cho chế độ riêng tư
- khởi động server bằng config cục bộ của bạn

Bạn vẫn có thể dùng quy trình thủ công bên dưới:

1. Sao chép file config mẫu:

```bash
cp movies_config.sample.json movies_config.json
```

2. Chỉnh sửa `movies_config.json` cho môi trường của bạn.

3. Khởi động server:

```bash
python3 movies_server.py --config movies_config.json
```

4. Mở UI:

```text
http://localhost:9245
```

Nếu bạn triển khai ứng dụng sau reverse proxy dưới một tiền tố như `/movie/`, hãy mở URL có tiền tố đó.

---

## Cấu Trúc Dự Án

- `movies_server.py`: entrypoint Flask và nối route
- `movies_server_core.py`: helper dùng chung phía server cho auth, config, cookie và xử lý mount path
- `movies_catalog.py`: quét catalog, tạo thumbnail, trích xuất phụ đề và helper transcoding cục bộ
- `movies_server_plex.py`: adapter Plex, ánh xạ poster/phụ đề và proxy Plex HLS
- `movies.js`: mã nguồn frontend
- `movies.min.js`: bundle frontend đã minify
- `movies.css`: style của gallery và player
- `passcode.py`: helper để xoay vòng passcode chế độ riêng tư

---

## Cấu Hình

Config mẫu đã được làm sạch có chủ đích và không bao gồm:

- đường dẫn hệ thống tệp thật
- Plex token thật
- passcode thật
- giá trị dành riêng cho thiết bị

### Trường Quan Trọng

- `root`: các thư mục gốc media để quét
- `thumbs_dir`: thư mục cho thumbnail và khung preview
- `private_folder`: các tiền tố thư mục được xem là riêng tư
- `private_passcode`: hash passcode của chế độ riêng tư
- `mount_script`: lệnh tùy chọn dùng khi phát chạm vào thư mục media bị thiếu
- `transcode`: bật worker transcoding nền ở phía catalog cho các source container như `.mkv` và `.ts`; việc này có thể tạo ra các tệp sidecar đã transcoded riêng nằm cạnh thư viện media, vì vậy thường nên để là `false`, đặc biệt khi đã bật tích hợp Plex
- `auto_scan_on_start`: quét lại media khi khởi động
- `on_demand_transcode`: bật transcoding lúc chạy phía player cho container nguồn, ưu tiên dùng mã hóa phần cứng khi có và fallback sang mã hóa phần mềm khi cần
- `on_demand_hls`: bật playlist HLS tích hợp cho container nguồn
- `enable_plex_server`: bật tích hợp Plex
- `plex.base_url`: URL gốc của Plex server
- `plex.token`: Plex token
- `debug_enabled`: hiển thị lớp phủ debug tích hợp
- `direct_playback`: object có `enabled` và `audio_whitelist`

### Ví Dụ Tối Thiểu Chỉ Cục Bộ

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

### Ví Dụ Tích Hợp Plex

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

### Hành Vi Quét Plex

- bỏ qua việc tạo thumbnail poster cục bộ khi có poster Plex
- thumbnail cục bộ đã được cache vẫn có thể tái sử dụng
- việc tạo khung preview vẫn được bật
- tích hợp Plex vẫn là tùy chọn và chế độ chỉ cục bộ vẫn hoạt động

### Cách Lấy Plex Token

#### Cách 1: Phiên Plex Web Hiện Có

1. Mở Plex Web và đăng nhập.
2. Mở công cụ dành cho nhà phát triển của trình duyệt.
3. Vào tab Network.
4. Tải lại trang.
5. Kiểm tra một request được gửi đến Plex server của bạn.
6. Tìm `X-Plex-Token` trong URL hoặc header.

#### Cách 2: Bộ Nhớ Trình Duyệt

Kiểm tra:

- Local Storage
- Session Storage
- URL và header của request trong DevTools

#### Cách 3: Request Cục Bộ Trực Tiếp

Nếu bạn đã có phiên Plex Web đang hoạt động trên cùng máy, hãy kiểm tra các request Plex trong DevTools và tìm:

```text
X-Plex-Token=...
```

Lưu ý bảo mật:

- coi Plex token như mật khẩu
- không commit nó vào git
- chỉ giữ nó trong `movies_config.json`

---

## Chế Độ Phát

### 1. Phát Trực Tiếp Native

Được dùng cho các tệp an toàn với trình duyệt như `.mp4`, `.m4v`, `.webm`.

Hành vi:

- phục vụ tệp cục bộ trực tiếp từ `/video/<id>`
- hỗ trợ HTTP range requests
- tránh overhead transcoding khi trình duyệt có thể phát tệp trực tiếp

Phù hợp nhất cho:

- tệp kiểu MP4/H.264
- trình duyệt đã hỗ trợ phát trực tiếp tệp đó
- tệp có codec âm thanh khớp với whitelist direct-play

### 2. Transcoding Cục Bộ Tích Hợp Không Dùng Plex

Đây là đường fallback khi Plex không được bật, hoặc khi bạn muốn giữ mọi thứ hoàn toàn cục bộ.

Triển khai hiện tại:

- `.mkv` và `.ts` có thể được cung cấp dưới dạng HLS cục bộ tại `/hls/<id>/index.m3u8`
- các tệp đó cũng có thể được stream dưới dạng fragmented MP4 qua `/video/<id>?fmp4=1`
- các segment HLS được tạo theo nhu cầu bằng `ffmpeg`
- có thể thử hardware encode trước rồi fallback về `libx264`
- đầu ra fMP4 được tạo bằng `libx264` cộng AAC

### 3. Phát Dựa Trên Plex

Khi tích hợp Plex được bật:

- frontend có thể dùng `plex_stream_url` cho phát ưu tiên tương thích
- Plex tạo playlist HLS upstream
- server này sẽ viết lại playlist và proxy các request playlist lồng nhau cùng segment
- trình duyệt vẫn nói chuyện với ứng dụng này chứ không trực tiếp với Plex

Phù hợp nhất cho:

- nội dung MKV hoặc TS trên thiết bị hỗ trợ codec hoặc container yếu hơn
- trường hợp muốn ưu tiên việc chọn phụ đề hoặc chuẩn hóa stream của Plex

### Chính Sách Chọn Phát

- direct playback được ưu tiên cho các tệp an toàn với trình duyệt có codec âm thanh khớp `direct_playback.audio_whitelist`
- Plex vẫn được ưu tiên cho `.mkv`, `.ts`, HLS, fMP4 hoặc codec âm thanh không được hỗ trợ
- thời gian fallback HLS native trên iOS dài hơn để cho stream Plex có thời gian khởi động

### Logic Phát Mặc Định

- `Direct` được ưu tiên cho `.mp4`, `.m4v`, `.webm`, `.avi` khi direct URL là đường dẫn tệp thật và codec âm thanh an toàn theo whitelist
- nếu metadata codec âm thanh bị thiếu đối với một trong các phần mở rộng an toàn với trình duyệt đó, ứng dụng vẫn ưu tiên `Direct`
- `Plex` được ưu tiên cho `.mkv`, `.ts`, direct URL dạng HLS/fMP4 và các tệp có codec âm thanh đã biết nằm ngoài whitelist
- nếu không có bản khớp Plex, ứng dụng sẽ fallback về `Direct`

---

## Lớp Phủ Debug

Bật `debug_enabled` trong `movies_config.json` để giữ một lớp phủ debug cố định ở góc dưới bên phải.

Bảng này hiển thị:

- server đang thiên về direct playback hay Plex
- whitelist codec âm thanh direct-play đã cấu hình
- candidate phát hiện tại và video ID
- các chỉ số tiến độ quét gần đây

Kiểm tra giá trị config đang hoạt động bằng:

```bash
curl -s http://localhost:9245/api/config | python3 -m json.tool
```

Nếu bạn phục vụ ứng dụng dưới `/movie/`, hãy dùng đường dẫn có prefix.

---

## Mô Hình Xác Thực

Ứng dụng dùng các phương thức vận chuyển khác nhau tùy theo loại request:

- request API dùng header `X-Device-Id`
- request HLS và Plex proxy dùng header `X-Device-Id`
- request media direct native dùng cookie `movies_device_id` làm fallback

Việc tách này tồn tại vì request `<video src="...">` native không thể đính kèm custom header tùy ý.

---

## Hỗ Trợ Reverse Proxy Và Context Path

Ứng dụng hỗ trợ triển khai dưới các subpath như:

- `https://example.com/movie/`
- `https://example.com/cinema/`

Routing sẽ giữ mount prefix hiện tại cho:

- media direct
- HLS cục bộ
- request Plex HLS proxy
- tài nguyên poster và phụ đề

---

## Truy Cập Plex Từ Xa Bằng Tailscale

Nếu UI tùy chỉnh có thể truy cập từ xa nhưng Plex chỉ truy cập được trong LAN riêng, máy chủ chạy movies server vẫn phải truy cập trực tiếp backend Plex.

### Cùng Một Máy

```json
"plex": {
  "base_url": "http://127.0.0.1:32400"
}
```

### Plex Trên Máy LAN Khác

Quảng bá route từ một node Tailscale có thể truy cập Plex:

```bash
sudo tailscale up --advertise-routes=192.168.50.0/24
```

Sau đó xác minh khả năng truy cập từ máy chủ movies server:

```bash
curl http://192.168.50.10:32400/identity
```

Lưu ý:

- trình duyệt không cần truy cập mạng trực tiếp đến Plex
- tiến trình movies server phải truy cập được `plex.base_url`
- reverse proxy hoặc tên MagicDNS cho UI không tự làm Plex trở nên truy cập được

---

## Chiến Lược Bộ Nhớ Đệm

### Bộ Nhớ Đệm Ảnh

Thumbnail, khung preview và ảnh poster Plex được phục vụ với header cache immutable thời gian dài.

### Bộ Nhớ Đệm Metadata

Snapshot metadata của gallery được cache trong IndexedDB với giới hạn dung lượng:

- TTL 1 ngày
- tối đa 8 bản ghi snapshot
- tổng kích thước ước tính khoảng 18 MB
- các mục cũ hơn sẽ bị loại bỏ khi vượt giới hạn

Mỗi snapshot được cache lưu:

- `catalogStatus` của server
- cache danh sách thư mục
- `videos` đã nạp
- các bộ đếm phân trang như `serverTotal`, `serverOffset`, `serverExhausted`

Việc loại bỏ mang tính cơ hội thay vì theo lịch:

- các mục hết hạn bị xóa khi đọc hoặc khi prune sau đó
- prune chạy sau khi lưu snapshot mới
- áp lực lưu trữ của trình duyệt hoặc việc xóa site data thủ công cũng có thể xóa dữ liệu IndexedDB

---

## Hành Vi Quét

Quét catalog được thiết kế để giữ chi phí ở mức tăng dần dù vẫn đi qua từng root đã cấu hình.

Hành vi hiện tại:

- các tệp không đổi tái sử dụng chữ ký `mtime + size` đã cache
- quét định kỳ không còn sort toàn bộ danh sách đường dẫn trước khi xử lý
- các tệp đã xóa bị loại khỏi catalog trong bộ nhớ và index đã lưu
- các tệp đã xóa cũng kích hoạt việc dọn dẹp thumbnail và preview đã tạo
- việc lưu index tái sử dụng dữ liệu chữ ký tệp đã cache thay vì stat lại từng tệp

Những gì việc quét vẫn làm:

- đi qua các root media đã cấu hình để phát hiện tệp thêm mới, thay đổi và xóa
- đưa vào hàng đợi việc tạo preview khi thiếu ảnh preview

Những gì nó không làm:

- không checksum các tệp media lớn trong các lần quét định kỳ
- không tạo lại thumbnail hoặc metadata cho tệp không đổi trừ khi thiếu artifact trong cache

### Bắt Buộc Full Rescan

Sử dụng:

```text
/rescan?full=1
```

Hữu ích khi:

- ai đó đã xóa thủ công thư mục cache thumbnail hoặc preview
- bạn nghi ngờ manifest quét đã lưu bị cũ
- bạn muốn buộc xác thực lại toàn bộ trạng thái được suy ra từ quá trình quét

### Kiểm Tra Trạng Thái Quét

```bash
curl -s http://localhost:9245/api/status | python3 -m json.tool
```

Nếu bạn phục vụ ứng dụng dưới `/movie/`, hãy dùng đường dẫn có prefix.

### Kích Hoạt Quét Lại

Rescan tăng dần thông thường:

```bash
curl -s http://localhost:9245/rescan | python3 -m json.tool
```

Full rescan bắt buộc:

```bash
curl -s "http://localhost:9245/rescan?full=1" | python3 -m json.tool
```

### UI Rescan

Nút `Rescan` mở một hộp thoại hành động thay vì bắt đầu quét tăng dần ngay lập tức.

Các hành động có sẵn:

- `Rescan`: quét tăng dần cho tệp mới hoặc đã thay đổi
- `Full Scan`: xóa trạng thái quét đã lưu và buộc xác thực lại metadata hoàn toàn
- `Refresh Database`: xóa snapshot IndexedDB của trình duyệt và tải lại dữ liệu catalog mới

### Khôi Phục Khi Thiếu Mount

Nếu `mount_script` được cấu hình và một request media gặp thư mục bị thiếu, server sẽ:

1. phát hiện thư mục cha không tồn tại
2. gọi mount script đã cấu hình một lần
3. kiểm tra lại đường dẫn đích
4. chỉ trả về `Media folder is not mounted` cùng HTTP 404 nếu thư mục vẫn không khả dụng

Frontend coi 404 khi phát là trạng thái kết thúc cho lần thử đó và hiển thị thông báo thử lại thay vì liên tục đánh vào server.

---

## Ghi Chú Phát Triển Frontend

Ứng dụng hiện tải `movies.js` trực tiếp từ `index.html`, vì vậy thay đổi frontend có hiệu lực mà không cần build lại `movies.min.js`.

---

## Chế Độ Riêng Tư

- thư mục riêng tư sẽ bị ẩn cho đến khi thiết bị được cấp quyền
- trạng thái mở khóa gắn với một device ID
- các thiết bị đã được chấp thuận được lưu phía server
- `passcode.py` có thể đổi passcode của chế độ riêng tư và xóa các phê duyệt

Ví dụ:

```bash
python3 passcode.py mynewpasscode
```

---

## Tệp Được Tạo Ra

Những tệp này được tạo lúc chạy và không nên commit:

- `movies_config.json`
- `movies_state.json`
- `movies_auth_state.json`
- `movies_catalog_index.json`
- `cache/`

---

## Khắc Phục Sự Cố

### Thay Đổi UI Không Xuất Hiện

- trước tiên hãy refresh trang bình thường
- nếu bundle JS đã thay đổi, hãy xác nhận `index.html` đang tham chiếu đúng phiên bản bundle mong muốn

### Direct Playback Riêng Tư Thất Bại

- mở khóa lại chế độ riêng tư để cookie `movies_device_id` được làm mới

### Plex Playback Thất Bại Nhưng Direct Playback Hoạt Động

- xác minh máy chủ movies server có thể truy cập `plex.base_url`
- xác minh Plex đã được bật trong config
- xác minh token đã cấu hình là hợp lệ

### Direct Playback Thất Bại Nhưng Plex Playback Hoạt Động

- container hoặc codec đó có thể không an toàn cho phát native của trình duyệt trên thiết bị đó
- hãy giữ Plex cho các tệp đó, hoặc buộc đường phát tương thích qua transcoding cục bộ hoặc Plex

### Local Transcoding Không Hoạt Động

- xác minh `ffmpeg` và `ffprobe` đã được cài đặt
- xác minh `on_demand_transcode` đã được bật
- xác minh tệp nguồn thuộc các container hiện được hỗ trợ: `.mkv` hoặc `.ts`

---

## Giấy Phép

Kho này hiện chưa khai báo giấy phép phần mềm. Hãy thêm rõ ràng nếu bạn định phân phối lại nó.
