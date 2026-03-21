# Cat Theatre Movies Server

> 使用 Flask、Waitress 與 `ffmpeg` 建立的自架電影瀏覽與串流伺服器，並可選擇整合 Plex 以提升相容性播放。

**語言**

[English](./README.md) | [简体中文](./README.zh-CN.md) | `繁體中文（香港）` | [繁體中文（台灣）](./README.zh-TW.md)

---

## 概覽

Cat Theatre 的定位是輕量：

- Python 依賴少
- 不需要資料庫
- 以檔案系統為核心
- 使用輪詢掃描，不依賴平台專用檔案監看
- Plex 是可選擴充，而不是核心前提

適合：

- 分散於多個資料夾的本地媒體庫
- 縮圖與預覽圖產生
- 按裝置控制私密資料夾
- 透過 `/movie/` 之類子路徑反向代理部署
- 直接播放、本地轉碼、Plex HLS 混合播放

---

## 功能

- 多媒體根目錄掃描
- 海報縮圖與預覽幀
- 私密資料夾解鎖
- 瀏覽器安全格式的原生直接播放
- 啟用時可對 `.mkv`、`.ts` 進行本地轉碼
- Plex 播放、海報、字幕與 HLS 代理整合
- 反向代理子路徑感知
- 瀏覽器圖片快取與 IndexedDB 中繼資料快取

---

## 專案結構

- `movies_server.py`
- `movies_server_core.py`
- `movies_catalog.py`
- `movies_server_plex.py`
- `movies.js`
- `movies.min.js`
- `movies.css`
- `passcode.py`

---

## 相依需求

### Python

```bash
pip install -r requirements.txt
```

### 系統工具

```bash
which ffmpeg
which ffprobe
```

---

## 快速開始

```bash
cp movies_config.sample.json movies_config.json
python3 movies_server.py --config movies_config.json
```

開啟：

```text
http://localhost:9245
```

---

## 設定

重要欄位：

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

## 播放模式

### 直接播放

- 從 `/video/<id>` 直接輸出
- 支援 Range
- 適合瀏覽器本身可播放的檔案

### 本地轉碼

- `/hls/<id>/index.m3u8`
- `/video/<id>?fmp4=1`
- 目前重點支援 `.mkv`、`.ts`

### Plex 播放

- Plex 產生上游 HLS
- 本服務代理播放清單與分段
- 瀏覽器仍只連線本服務

### 預設播放邏輯

- 對於 `.mp4`、`.m4v`、`.webm`、`.avi`，如果直接播放 URL 是真實檔案路徑，而且音訊編碼符合白名單，則優先 `Direct`
- 如果這些瀏覽器安全副檔名缺少音訊編碼中繼資料，應用仍會優先 `Direct`
- `.mkv`、`.ts`、HLS/fMP4 直接播放 URL，以及已知音訊編碼不在白名單內的檔案，優先 `Plex`
- 如果沒有 Plex 配對，則回退到 `Direct`

---

## 快取與掃描

- 圖片使用長效快取
- IndexedDB 快照預設 1 日 TTL
- 最多 8 筆快照
- 約 18 MB 總量上限
- `/rescan?full=1` 可強制完整重新掃描

---

## 私密模式與除錯

- 私密資料夾預設隱藏
- 解鎖狀態按裝置保存
- `passcode.py` 可輪換密碼
- `debug_enabled` 可顯示右下角除錯面板

---

## 疑難排解

- Plex 播放失敗時，先檢查 `plex.base_url` 與 token
- 本地轉碼失敗時，先檢查 `ffmpeg`、`ffprobe` 與 `on_demand_transcode`
