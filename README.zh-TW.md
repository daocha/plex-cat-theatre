# Cat Theatre Movies Server

> 以 Flask、Waitress 和 `ffmpeg` 建構的輕量級自架電影瀏覽與串流伺服器，並可選擇整合 _`Plex`_，以提供更著重相容性的播放方案。

---

![Screenshot 2026-03-22 at 9 39 12 PM](https://github.com/user-attachments/assets/124f21b7-71b0-46fc-9d76-c73f700c25f3)

---

**語言**

[English](https://github.com/daocha/plex-cat-theatre/blob/main/README.md) | [简体中文](https://github.com/daocha/plex-cat-theatre/blob/main/README.zh-CN.md) | [繁體中文（香港）](https://github.com/daocha/plex-cat-theatre/blob/main/README.zh-HK.md) | `繁體中文（台灣）` | [Français](https://github.com/daocha/plex-cat-theatre/blob/main/README.fr.md) | [한국어](https://github.com/daocha/plex-cat-theatre/blob/main/README.ko.md) | [日本語](https://github.com/daocha/plex-cat-theatre/blob/main/README.ja.md) | [Deutsch](https://github.com/daocha/plex-cat-theatre/blob/main/README.de.md) | [ไทย](https://github.com/daocha/plex-cat-theatre/blob/main/README.th.md) | [Tiếng Việt](https://github.com/daocha/plex-cat-theatre/blob/main/README.vi.md) | [Nederlands](https://github.com/daocha/plex-cat-theatre/blob/main/README.nl.md)

---

## 概覽

Cat Theatre 刻意保持輕量：

- Python 依賴少
- 不需要資料庫
- 以檔案系統為核心進行目錄整理
- 使用可攜式輪詢掃描流程，而不是依賴作業系統專屬的檔案監看
- Plex 整合是可選加層，而非核心播放所必需

它適用於：

- 分散在一個或多個資料夾中的本機媒體庫
- 縮圖與預覽影格產生
- 以裝置為基礎的私密資料夾存取控制
- 透過如 `/movie/` 這類路徑前綴在反向代理後部署
- 混合播放策略：直接檔案播放、內建本機轉碼，或 Plex HLS 播放

---

## 功能

- 多根目錄媒體掃描
- 海報縮圖與預覽影格產生
- 以裝置解鎖的私密資料夾
- 支援瀏覽器安全格式的原生直接播放
- 啟用時為 `.mkv` 和 `.ts` 提供內建本機轉碼
- Plex 整合，支援播放、海報、字幕與 HLS 代理
- 為反向代理提供內容路徑感知路由
- 瀏覽器圖片快取與 IndexedDB 中繼資料快取

### 介面與播放說明

- 內建偵錯面板位於右下角，並可滑向最近邊緣
- 播放會自動為目前檔案與裝置優先選擇較穩妥的路徑
- 手動 Direct/Plex 覆寫會按影片儲存在 IndexedDB
- 快取的縮圖與中繼資料會維持在瀏覽器儲存空間限制內

---

## 需求

### Python

```bash
pip install -r requirements.txt
```

目前 Python 套件：

- `Flask`
- `waitress`

### 系統二進位工具

中繼資料探測、預覽、縮圖與本機轉碼需要：

- `ffmpeg`
- `ffprobe`

確認它們可用：

```bash
which ffmpeg
which ffprobe
```

---

## 快速開始

如果你安裝的是已發佈到 PyPI 的套件，請使用：

```bash
pip install plex-cat-theatre
plex-cat-theatre-init
plex-cat-theatre --config ~/movies_config.json
```

首選啟動方式：

```bash
./startup.sh
```

這個啟動腳本可以：

- 首次執行時根據範例設定建立 `movies_config.json`
- 建立本地 `.venv`
- 將 Python 依賴安裝到這個本地虛擬環境
- 在需要時按設定檔位置建立 `cache/thumbnails` 與 `logs` 資料夾
- 檢查 `ffmpeg` 和 `ffprobe`
- 可選地協助你產生私密模式密碼雜湊
- 以本地設定啟動伺服器

你仍然可以使用下面的手動流程：

1. 複製範例設定：

```bash
cp movies_config.sample.json movies_config.json
```

2. 依你的環境編輯 `movies_config.json`。

3. 啟動伺服器：

```bash
python3 movies_server.py --config movies_config.json
```

4. 開啟介面：

```text
http://localhost:9245
```

若你將應用透過反向代理部署在如 `/movie/` 這類前綴下，請改為開啟帶前綴的 URL。

---

## 專案結構

- `movies_server.py`：Flask 進入點與路由綁定
- `movies_server_core.py`：認證、設定、Cookie 與掛載路徑處理等共用伺服器輔助邏輯
- `movies_catalog.py`：目錄掃描、縮圖產生、字幕擷取與本機轉碼輔助邏輯
- `movies_server_plex.py`：Plex 介接器、海報/字幕映射與 Plex HLS 代理
- `movies.js`：前端原始碼
- `movies.min.js`：前端壓縮版本
- `movies.css`：圖庫與播放器樣式
- `passcode.py`：用於輪換私密模式密碼的輔助腳本

---

## 發佈版本規則

套件版本由 Git 標籤推導而來。

- TestPyPI/測試：使用如 `2026.3.26.dev1` 的開發版本
- PyPI 預發佈：使用如 `2026.3.26rc1` 的候選發佈版本
- PyPI 穩定版：使用如 `2026.3.26` 的穩定版本
- Git 標籤應為 `v2026.3.26.dev1`、`v2026.3.26rc1` 與 `v2026.3.26`

---

## 設定

範例設定已刻意清理，不包含：

- 真實檔案系統路徑
- 真實 Plex Token
- 真實密碼
- 裝置專屬值

### 重要欄位

- `root`：要掃描的媒體根目錄
- `thumbs_dir`：縮圖與預覽影格目錄
- `private_folder`：視為私密的資料夾前綴
- `private_passcode`：私密模式密碼雜湊
- `mount_script`：播放遇到遺失媒體資料夾時可呼叫的掛載腳本
- `transcode`：為 `.mkv`、`.ts` 等來源容器啟用目錄掃描端的背景轉碼工作程序；這可能會在媒體庫旁邊產生額外的轉碼檔案，因此通常建議保持為 `false`，尤其在啟用 Plex 整合時
- `auto_scan_on_start`：啟動時重新掃描媒體
- `on_demand_transcode`：為播放器執行期間啟用來源容器轉碼，可優先使用硬體編碼，不可用時再回退到軟體編碼
- `on_demand_hls`：為來源容器啟用內建 HLS 播放清單
- `enable_plex_server`：啟用 Plex 整合
- `plex.base_url`：Plex 伺服器基底 URL
- `plex.token`：Plex Token
- `debug_enabled`：顯示內建偵錯浮層
- `direct_playback`：包含 `enabled` 與 `audio_whitelist` 的物件

### 最小純本機示例

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

### 整合 Plex 的示例

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

### Plex 掃描行為

- 當 Plex 海報可用時，會跳過本機海報縮圖產生
- 已快取的本機縮圖仍可重用
- 預覽影格產生仍保持啟用
- Plex 整合仍為可選，純本機模式依然可用

### 如何取得 Plex Token

#### 方法 1：使用現有 Plex Web 工作階段

1. 開啟 Plex Web 並登入。
2. 開啟瀏覽器開發者工具。
3. 前往 Network 分頁。
4. 重新整理頁面。
5. 檢視發往 Plex 伺服器的請求。
6. 在 URL 或標頭中尋找 `X-Plex-Token`。

#### 方法 2：從瀏覽器儲存空間查看

檢查：

- Local Storage
- Session Storage
- DevTools 中的請求 URL 與標頭

#### 方法 3：直接本機請求

若你在同一台機器上已有 Plex Web 的有效工作階段，可在 DevTools 中檢查 Plex 請求並找出：

```text
X-Plex-Token=...
```

安全說明：

- 請把 Plex Token 當成密碼處理
- 不要提交到 git
- 只存放於 `movies_config.json`

---

## 播放模式

### 1. 原生直接播放

用於 `.mp4`、`.m4v`、`.webm` 等瀏覽器安全檔案。

行為：

- 直接由 `/video/<id>` 提供本機檔案
- 支援 HTTP Range 請求
- 當瀏覽器可原生播放檔案時，避免轉碼成本

最適合：

- MP4/H.264 類型檔案
- 瀏覽器本身已支援直接播放的檔案
- 音訊編碼符合 direct-play 白名單的檔案

### 2. 不依賴 Plex 的內建本機轉碼

這是未啟用 Plex 時的後備路徑，或你刻意希望完全維持本機方案時的路徑。

目前實作：

- `.mkv` 和 `.ts` 可透過 `/hls/<id>/index.m3u8` 作為本機 HLS 提供
- 同一類檔案也可透過 `/video/<id>?fmp4=1` 以 fragmented MP4 方式串流
- HLS 分段按需以 `ffmpeg` 產生
- 可先嘗試硬體編碼，再回退到 `libx264`
- fMP4 輸出使用 `libx264` 加 AAC 產生

### 3. Plex 支援的播放

啟用 Plex 整合後：

- 前端可使用 `plex_stream_url` 進行偏重相容性的播放
- Plex 會產生上游 HLS 播放清單
- 本伺服器會重寫播放清單，並代理巢狀播放清單與分段請求
- 瀏覽器仍只與此應用程式通訊，而非直接連到 Plex

最適合：

- 在編解碼器或容器支援較弱的裝置上播放 MKV 或 TS 內容
- 偏好由 Plex 負責字幕選擇或串流正規化的情況

### 播放選擇策略

- 對於音訊編碼符合 `direct_playback.audio_whitelist` 的瀏覽器安全檔案，直接播放優先
- 對於 `.mkv`、`.ts`、HLS、fMP4 或不受支援的音訊編碼，仍優先使用 Plex
- iOS 原生 HLS 後備的等待時間較長，讓 Plex 串流有時間預熱

### 預設播放邏輯

- 若直連 URL 為真實檔案路徑，且音訊編碼符合白名單，`.mp4`、`.m4v`、`.webm` 與 `.avi` 會優先使用 `Direct`
- 若上述瀏覽器安全副檔名缺少音訊編碼中繼資料，應用仍會優先使用 `Direct`
- 對於 `.mkv`、`.ts`、HLS/fMP4 直連 URL，以及已知音訊編碼不在白名單中的檔案，會優先使用 `Plex`
- 若沒有 Plex 對應，應用會回退至 `Direct`

---

## 偵錯浮層

在 `movies_config.json` 啟用 `debug_enabled`，即可於右下角保留常駐偵錯浮層。

面板會顯示：

- 伺服器目前偏向直接播放還是 Plex
- 已設定的 direct-play 音訊白名單
- 目前播放候選與影片 ID
- 最近的掃描進度指標

使用以下指令檢視目前設定值：

```bash
curl -s http://localhost:9245/api/config | python3 -m json.tool
```

若你透過 `/movie/` 提供服務，請使用帶前綴的路徑。

---

## 驗證模型

應用會依請求類型使用不同的傳輸方式：

- API 請求使用 `X-Device-Id` 標頭
- HLS 與 Plex 代理請求使用 `X-Device-Id` 標頭
- 原生直接媒體請求則使用 `movies_device_id` Cookie 作為後備

之所以這樣拆分，是因為原生 `<video src="...">` 請求無法附帶任意自訂標頭。

---

## 反向代理與內容路徑支援

本應用支援部署於以下子路徑：

- `https://example.com/movie/`
- `https://example.com/cinema/`

路由會保留目前掛載前綴，用於：

- 直接媒體
- 本機 HLS
- Plex HLS 代理請求
- 海報與字幕資產

---

## 透過 Tailscale 遠端存取 Plex

如果自訂 UI 可從遠端存取，但 Plex 僅能在私人 LAN 中存取，則 movies server 主機仍必須能直接連到 Plex 後端。

### 同一台主機

```json
"plex": {
  "base_url": "http://127.0.0.1:32400"
}
```

### Plex 位於另一台 LAN 機器

從可連到 Plex 的 Tailscale 節點廣播路由：

```bash
sudo tailscale up --advertise-routes=192.168.50.0/24
```

然後在 movies server 主機上確認可達性：

```bash
curl http://192.168.50.10:32400/identity
```

說明：

- 瀏覽器不需要能直接連到 Plex
- movies server 行程必須能連到 `plex.base_url`
- UI 的反向代理或 MagicDNS 名稱本身不會讓 Plex 自動可達

---

## 快取策略

### 圖片快取

縮圖、預覽影格與 Plex 海報圖片都會以長效 immutable 快取標頭提供。

### 中繼資料快取

圖庫中繼資料快照會以受限方式快取於 IndexedDB：

- 1 天 TTL
- 最多 8 份快照記錄
- 估算總大小上限約 18 MB
- 超出限制時會淘汰較舊項目

每份快取快照會儲存：

- 伺服器 `catalogStatus`
- 資料夾清單快取
- 已載入的 `videos`
- `serverTotal`、`serverOffset`、`serverExhausted` 等分頁計數器

淘汰是機會式進行，而非定時執行：

- 過期項目會在讀取時或後續清理時刪除
- 儲存新快照後會執行清理
- 瀏覽器儲存壓力或手動清除網站資料也可能移除 IndexedDB 資料

---

## 掃描行為

目錄掃描的設計是即使仍需走訪每個設定根目錄，成本仍能維持增量化。

目前行為：

- 未變更檔案會重用快取的 `mtime + size` 簽章
- 週期性掃描不再於處理前排序整份路徑清單
- 已刪除檔案會從記憶體目錄與持久化索引中移除
- 已刪除檔案也會觸發已生成縮圖與預覽資產的清理
- 儲存索引時會重用快取的檔案簽章資料，而不是再次對每個檔案做 stat

掃描仍會做的事：

- 走訪設定的媒體根目錄，以偵測新增、變更與刪除的檔案
- 當預覽圖缺失時，排入預覽圖產生工作

不會做的事：

- 週期性掃描不會對大型媒體檔案做校驗和
- 對於未變更檔案，除非快取資產缺失，否則不會重新產生縮圖或中繼資料

### 強制完整重掃

使用：

```text
/rescan?full=1
```

適用情況：

- 有人手動刪除了縮圖或預覽快取資料夾
- 你懷疑已儲存的掃描資訊已過時
- 你想強制重新驗證所有掃描衍生狀態

### 檢查掃描狀態

```bash
curl -s http://localhost:9245/api/status | python3 -m json.tool
```

若你透過 `/movie/` 提供服務，請使用帶前綴的路徑。

### 觸發重掃

一般增量重掃：

```bash
curl -s http://localhost:9245/rescan | python3 -m json.tool
```

強制完整重掃：

```bash
curl -s "http://localhost:9245/rescan?full=1" | python3 -m json.tool
```

### 重掃介面

`Rescan` 按鈕會開啟操作對話框，而非立即開始增量掃描。

可用操作：

- `Rescan`：針對新增或變更檔案執行增量掃描
- `Full Scan`：清除已儲存的掃描狀態，並強制完整重新驗證中繼資料
- `Refresh Database`：清除瀏覽器 IndexedDB 快照，並重新載入最新目錄資料

### 遺失掛載修復

若已設定 `mount_script`，且媒體請求命中遺失資料夾，伺服器將會：

1. 偵測父資料夾不存在
2. 呼叫一次已設定的掛載腳本
3. 重新檢查目標路徑
4. 只有在資料夾仍不可用時，才回傳 `Media folder is not mounted` 與 HTTP 404

前端會把播放 404 視為該次嘗試的終止狀態，並顯示重試訊息，而非持續反覆打向伺服器。

---

## 前端開發說明

目前 `index.html` 直接載入 `movies.js`，因此前端修改無需重新建置 `movies.min.js` 也會生效。

---

## 私密模式

- 私密資料夾在裝置未授權前會被隱藏
- 解鎖狀態綁定裝置 ID
- 已授權裝置會儲存在伺服器端
- `passcode.py` 可輪換私密模式密碼並清除授權

示例：

```bash
python3 passcode.py mynewpasscode
```

---

## 產生的檔案

以下檔案會於執行時產生，不應提交：

- `movies_config.json`
- `movies_state.json`
- `movies_auth_state.json`
- `movies_catalog_index.json`
- `cache/`

---

## 疑難排解

### 介面變更沒有出現

- 先正常重新整理頁面
- 若 JS 套件已變更，請確認 `index.html` 指向預期的套件版本

### 私密內容的直接播放失敗

- 重新解鎖私密模式，讓 `movies_device_id` Cookie 重新整理

### Plex 播放失敗但直接播放可行

- 確認 movies server 主機可連到 `plex.base_url`
- 確認設定中已啟用 Plex
- 確認設定的 Token 有效

### 直接播放失敗但 Plex 可行

- 該容器或編解碼器很可能不適合在該裝置上的瀏覽器原生播放
- 對這些檔案保持啟用 Plex，或透過本機轉碼/Plex 強制走相容路徑

### 本機轉碼無法運作

- 確認已安裝 `ffmpeg` 與 `ffprobe`
- 確認已啟用 `on_demand_transcode`
- 確認來源檔案屬於目前支援的容器：`.mkv` 或 `.ts`

---

## 授權條款

本專案以 MIT License 發佈。若你打算發布或重新散布它，請加入包含 MIT 內容的 `LICENSE` 檔案。
