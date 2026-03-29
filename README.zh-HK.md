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
  <p><strong>超輕量，私隱模式 🔐，跨裝置，智能串流</strong></p>
  <p>毋須應用程式。伺服器安裝簡單，介面對手機友善，令你的 NAS 隨時隨地都可連線，並可選擇整合 Plex</p>
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



> 沒有沉重依賴，一切都很透明。以 Flask、Waitress 和 `ffmpeg` 建構的輕量級自託管電影瀏覽與串流伺服器，並可選擇整合 _`Plex`_，以提供更著重相容性的播放方案。

---

![Screenshot 2026-03-22 at 9 39 12 PM](https://github.com/user-attachments/assets/124f21b7-71b0-46fc-9d76-c73f700c25f3)

---

## ✨ 為什麼要用它

Cat Theatre 刻意保持輕量：

- 🩷 _遠端存取_ 不需要 Plex 訂閱 💰
- ✅ Python 依賴面小
- ✅ 不需要資料庫
- ✅ 以檔案系統為核心進行目錄整理
- ✅ 相容於 🖥️ 桌面、📱 手機與平板
- ✅ 使用可攜式輪詢掃描流程，而不是依賴作業系統專屬的檔案監看
- 🔶 Plex 整合屬可選加層，而非核心播放所必需

## ✴️ 功能特色

- 🎬 分散在多個資料夾中的本機 / NAS 媒體庫
- 🌄 縮圖 / 海報與預覽影格產生
- 🔐 以裝置解鎖的私人資料夾
- 🔗 支援在 `http://192.168.1.100/movie/` 這類路徑前綴下透過反向代理部署
- 📽️ 混合播放策略：直接播放、針對 `.mkv` 與 `.ts` 的內建本地轉碼，或由 Plex 支援的 HLS 代理。可按媒體輕鬆切換
- 🌐 瀏覽器圖片快取與 IndexedDB 中繼資料快取

---
→ 一行指令安裝：
```
curl -fsSL https://raw.githubusercontent.com/daocha/plex-cat-theatre/main/install.sh | bash
```
---

## 🟢 執行需求

### Python 3.9 或以上

目前 Python 套件：

- `Flask`
- `waitress`

### 用於中繼資料探測、預覽、縮圖與本地轉碼的系統二進位工具：

- `ffmpeg`
- `ffprobe`

確認它們可用：

```bash
which ffmpeg
which ffprobe
```

---

## 🚀 快速開始


### → 選項 A：一行指令安裝：
```
curl -fsSL https://raw.githubusercontent.com/daocha/plex-cat-theatre/main/install.sh | bash
```

### → 選項 B：使用 pip 從 PyPI 安裝

```bash
pip install plex-cat-theatre
plex-cat-theatre-init
plex-cat-theatre --config ~/movies_config.json
```

### → 選項 C：首選啟動方式

```bash
git clone https://github.com/daocha/plex-cat-theatre
cd plex-cat-theatre
./startup.sh
```

這個啟動腳本可以：

- 首次執行時根據範例設定建立 `movies_config.json`
- 建立本地 `.venv`
- 將 Python 依賴安裝到這個本地虛擬環境
- 在需要時按設定檔位置建立 `cache/thumbnails` 與 `logs` 目錄
- 檢查 `ffmpeg` 與 `ffprobe`
- 可選地協助你產生私人模式口令雜湊
- 使用本地設定啟動伺服器

你仍然可以使用以下手動流程：

1. 複製範例設定：

```bash
cp movies_config.sample.json movies_config.json
```

2. 按你的環境修改 `movies_config.json`。

### 🌐 啟動伺服器：

```bash
# 如果你使用選項 A 或選項 B，請執行
plex-cat-theatre --config ~/movies_config.json

# 如果你使用選項 C，請執行
python3 movies_server.py --config movies_config.json
```

開啟介面：

```text
http://localhost:9245
```
### 🔑 更改口令
```bash
# 如果你使用選項 A 或選項 B，請執行
plex-cat-theatre-passcode newpasscode

# 如果你使用選項 C，請執行
python3 passcode.py newpasscode
```
- 私人資料夾會保持隱藏，直到裝置獲授權
- 解鎖狀態會綁定到裝置 ID
- 已批准裝置會儲存在伺服器端
- 這個腳本可輪替私人模式口令並清除既有授權

---

## 🗂️ 專案結構

- `movies_server.py`：Flask 入口點與路由接線
- `movies_server_core.py`：用於驗證、設定、Cookie 與掛載路徑處理的共用伺服器輔助邏輯
- `movies_catalog.py`：目錄掃描、縮圖產生、字幕擷取與本地轉碼輔助功能
- `movies_server_plex.py`：Plex 介接器、海報 / 字幕對應與 Plex HLS 代理
- `movies.js`：前端原始碼
- `movies.min.js`：壓縮後的前端 bundle
- `movies.css`：圖庫與播放器樣式
- `passcode.py`：用於輪替私人模式口令的輔助腳本

---

## ⚙️ 設定

範例設定刻意做過去識別化，不包含：

- 真實檔案系統路徑
- 真實 Plex 權杖
- 真實口令雜湊
- 裝置相關數值

### 📍 重要欄位

<table>
  <tr>
    <td width="200"><code>root</code></td>
    <td>要掃描的媒體根目錄（支援多個資料夾）</td>
  </tr>
  <tr>
    <td><code>thumbs_dir</code></td>
    <td>縮圖與預覽影格目錄。預設值：<code>./cache/thumbnails</code></td>
  </tr>
  <tr>
    <td><code>private_folder</code></td>
    <td>視為私人的資料夾前綴。例如 <code>Personal</code>。在你從介面解鎖前，位於 <code>Personal</code> 資料夾下的內容都會被鎖住。</td>
  </tr>
  <tr>
    <td><code>private_passcode</code></td>
    <td>私人模式口令雜湊，不應直接用明文更新。若想修改，請參考 <code>更改口令</code> 章節。</td>
  </tr>
  <tr>
    <td><code>mount_script</code></td>
    <td>[可選] 當播放命中遺失的媒體資料夾，且原因是掛載意外中斷時要執行的命令。</td>
  </tr>
  <tr>
    <td><code>transcode</code></td>
    <td>啟用目錄端背景轉碼 worker，用於 `.mkv`、`.ts` 等來源容器；這可能會在來源媒體庫旁產生額外的轉碼 sidecar 檔案，因此通常建議維持為 <code>false</code>，尤其在啟用 Plex 整合時。預設值：<code>false</code></td>
  </tr>
  <tr>
    <td><code>auto_scan_on_start</code></td>
    <td>啟動時重新掃描媒體。預設值：<code>false</code></td>
  </tr>
  <tr>
    <td><code>on_demand_transcode</code></td>
    <td>為來源容器啟用播放器執行期轉碼；可優先使用硬體編碼，不可用時回退到軟體編碼。預設值：<code>true</code></td>
  </tr>
  <tr>
    <td><code>on_demand_hls</code></td>
    <td>為來源容器啟用內建 HLS 播放清單。預設值：<code>true</code></td>
  </tr>
  <tr>
  <td><code>enable_plex_server</code></td>
  <td>📍 [可選] 啟用 Plex 整合。預設值：<code>false</code>。啟用前請先確認 Plex Server 已正確安裝並設定完成。<br> 這個伺服器支援原生字幕，但如果你想自動抓取字幕，通常更建議交由 Plex 處理。
  <br> 如果你希望獲得更好的隨選轉碼體驗，強烈建議安裝 Plex server，以提供更順暢的媒體串流。<br>
  即使沒有 Plex server，這個服務仍然可以正常運作，但請留意：
  <br>→ 對於你的裝置可以直接播放的媒體，拖曳定位功能可正常運作。
  <br>→ 對於你的裝置無法直接播放的媒體，例如 <code>h.265 配 DTS 音訊</code>（h.265 配 AAC 或 MP3 不受影響）、<code>.mkv</code>、<code>.ts</code> 或 <code>.wmv</code>，這個服務仍可即時轉碼，但拖曳定位可能不可用。
  </td>
  </tr>
  <tr>
    <td><code>plex.base_url</code></td>
    <td>Plex 伺服器基礎 URL。</td>
  </tr>
  <tr>
    <td><code>plex.token</code></td>
    <td>Plex 權杖</td>
  </tr>
  <tr>
    <td><code>debug_enabled</code></td>
    <td>顯示內建除錯浮層</td>
  </tr>
  <tr>
    <td><code>direct_playback</code></td>
    <td>包含 <code>enabled</code> 與 <code>audio_whitelist</code> 的物件。當 <code>enabled=true</code> 時，可用原生播放器直接播放媒體而毋須轉碼（更快）。建議保留預設設定。</td>
  </tr>
</table>

### 最小純本地範例

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

### 啟用 Plex 整合的範例

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

### 🅿️ Plex 掃描行為

- 當 Plex 海報可用時，會跳過本地海報縮圖產生
- 既有的本地快取縮圖仍可重用
- 預覽影格產生仍會維持啟用
- Plex 整合仍然是可選的，純本地模式依然可用

### → 如何取得 Plex 權杖

#### 方法 1：現有 Plex Web 工作階段

1. 開啟 Plex Web 並登入。
2. 開啟瀏覽器開發者工具。
3. 進入網絡分頁。
4. 重新整理頁面。
5. 檢查一個送往 Plex 伺服器的請求。
6. 在 URL 或標頭中找出 `X-Plex-Token`。

#### 方法 2：瀏覽器儲存空間

檢查：

- 本機儲存（`Local Storage`）
- 工作階段儲存（`Session Storage`）
- DevTools 內的請求 URL 與標頭

#### 方法 3：本機直接請求

如果你已在同一部機器上登入 Plex Web 且工作階段仍有效，可在 DevTools 中檢查 Plex 請求並尋找：

```text
X-Plex-Token=...
```

‼️ 安全提醒：

- 請把 Plex 權杖當作密碼看待
- 不要把它提交到 git
- 只把它存放在 `movies_config.json`

---

## 🎥 播放模式

### 1. 原生直接播放

用於 `.mp4`、`.m4v`、`.webm` 等瀏覽器安全檔案。

行為：

- 透過 `/video/<id>` 直接提供本地檔案
- 支援 HTTP range request
- 當瀏覽器可原生播放檔案時，可避免轉碼額外負擔

最適合：

- MP4 / H.264 類型檔案
- 瀏覽器本身已支援直接播放的檔案
- 音訊編碼符合 direct-play 白名單的檔案

### 2. 不依賴 Plex 的內建本地轉碼

當 Plex 未啟用，或你刻意想維持完全本地時，就會走這個回退路徑。

目前實作：

- `.mkv` 與 `.ts` 可透過 `/hls/<id>/index.m3u8` 以本地 HLS 形式提供
- 同一批檔案也可透過 `/video/<id>?fmp4=1` 以 fragmented MP4 形式串流
- HLS 分段會以 `ffmpeg` 按需產生
- 會優先嘗試硬體編碼，必要時回退到 `libx264`
- fMP4 輸出使用 `libx264` 加 AAC 產生

### 3. Plex 支援播放

啟用 Plex 整合後：

- 前端可使用 `plex_stream_url` 處理更重視相容性的播放
- Plex 會產生上游 HLS 播放清單
- 本服務會改寫播放清單，並代理巢狀播放清單與分段請求
- 瀏覽器仍然是連到這個應用，而不是直接連 Plex

最適合：

- 在編碼器或容器支援較弱的裝置上播放 MKV 或 TS 內容
- 較適合使用 Plex 做字幕選擇或串流正規化的情境

### 播放選擇策略

- 對於瀏覽器安全且音訊編碼符合 `direct_playback.audio_whitelist` 的檔案，優先使用直接播放
- 對於 `.mkv`、`.ts`、HLS、fMP4 或不受支援的音訊編碼，仍優先選擇 Plex
- iOS 原生 HLS 的回退等待時間會更長，以便讓 Plex 串流有時間暖機

### 預設播放邏輯

- 當直接 URL 是真實檔案路徑且音訊編碼在白名單內時，`.mp4`、`.m4v`、`.webm` 與 `.avi` 會優先使用 `Direct`
- 若這些瀏覽器安全副檔名缺少音訊編碼中繼資料，應用仍會偏好 `Direct`
- 對於 `.mkv`、`.ts`、HLS / fMP4 直接 URL，以及已知音訊編碼不在白名單內的檔案，則優先使用 `Plex`
- 如果找不到 Plex 對應項，應用會回退到 `Direct`

---

## 驗證模型

應用會依請求類型使用不同的傳輸方式：

- API 請求使用 `X-Device-Id` 標頭
- HLS 與 Plex 代理請求使用 `X-Device-Id` 標頭
- 原生直接媒體請求使用 `movies_device_id` Cookie 回退

這種拆分是因為原生 `<video src="...">` 請求無法附加任意自訂標頭。

---

## 反向代理與內容路徑支援

應用支援部署在如下子路徑：

- `https://example.com/movie/`
- `https://example.com/cinema/`

路由會為以下項目保留目前掛載前綴：

- 直接媒體
- 本地 HLS
- Plex HLS 代理請求
- 海報與字幕資產

---

## 透過 Tailscale 進行遠端 Plex 存取

如果自訂介面可從遠端連線，但 Plex 只能在私人 LAN 中存取，那麼 movies server 所在主機仍必須能直接連到 Plex 後端。

### 同一部主機

```json
"plex": {
  "base_url": "http://127.0.0.1:32400"
}
```

### Plex 位於另一部 LAN 機器

由可連到 Plex 的 Tailscale 節點宣告路由：

```bash
sudo tailscale up --advertise-routes=192.168.50.0/24
```

然後在 movies server 主機上確認可達性：

```bash
curl http://192.168.50.10:32400/identity
```

📌 注意：

- 瀏覽器不需要直接存取 Plex
- movies server 程序必須能連到 `plex.base_url`
- 介面的反向代理或 MagicDNS 名稱本身不會令 Plex 自動變得可達

---

## 💾 快取策略

### 圖片快取

縮圖、預覽影格與 Plex 海報圖片都會以長效 immutable cache header 提供。

### 中繼資料快取

圖庫中繼資料快照會儲存在 IndexedDB 中，並設有儲存上限：

- 1 日 TTL
- 最多 8 筆快照記錄
- 總估計大小最多約 18 MB
- 超出限制時會淘汰較舊資料

每筆快取快照會儲存：

- 伺服器 `catalogStatus`
- 資料夾列表快取
- 已載入的 `videos`
- 如 `serverTotal`、`serverOffset` 與 `serverExhausted` 等分頁計數器

淘汰策略是機會式，而非排程式：

- 過期項目會在讀取時或後續清理時移除
- 儲存新快照後會執行清理
- 瀏覽器儲存空間壓力或手動清除網站資料，也可能刪除 IndexedDB 資料

---

## 🔍 掃描行為

目錄掃描的設計目標，是即使仍要走訪每個已設定根目錄，也能讓成本保持增量化。

目前行為：

- 未變動檔案會重用快取的 `mtime + size` 簽章
- 週期性掃描不再於處理前排序完整路徑清單
- 已刪除檔案會從記憶體目錄與持久化索引中移除
- 已刪除檔案亦會觸發已生成縮圖與預覽產物的清理
- 儲存索引時會重用快取的檔案簽章資料，而不是重新對每個檔案執行 `stat`

掃描仍會做的事：

- 走訪已設定的媒體根目錄，以偵測新增、變更與刪除檔案
- 當缺少預覽圖時，將預覽產生加入佇列

掃描不會做的事：

- 週期性掃描時不會對大型媒體檔案做 checksum
- 只要快取產物仍存在，就不會為未變動檔案重新產生縮圖或中繼資料

### → 觸發重新掃描

一般增量重掃：

```bash
curl -s http://localhost:9245/rescan | python3 -m json.tool
```

強制完整重掃：

```bash
curl -s "http://localhost:9245/rescan?full=1" | python3 -m json.tool
```

### → 重掃介面

`Rescan` 按鈕不會即時啟動增量掃描，而是先開啟操作對話框。

可用操作：

- `Rescan`：針對新增或變更檔案進行增量掃描
- `Full Scan`：清除已儲存的掃描狀態並強制完整中繼資料重新驗證
- `Refresh Database`：清除瀏覽器 IndexedDB 快照並重新載入最新目錄資料

### ⛓️‍💥 遺失掛載恢復

這項功能主要是因應某些 NAS 可能啟用自動休眠，導致 SMB 掛載被某些作業系統自動卸除的情況。

若已設定 `mount_script`，而某個媒體請求命中遺失的資料夾，伺服器會：

1. 偵測父層資料夾不存在
2. 呼叫一次已設定的掛載腳本
3. 再次檢查目標路徑
4. 只有在資料夾仍不可用時，才回傳 `Media folder is not mounted` 與 HTTP 404

前端會將播放過程中的 404 視為本次嘗試的終止條件，並顯示重試訊息，而不是持續重覆請求伺服器。

---

## 📄 產生的檔案

以下檔案會在執行時產生，不應提交至版本庫：

- `movies_config.json`
- `movies_state.json`
- `movies_auth_state.json`
- `movies_catalog_index.json`
- `cache/`

---

## 🛠️ 疑難排解


### → 除錯浮層

在 `movies_config.json` 中啟用 `debug_enabled`，即可讓右下角持續顯示除錯浮層。

該面板會顯示：

- 伺服器目前偏好直接播放還是 Plex
- 已設定的 direct-play 音訊白名單
- 目前播放候選項與影片 ID
- 最近的掃描進度指標

使用以下指令檢查目前生效的設定值：

```bash
curl -s http://localhost:9245/api/config | python3 -m json.tool
```

### → 介面變更未有顯示

- 目前應用會直接從 `index.html` 載入 `movies.js`，所以前端變更不需要重新建置 `movies.min.js` 就會生效。
- 先正常重新整理頁面
- 若 JS bundle 已變更，請確認 `index.html` 引用的是預期版本的 bundle

### → 私人內容的直接播放失敗

- 請重新解鎖私人模式，以刷新 `movies_device_id` Cookie

### → Plex 播放失敗但直接播放正常

- 確認 movies server 主機可連到 `plex.base_url`
- 確認設定中已啟用 Plex
- 確認設定的 token 有效

### → 直接播放失敗但 Plex 正常

- 該裝置上的瀏覽器原生播放很可能無法安全支援該容器或編碼
- 可繼續為這些檔案啟用 Plex，或透過本地轉碼 / Plex 強制走相容路徑

### → 本地轉碼無法運作

- 確認已安裝 `ffmpeg` 與 `ffprobe`
- 確認已啟用 `on_demand_transcode`
- 確認來源檔案屬於目前支援的容器：`.mkv` 或 `.ts`

---

## 📦 發布版本規則

套件版本號來自 Git tag。

- TestPyPI / testing：使用開發版本，例如 `2026.3.26.dev1`
- PyPI 預發布：使用候選版本，例如 `2026.3.26rc1`
- PyPI 正式版：使用穩定版本，例如 `2026.3.26`
- Git tag 應為 `v2026.3.26.dev1`、`v2026.3.26rc1` 與 `v2026.3.26`
  
---

## ©️ 授權

本專案以 MIT License 發布。發布或重新分發時，請附上包含 MIT 文字的 `LICENSE` 檔案。
