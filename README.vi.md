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
  <p><strong>Siêu nhẹ, chế độ riêng tư 🔐, đa thiết bị, phát trực tuyến thông minh</strong></p>
  <p>Không cần ứng dụng. Cài server đơn giản. Giao diện thân thiện với điện thoại, giúp kết nối NAS ở mọi nơi, với tích hợp Plex tùy chọn</p>
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



> Không có phụ thuộc nặng, mọi thứ đều minh bạch. Máy chủ duyệt phim và phát trực tuyến tự lưu trữ gọn nhẹ được xây dựng bằng Flask, Waitress và `ffmpeg`, với tích hợp _`Plex`_ tùy chọn cho lộ trình phát ưu tiên tính tương thích.

---

![Screenshot 2026-03-22 at 9 39 12 PM](https://github.com/user-attachments/assets/124f21b7-71b0-46fc-9d76-c73f700c25f3)

---

## ✨ Vì sao nên dùng

Cat Theatre được thiết kế có chủ đích để nhẹ:

- 🩷 _Truy cập từ xa_ không cần gói thuê bao Plex 💰
- ✅ Bề mặt phụ thuộc Python nhỏ
- ✅ Không cần cơ sở dữ liệu
- ✅ Lập danh mục dựa trên hệ thống tệp
- ✅ Tương thích với 🖥️ desktop, 📱 điện thoại và máy tính bảng
- ✅ Dùng luồng quét polling có thể di chuyển thay vì phụ thuộc vào watcher riêng của hệ điều hành
- 🔶 Tích hợp Plex là lớp tùy chọn chứ không bắt buộc cho phát lõi

## ✴️ Tính năng

- 🎬 Thư viện media cục bộ / NAS trải trên nhiều thư mục
- 🌄 Tạo thumbnail / poster và khung xem trước
- 🔐 Thư mục riêng tư với mở khóa theo thiết bị
- 🔗 Triển khai sau reverse proxy với tiền tố đường dẫn như `http://192.168.1.100/movie/`
- 📽️ Chiến lược phát hỗn hợp: phát trực tiếp, transcoding cục bộ tích hợp cho `.mkv` và `.ts`, hoặc proxy HLS dựa trên Plex. Dễ chuyển theo từng media
- 🌐 Bộ nhớ đệm ảnh của trình duyệt cùng bộ nhớ đệm metadata trong IndexedDB

---
→ Cài đặt bằng one-liner:
```
curl -fsSL https://raw.githubusercontent.com/daocha/plex-cat-theatre/main/install.sh | bash
```
---

## 🟢 Yêu cầu

### Python 3.9 trở lên

Các gói Python hiện tại:

- `Flask`
- `waitress`

### Công cụ hệ thống cần thiết cho dò metadata, preview, thumbnail và transcoding cục bộ:

- `ffmpeg`
- `ffprobe`

Kiểm tra chúng có sẵn:

```bash
which ffmpeg
which ffprobe
```

---

## 🚀 Bắt đầu nhanh


### → Tùy chọn A: cài đặt bằng one-liner:
```
curl -fsSL https://raw.githubusercontent.com/daocha/plex-cat-theatre/main/install.sh | bash
```

### → Tùy chọn B: cài từ PyPI bằng pip

```bash
pip install plex-cat-theatre
plex-cat-theatre-init
plex-cat-theatre --config ~/movies_config.json
```

### → Tùy chọn C: cách khởi động được khuyến nghị

```bash
git clone https://github.com/daocha/plex-cat-theatre
cd plex-cat-theatre
./startup.sh
```

Script bootstrap này có thể:

- tạo `movies_config.json` từ config mẫu trong lần chạy đầu tiên
- tạo `.venv` cục bộ
- cài đặt các dependency Python vào môi trường ảo cục bộ đó
- tạo các thư mục `cache/thumbnails` và `logs` theo vị trí file config khi cần
- kiểm tra `ffmpeg` và `ffprobe`
- tùy chọn hỗ trợ tạo hash passcode cho chế độ riêng tư
- khởi động server với cấu hình cục bộ của bạn

Bạn vẫn có thể dùng luồng thủ công bên dưới:

1. Sao chép config mẫu:

```bash
cp movies_config.sample.json movies_config.json
```

2. Chỉnh `movies_config.json` cho phù hợp môi trường của bạn.

### 🌐 Khởi động server:

```bash
# nếu bạn dùng tùy chọn A hoặc B thì chạy
plex-cat-theatre --config ~/movies_config.json

# nếu bạn dùng tùy chọn C thì chạy
python3 movies_server.py --config movies_config.json
```

Mở giao diện:

```text
http://localhost:9245
```
### 🔑 Đổi passcode
```bash
# nếu bạn dùng tùy chọn A hoặc B thì chạy
plex-cat-theatre-passcode newpasscode

# nếu bạn dùng tùy chọn C thì chạy
python3 passcode.py newpasscode
```
- thư mục riêng tư sẽ bị ẩn cho đến khi thiết bị được cấp quyền
- trạng thái mở khóa gắn với một device ID
- thiết bị đã được chấp thuận được lưu phía server
- script có thể xoay passcode của chế độ riêng tư và xóa các quyền đã cấp

---

## 🗂️ Cấu trúc dự án

- `movies_server.py`: entrypoint Flask và phần nối route
- `movies_server_core.py`: helper server dùng chung cho auth, config, cookie và xử lý mount path
- `movies_catalog.py`: quét catalog, tạo thumbnail, trích xuất phụ đề và helper transcoding cục bộ
- `movies_server_plex.py`: adapter Plex, ánh xạ poster / phụ đề và proxy Plex HLS
- `movies.js`: mã nguồn frontend
- `movies.min.js`: bundle frontend đã nén
- `movies.css`: style của gallery và player
- `passcode.py`: helper để xoay passcode cho chế độ riêng tư

---

## ⚙️ Cấu hình

Config mẫu đã được làm sạch có chủ đích và không bao gồm:

- đường dẫn hệ thống tệp thật
- token Plex thật
- passcode hash thật
- giá trị đặc thù theo thiết bị

### 📍 Trường quan trọng

<table>
  <tr>
    <td width="200"><code>root</code></td>
    <td>các thư mục gốc media cần quét (hỗ trợ nhiều thư mục)</td>
  </tr>
  <tr>
    <td><code>thumbs_dir</code></td>
    <td>thư mục cho thumbnail và khung preview. Mặc định: <code>./cache/thumbnails</code></td>
  </tr>
  <tr>
    <td><code>private_folder</code></td>
    <td>tiền tố thư mục được xem là riêng tư. Ví dụ: <code>Personal</code>. Mọi thứ bên dưới thư mục <code>Personal</code> sẽ bị khóa cho đến khi bạn mở khóa từ giao diện.</td>
  </tr>
  <tr>
    <td><code>private_passcode</code></td>
    <td>hash passcode cho chế độ riêng tư; bạn không nên cập nhật trực tiếp bằng văn bản thuần. Nếu muốn thay đổi, hãy xem phần <code>Đổi passcode</code>.</td>
  </tr>
  <tr>
    <td><code>mount_script</code></td>
    <td>[tùy chọn] Lệnh dùng khi phát hiện thư mục media bị thiếu do mount bị ngắt ngoài ý muốn.</td>
  </tr>
  <tr>
    <td><code>transcode</code></td>
    <td>Bật worker transcoding nền phía catalog cho các container nguồn như `.mkv` và `.ts`; việc này có thể tạo thêm file sidecar đã transcoding bên cạnh thư viện nguồn, nên thường tốt nhất là để <code>false</code>, đặc biệt khi đã bật tích hợp Plex. Mặc định: <code>false</code></td>
  </tr>
  <tr>
    <td><code>auto_scan_on_start</code></td>
    <td>Quét lại media khi khởi động. Mặc định: <code>false</code></td>
  </tr>
  <tr>
    <td><code>on_demand_transcode</code></td>
    <td>Bật transcoding lúc chạy trong player cho các container nguồn, ưu tiên mã hóa phần cứng nếu có và rơi về phần mềm khi cần. Mặc định: <code>true</code></td>
  </tr>
  <tr>
    <td><code>on_demand_hls</code></td>
    <td>Bật playlist HLS tích hợp cho các container nguồn. Mặc định: <code>true</code></td>
  </tr>
  <tr>
  <td><code>enable_plex_server</code></td>
  <td>📍 [tùy chọn] Bật tích hợp Plex. Mặc định: <code>false</code>. Hãy chắc chắn Plex Server đã được cài và cấu hình đúng trước khi bật tùy chọn này.<br> Server này hỗ trợ phụ đề native, nhưng nếu bạn muốn tự động lấy phụ đề thì thường nên dùng Plex.
  <br> Nếu bạn muốn trải nghiệm transcoding theo yêu cầu tốt hơn, rất nên cài Plex server để có luồng phát media mượt hơn.<br>
  Ngay cả khi không có Plex server, server này vẫn hoạt động tốt, nhưng lưu ý:
  <br>→ Với media mà thiết bị của bạn phát trực tiếp được, chức năng tua sẽ hoạt động bình thường.
  <br>→ Với media mà thiết bị không phát trực tiếp được, ví dụ <code>h.265 với âm thanh DTS</code> (h.265 với AAC hoặc MP3 không bị ảnh hưởng), <code>.mkv</code>, <code>.ts</code> hoặc <code>.wmv</code>, server vẫn có thể transcoding tức thời nhưng chức năng tua có thể không khả dụng.
  </td>
  </tr>
  <tr>
    <td><code>plex.base_url</code></td>
    <td>URL gốc của Plex server.</td>
  </tr>
  <tr>
    <td><code>plex.token</code></td>
    <td>Mã token Plex</td>
  </tr>
  <tr>
    <td><code>debug_enabled</code></td>
    <td>Hiển thị lớp phủ debug tích hợp</td>
  </tr>
  <tr>
    <td><code>direct_playback</code></td>
    <td>Đối tượng gồm <code>enabled</code> và <code>audio_whitelist</code>. Khi <code>enabled=true</code>, bạn có thể phát bằng player native mà không cần transcoding (nhanh). Khuyến nghị giữ cấu hình mặc định.</td>
  </tr>
</table>

### Ví dụ tối thiểu chỉ chạy local

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

### Ví dụ có tích hợp Plex

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

### 🅿️ Hành vi quét với Plex

- bỏ qua việc tạo poster thumbnail cục bộ nếu poster Plex đã có
- thumbnail cục bộ đã cache vẫn có thể được tái sử dụng
- việc tạo khung preview vẫn được bật
- tích hợp Plex vẫn là tùy chọn và chế độ local-only vẫn hoạt động

### → Cách lấy mã token Plex

#### Cách 1: Phiên Plex Web hiện có

1. Mở Plex Web và đăng nhập.
2. Mở developer tools của trình duyệt.
3. Vào tab mạng.
4. Tải lại trang.
5. Kiểm tra một request được gửi tới Plex server của bạn.
6. Tìm `X-Plex-Token` trong URL hoặc header.

#### Cách 2: Bộ nhớ trình duyệt

Kiểm tra:

- bộ nhớ cục bộ (`Local Storage`)
- bộ nhớ phiên (`Session Storage`)
- URL và header request trong DevTools

#### Cách 3: Request cục bộ trực tiếp

Nếu bạn đã có phiên Plex Web đang hoạt động trên cùng máy, hãy kiểm tra các request Plex trong DevTools và tìm:

```text
X-Plex-Token=...
```

‼️ Lưu ý bảo mật:

- hãy coi mã token Plex như mật khẩu
- đừng commit nó vào git
- chỉ lưu nó trong `movies_config.json`

---

## 🎥 Chế độ phát

### 1. Phát trực tiếp native

Dùng cho các tệp an toàn với trình duyệt như `.mp4`, `.m4v` và `.webm`.

Hành vi:

- phục vụ trực tiếp tệp cục bộ từ `/video/<id>`
- hỗ trợ HTTP range request
- tránh chi phí transcoding khi trình duyệt có thể phát file một cách native

Phù hợp nhất với:

- file kiểu MP4 / H.264
- trình duyệt đã hỗ trợ phát trực tiếp file đó
- file có codec âm thanh khớp với direct-play whitelist

### 2. Transcoding cục bộ tích hợp không cần Plex

Đây là đường lui khi Plex không bật, hoặc khi bạn muốn giữ mọi thứ hoàn toàn local.

Triển khai hiện tại:

- `.mkv` và `.ts` có thể được cung cấp dưới dạng HLS cục bộ tại `/hls/<id>/index.m3u8`
- cùng các file đó cũng có thể được stream dưới dạng fragmented MP4 từ `/video/<id>?fmp4=1`
- các đoạn HLS được tạo theo yêu cầu bằng `ffmpeg`
- có thể thử mã hóa phần cứng trước rồi fallback sang `libx264`
- đầu ra fMP4 được tạo bằng `libx264` cùng AAC

### 3. Phát dựa trên Plex

Khi tích hợp Plex được bật:

- frontend có thể dùng `plex_stream_url` cho đường phát cần ưu tiên tương thích
- Plex tạo playlist HLS phía upstream
- server này sẽ viết lại playlist và proxy các request playlist lồng nhau cùng segment
- trình duyệt vẫn nói chuyện với ứng dụng này chứ không trực tiếp với Plex

Phù hợp nhất với:

- nội dung MKV hoặc TS trên thiết bị có hỗ trợ codec hoặc container yếu hơn
- trường hợp muốn Plex xử lý chọn phụ đề hoặc chuẩn hóa luồng

### Chính sách chọn đường phát

- phát trực tiếp được ưu tiên cho các file an toàn với trình duyệt có codec âm thanh khớp `direct_playback.audio_whitelist`
- Plex vẫn được ưu tiên cho `.mkv`, `.ts`, HLS, fMP4 hoặc codec âm thanh không được hỗ trợ
- thời gian chờ fallback HLS native trên iOS dài hơn để Plex stream có thời gian warm up

### Logic phát mặc định

- `Direct` được ưu tiên cho `.mp4`, `.m4v`, `.webm` và `.avi` khi URL trực tiếp là đường dẫn file thật và codec âm thanh nằm trong whitelist
- nếu metadata codec âm thanh bị thiếu cho một trong các phần mở rộng an toàn với trình duyệt đó, ứng dụng vẫn ưu tiên `Direct`
- `Plex` được ưu tiên cho `.mkv`, `.ts`, URL trực tiếp HLS / fMP4 và các file có codec âm thanh đã biết nằm ngoài whitelist
- nếu không có bản khớp Plex, ứng dụng sẽ fallback về `Direct`

---

## Mô hình xác thực

Ứng dụng dùng các cách truyền khác nhau tùy loại request:

- request API dùng header `X-Device-Id`
- request HLS và Plex proxy dùng header `X-Device-Id`
- request media native direct dùng fallback cookie `movies_device_id`

Sự tách biệt này tồn tại vì request `<video src="...">` native không thể gắn các custom header tùy ý.

---

## Hỗ trợ reverse proxy và context path

Ứng dụng hỗ trợ triển khai dưới các subpath như:

- `https://example.com/movie/`
- `https://example.com/cinema/`

Routing sẽ giữ nguyên mount prefix hiện tại cho:

- media trực tiếp
- HLS cục bộ
- request proxy HLS của Plex
- tài nguyên poster và phụ đề

---

## Truy cập Plex từ xa với Tailscale

Nếu giao diện tùy biến truy cập được từ xa nhưng Plex chỉ truy cập được trong LAN riêng, máy chủ movies server vẫn phải có khả năng kết nối trực tiếp tới backend Plex.

### Cùng một host

```json
"plex": {
  "base_url": "http://127.0.0.1:32400"
}
```

### Plex trên một máy LAN khác

Quảng bá route từ một node Tailscale có thể tới Plex:

```bash
sudo tailscale up --advertise-routes=192.168.50.0/24
```

Sau đó kiểm tra khả năng truy cập từ host chạy movies server:

```bash
curl http://192.168.50.10:32400/identity
```

📌 Lưu ý:

- trình duyệt không cần truy cập mạng trực tiếp tới Plex
- tiến trình movies server phải truy cập được `plex.base_url`
- tên reverse proxy hoặc MagicDNS cho giao diện không tự làm Plex trở nên truy cập được

---

## 💾 Chiến lược cache

### Cache hình ảnh

Thumbnail, khung preview và ảnh poster Plex được phục vụ với cache header immutable có thời hạn dài.

### Bộ nhớ đệm metadata

Ảnh chụp metadata của gallery được cache trong IndexedDB với giới hạn lưu trữ:

- TTL 1 ngày
- tối đa 8 bản snapshot
- tổng kích thước ước tính khoảng 18 MB
- bản cũ hơn sẽ bị loại bỏ khi vượt giới hạn

Mỗi snapshot được cache lưu:

- `catalogStatus` của server
- cache danh sách thư mục
- `videos` đã tải
- các bộ đếm phân trang như `serverTotal`, `serverOffset`, và `serverExhausted`

Việc loại bỏ là cơ hội, không theo lịch:

- mục hết hạn sẽ bị xóa khi đọc hoặc trong lần dọn dẹp sau
- dọn dẹp chạy sau khi lưu snapshot mới
- áp lực lưu trữ của trình duyệt hoặc việc xóa dữ liệu site thủ công cũng có thể xóa dữ liệu IndexedDB

---

## 🔍 Hành vi quét

Việc quét catalog được thiết kế để chi phí vẫn tăng theo hướng gia tăng dù nó vẫn đi qua từng root đã cấu hình.

Hành vi hiện tại:

- file không đổi sẽ tái sử dụng chữ ký `mtime + size` đã cache
- các lần quét định kỳ không còn sắp xếp toàn bộ danh sách đường dẫn trước khi xử lý
- file đã xóa bị loại khỏi catalog trong bộ nhớ và chỉ mục lưu bền
- file đã xóa cũng kích hoạt việc dọn dẹp thumbnail và preview được tạo ra
- khi lưu chỉ mục, hệ thống tái sử dụng dữ liệu chữ ký file đã cache thay vì `stat` lại mọi file

Những gì quá trình quét vẫn làm:

- đi qua các media root đã cấu hình để phát hiện file mới, thay đổi và đã xóa
- đưa việc tạo preview vào hàng đợi khi thiếu ảnh preview

Những gì nó không làm:

- không tính checksum cho các file media lớn trong các lần quét định kỳ
- không tạo lại thumbnail hay metadata cho file không đổi nếu các artefact đã cache vẫn còn

### → Kích hoạt quét lại

Quét lại gia tăng thông thường:

```bash
curl -s http://localhost:9245/rescan | python3 -m json.tool
```

Quét lại toàn bộ có ép buộc:

```bash
curl -s "http://localhost:9245/rescan?full=1" | python3 -m json.tool
```

### → Giao diện Rescan

Nút `Rescan` sẽ mở hộp thoại hành động thay vì lập tức bắt đầu quét gia tăng.

Các hành động khả dụng:

- `Rescan`: quét gia tăng cho file mới hoặc đã thay đổi
- `Full Scan`: xóa trạng thái quét đã lưu và ép kiểm định lại toàn bộ metadata
- `Refresh Database`: xóa các snapshot IndexedDB của trình duyệt và nạp lại dữ liệu catalog mới

### ⛓️‍💥 Phục hồi mount bị mất

Tính năng này dành cho trường hợp một số NAS được cấu hình ngủ tự động, khiến SMB mount có thể bị hệ điều hành tự động ngắt.

Nếu `mount_script` được cấu hình và một request media chạm vào thư mục bị thiếu, server sẽ:

1. phát hiện thư mục cha không tồn tại
2. gọi script mount đã cấu hình một lần
3. kiểm tra lại đường dẫn đích
4. chỉ trả về `Media folder is not mounted` với HTTP 404 nếu thư mục vẫn không khả dụng

Frontend coi 404 trong lúc phát là lỗi cuối cùng cho lần thử đó và hiển thị thông báo thử lại thay vì liên tục đập request vào server.

---

## 📄 Tệp được tạo ra

Những tệp sau được tạo trong lúc chạy và không nên commit:

- `movies_config.json`
- `movies_state.json`
- `movies_auth_state.json`
- `movies_catalog_index.json`
- `cache/`

---

## 🛠️ Khắc phục sự cố


### → Lớp phủ debug

Bật `debug_enabled` trong `movies_config.json` để giữ lớp phủ debug cố định ở góc dưới bên phải.

Bảng này hiển thị:

- server đang ưu tiên phát trực tiếp hay Plex
- direct-play audio whitelist hiện được cấu hình
- ứng viên phát hiện tại và video ID
- các chỉ số tiến độ quét gần đây

Kiểm tra giá trị config đang có hiệu lực bằng:

```bash
curl -s http://localhost:9245/api/config | python3 -m json.tool
```

### → Thay đổi giao diện không xuất hiện

- Ứng dụng hiện tải `movies.js` trực tiếp từ `index.html`, nên thay đổi frontend có hiệu lực mà không cần build lại `movies.min.js`.
- trước tiên hãy refresh trang bình thường
- nếu bundle JS đã thay đổi, hãy xác nhận `index.html` đang tham chiếu tới đúng phiên bản bundle mong muốn

### → Phát trực tiếp nội dung riêng tư bị lỗi

- hãy mở khóa lại chế độ riêng tư để làm mới cookie `movies_device_id`

### → Plex phát lỗi nhưng phát trực tiếp vẫn chạy

- xác minh host chạy movies server có thể truy cập `plex.base_url`
- xác minh Plex được bật trong config
- xác minh token đã cấu hình là hợp lệ

### → Phát trực tiếp lỗi nhưng Plex vẫn chạy

- container hoặc codec đó có thể không an toàn cho phát native trên trình duyệt của thiết bị
- hãy giữ Plex cho những file đó, hoặc ép đường tương thích thông qua transcoding cục bộ hoặc Plex

### → Transcoding cục bộ không hoạt động

- xác minh `ffmpeg` và `ffprobe` đã được cài
- xác minh `on_demand_transcode` đang bật
- xác minh file nguồn thuộc một trong các container hiện hỗ trợ: `.mkv` hoặc `.ts`

---

## 📦 Quy ước phiên bản phát hành

Phiên bản gói được suy ra từ Git tag.

- TestPyPI / testing: dùng phiên bản phát triển như `2026.3.26.dev1`
- Bản prerelease trên PyPI: dùng release candidate như `2026.3.26rc1`
- Bản stable trên PyPI: dùng phiên bản ổn định như `2026.3.26`
- Git tag nên là `v2026.3.26.dev1`, `v2026.3.26rc1`, và `v2026.3.26`
  
---

## ©️ Giấy phép

Dự án này được phát hành theo MIT License. Khi phát hành hoặc phân phối lại, hãy thêm tệp `LICENSE` chứa toàn văn MIT.
