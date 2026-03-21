# Cat Theatre Movies Server

> 使用 Flask、Waitress 與 `ffmpeg` 建立的自架電影瀏覽與串流伺服器，並可選擇整合 Plex 以提升相容性播放。

**語言**

[English](./README.md) | [简体中文](./README.zh-CN.md) | [繁體中文（香港）](./README.zh-HK.md) | `繁體中文（台灣）`

---

## 概覽

Cat Theatre 的設計重點是輕量：

- Python 相依少
- 不需要資料庫
- 以檔案系統為核心
- 使用輪詢掃描，不依賴平台專用檔案監看
- Plex 為可選擴充

適合：

- 分散於多個資料夾的本地媒體庫
- 縮圖與預覽圖產生
- 按裝置控制私密資料夾
- 透過 `/movie/` 等子路徑反向代理部署
- 直接播放、本地轉碼、Plex HLS 混合播放

---

## 功能

- 多媒體根目錄掃描
- 海報縮圖與預覽幀
- 私密資料夾解鎖
- 原生直接播放
- `.mkv`、`.ts` 本地轉碼
- Plex 播放與 HLS 代理
- 反向代理子路徑感知
- 瀏覽器圖片快取與 IndexedDB 快取

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

```bash
pip install -r requirements.txt
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

- 直接播放：`/video/<id>`
- 本地轉碼：`/hls/<id>/index.m3u8` 或 `/video/<id>?fmp4=1`
- Plex 播放：由 Plex 產生 HLS，本服務負責代理

### 預設播放邏輯

- 對於 `.mp4`、`.m4v`、`.webm`、`.avi`，如果直接播放 URL 是實際檔案路徑，且音訊編碼符合白名單，則優先 `Direct`
- 如果這些瀏覽器安全副檔名缺少音訊編碼中繼資料，應用仍會優先 `Direct`
- `.mkv`、`.ts`、HLS/fMP4 直接播放 URL，以及已知音訊編碼不在白名單內的檔案，優先 `Plex`
- 如果沒有 Plex 配對，則回退到 `Direct`

---

## 快取與掃描

- 圖片使用長效快取
- IndexedDB 快照預設 1 天 TTL
- 最多 8 筆快照
- 約 18 MB 上限
- 可用 `/rescan?full=1` 強制完整重新掃描

---

## 私密模式與除錯

- 私密資料夾預設隱藏
- 解鎖狀態綁定裝置
- `passcode.py` 可輪換私密密碼
- `debug_enabled` 可顯示除錯面板

---

## 疑難排解

- Plex 播放失敗時，檢查 `plex.base_url` 與 token
- 本地轉碼失敗時，檢查 `ffmpeg`、`ffprobe` 與 `on_demand_transcode`
