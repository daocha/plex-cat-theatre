# Cat Theatre Movies Server

> 使用 Flask、Waitress 与 `ffmpeg` 构建的自托管电影浏览与流媒体服务器，并可选接入 Plex 以获得更好的兼容性播放。

**语言**

[English](./README.md) | `简体中文` | [繁體中文（香港）](./README.zh-HK.md) | [繁體中文（台灣）](./README.zh-TW.md)

---

## 概览

Cat Theatre 的设计目标是轻量：

- Python 依赖少
- 不需要数据库
- 以文件系统为核心
- 使用轮询扫描，不依赖特定平台的文件监听
- Plex 是可选增强，而不是核心前提

适合：

- 分布在多个目录中的本地媒体库
- 缩略图与预览图生成
- 按设备控制私密目录
- 通过 `/movie/` 这类子路径反向代理部署
- 直放、本地转码、Plex HLS 混合播放

---

## 功能

- 多媒体根目录扫描
- 海报缩略图与预览帧生成
- 私密目录解锁
- 浏览器安全格式的原生直放
- 启用时可对 `.mkv` 与 `.ts` 做本地转码
- Plex 播放、海报、字幕与 HLS 代理集成
- 反向代理子路径感知
- 浏览器图片缓存与 IndexedDB 元数据缓存

---

## 项目结构

- `movies_server.py`：Flask 入口与路由
- `movies_server_core.py`：配置、认证、Cookie、挂载路径辅助逻辑
- `movies_catalog.py`：扫描、缩略图、字幕、元数据与本地转码
- `movies_server_plex.py`：Plex 适配层
- `movies.js`：前端源码
- `movies.min.js`：压缩后的前端包
- `movies.css`：界面样式
- `passcode.py`：私密模式密码辅助脚本

---

## 依赖

### Python

```bash
pip install -r requirements.txt
```

### 系统工具

```bash
which ffmpeg
which ffprobe
```

`ffmpeg` 与 `ffprobe` 用于预览、缩略图、探测与本地转码。

---

## 快速开始

1. 复制配置模板：

```bash
cp movies_config.sample.json movies_config.json
```

2. 修改 `movies_config.json`

3. 启动：

```bash
python3 movies_server.py --config movies_config.json
```

4. 打开：

```text
http://localhost:9245
```

若部署在 `/movie/` 这类前缀下，请访问带前缀的地址。

---

## 配置

重要字段：

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

### 本地模式示例

```json
{
  "root": ["~/Movies"],
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

### Plex 模式示例

```json
{
  "root": ["~/Movies"],
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

---

## 播放模式

### 原生直放

- 从 `/video/<id>` 直接输出
- 支持 Range 请求
- 适合浏览器原生支持的文件

### 无 Plex 的本地转码

- 可通过 `/hls/<id>/index.m3u8` 提供本地 HLS
- 也可通过 `/video/<id>?fmp4=1` 提供 fMP4
- 当前重点支持 `.mkv` 与 `.ts`

### Plex 播放

- Plex 生成上游 HLS
- 本服务重写并代理播放列表与分片
- 浏览器仍只连接本服务

### 默认播放逻辑

- 对于 `.mp4`、`.m4v`、`.webm`、`.avi`，如果直连 URL 是真实文件地址，且音频编码满足白名单，则优先 `Direct`
- 如果这些浏览器安全扩展名缺少音频编码元数据，应用仍会优先 `Direct`
- `.mkv`、`.ts`、HLS/fMP4 直连 URL，以及已知音频编码不在白名单内的文件，优先 `Plex`
- 如果没有 Plex 匹配，则回退到 `Direct`

---

## 缓存与扫描

### 缓存

- 图片使用长缓存头
- IndexedDB 元数据快照默认 1 天 TTL
- 最多 8 条快照
- 总大小大约 18 MB 上限

### 扫描

- 未变化文件复用缓存签名
- 会检测新增、删除、修改
- 缺失预览图时会补生成

强制全量扫描：

```text
/rescan?full=1
```

---

## 私密模式与调试

- 私密目录默认隐藏
- 解锁按设备保存
- `passcode.py` 可轮换密码并清除授权
- `debug_enabled` 可显示右下角调试面板

---

## 故障排除

### 页面改动未生效

- 先普通刷新
- 确认 `index.html` 引用了正确的前端文件版本

### Plex 播放失败

- 检查服务器是否能访问 `plex.base_url`
- 检查 Plex 是否启用
- 检查 token 是否有效

### 本地转码失败

- 检查 `ffmpeg` 与 `ffprobe`
- 检查 `on_demand_transcode`
- 检查文件是否属于当前支持的容器
