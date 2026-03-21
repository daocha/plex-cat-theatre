# Cat Theatre 電影伺服器

> 輕量級自架電影瀏覽與串流伺服器，基於 Flask、Waitress 與 `ffmpeg`。

[English](./README.md)

---

## 主要功能

- 多媒體資料夾掃描
- 縮圖與預覽畫面生成
- 私密資料夾按裝置解鎖
- 直接播放、本地轉碼、Plex 播放三條路徑
- 支援 `/movie/` 形式的反向代理前綴

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

## 重要設定

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

## 播放模式

### 直接播放

- 適合 `.mp4`、`.m4v`、`.webm`
- 路徑：`/video/<id>`

### 本地轉碼

- HLS：`/hls/<id>/index.m3u8`
- fMP4：`/video/<id>?fmp4=1`

### Plex

- Plex HLS
- Plex 海報
- Plex 字幕

---

## 驗證指令

```bash
python3 -m py_compile movies_server.py movies_server_core.py movies_server_plex.py movies_catalog.py
node --check movies.js
```
