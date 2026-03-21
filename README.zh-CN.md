# Cat Theatre 电影服务器

> 轻量级自托管电影浏览与播放服务器，基于 Flask、Waitress 与 `ffmpeg`。

[English](./README.md)

---

## 核心能力

- 多媒体目录扫描
- 缩略图与预览帧生成
- 私密目录按设备解锁
- 直接播放、本地转码、Plex 播放三种路径
- 支持 `/movie/` 这类反向代理前缀部署

---

## 快速开始

### 1. 复制配置

```bash
cp movies_config.sample.json movies_config.json
```

### 2. 编辑配置

重点字段：

- `root`
- `thumbs_dir`
- `private_folder`
- `private_passcode`
- `mount_script`
- `enable_plex_server`
- `direct_playback`

### 3. 启动服务

```bash
python3 movies_server.py --config movies_config.json
```

### 4. 打开页面

```text
http://localhost:9245
```

---

## 重要配置

- `root`: 要扫描的媒体根目录
- `thumbs_dir`: 缩略图与预览帧缓存目录
- `private_folder`: 视为私密的目录前缀
- `private_passcode`: 私密模式密码哈希
- `mount_script`: 媒体目录未挂载时的自动挂载脚本
- `on_demand_transcode`: 启用本地转码
- `on_demand_hls`: 启用本地 HLS
- `enable_plex_server`: 启用 Plex 集成
- `plex.base_url`: Plex 地址
- `plex.token`: Plex Token

---

## 播放模式

### 直接播放

- 适合 `.mp4`、`.m4v`、`.webm`
- 路径为 `/video/<id>`

### 本地转码

- 本地 HLS：`/hls/<id>/index.m3u8`
- fMP4 回退：`/video/<id>?fmp4=1`

### Plex 播放

- Plex HLS
- Plex 海报
- Plex 字幕

---

## 开发检查

```bash
python3 -m py_compile movies_server.py movies_server_core.py movies_server_plex.py movies_catalog.py
node --check movies.js
```
