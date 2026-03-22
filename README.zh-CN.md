# Cat Theatre Movies Server

> 基于 Flask、Waitress 和 `ffmpeg` 构建的轻量级自托管电影浏览与流媒体服务器，并可选集成 _`Plex`_ 以提供更注重兼容性的播放方案。

---

![Screenshot 2026-03-22 at 9 39 12 PM](https://github.com/user-attachments/assets/124f21b7-71b0-46fc-9d76-c73f700c25f3)

---

**语言**

[English](./README.md) | `简体中文` | [繁體中文（香港）](./README.zh-HK.md) | [繁體中文（台灣）](./README.zh-TW.md) | [Français](./README.fr.md) | [한국어](./README.ko.md) | [日本語](./README.ja.md) | [Deutsch](./README.de.md) | [ไทย](./README.th.md) | [Tiếng Việt](./README.vi.md) | [Nederlands](./README.nl.md)

---

## 概览

Cat Theatre 的设计目标是保持轻量：

- Python 依赖面小
- 不需要数据库
- 以文件系统为核心进行目录编制
- 使用可移植的轮询扫描流程，而不是依赖操作系统专属的文件监控
- Plex 集成为可选附加层，而不是核心播放所必需

它适用于：

- 分布在一个或多个文件夹中的本地媒体库
- 缩略图和预览帧生成
- 基于设备的私密文件夹访问控制
- 在如 `/movie/` 这样的路径前缀下通过反向代理部署
- 混合播放策略：直接文件播放、内置本地转码，或基于 Plex 的 HLS

---

## 功能

- 多根目录媒体扫描
- 海报缩略图和预览帧生成
- 带设备解锁的私密文件夹
- 浏览器安全格式的原生直接播放
- 启用时为 `.mkv` 和 `.ts` 提供内置本地转码
- Plex 集成，支持播放、海报、字幕和 HLS 代理
- 面向反向代理的上下文路径路由支持
- 浏览器图片缓存与 IndexedDB 元数据缓存

### 界面与播放说明

- 内置调试面板位于右下角，并可滑动到最近的边缘
- 播放会自动为当前文件和设备优先选择更稳妥的路径
- 手动 Direct/Plex 覆盖会按视频存储在 IndexedDB 中
- 缓存的缩略图和元数据会保持在浏览器存储限制内

---

## 依赖要求

### Python

```bash
pip install -r requirements.txt
```

当前 Python 包：

- `Flask`
- `waitress`

### 系统二进制工具

元数据探测、预览、缩略图和本地转码需要：

- `ffmpeg`
- `ffprobe`

确认它们可用：

```bash
which ffmpeg
which ffprobe
```

---

## 快速开始

首选启动方式：

```bash
./startup.sh
```

这个引导脚本可以：

- 首次运行时根据示例配置创建 `movies_config.json`
- 创建本地 `.venv`
- 将 Python 依赖安装到这个本地虚拟环境中
- 检查 `ffmpeg` 和 `ffprobe`
- 可选地帮助你生成私密模式口令哈希
- 使用本地配置启动服务器

你仍然可以使用下面的手动流程：

1. 复制示例配置：

```bash
cp movies_config.sample.json movies_config.json
```

2. 按你的环境编辑 `movies_config.json`。

3. 启动服务器：

```bash
python3 movies_server.py --config movies_config.json
```

4. 打开界面：

```text
http://localhost:9245
```

如果你通过反向代理把应用部署在如 `/movie/` 这样的前缀下，请改为打开带前缀的 URL。

---

## 项目结构

- `movies_server.py`：Flask 入口与路由绑定
- `movies_server_core.py`：认证、配置、Cookie 与挂载路径处理等共享服务端辅助逻辑
- `movies_catalog.py`：目录扫描、缩略图生成、字幕提取和本地转码辅助逻辑
- `movies_server_plex.py`：Plex 适配器、海报/字幕映射与 Plex HLS 代理
- `movies.js`：前端源码
- `movies.min.js`：前端压缩包
- `movies.css`：图库与播放器样式
- `passcode.py`：用于轮换私密模式口令的辅助脚本

---

## 配置

示例配置经过刻意清理，不包含：

- 真实文件系统路径
- 真实 Plex Token
- 真实口令
- 设备专属值

### 重要字段

- `root`：要扫描的媒体根目录
- `thumbs_dir`：缩略图和预览帧目录
- `private_folder`：视为私密的文件夹前缀
- `private_passcode`：私密模式口令哈希
- `mount_script`：当播放遇到缺失媒体目录时可调用的挂载脚本
- `transcode`：为 `.mkv`、`.ts` 等源容器启用目录扫描侧的后台转码工作线程；这可能会在媒体库旁边生成额外的转码旁路文件，因此通常建议保持为 `false`，尤其是在启用 Plex 集成时
- `auto_scan_on_start`：启动时重新扫描媒体
- `on_demand_transcode`：为播放器运行时启用源容器转码，可优先使用硬件编码，不可用时再回退到软件编码
- `on_demand_hls`：为源容器启用内置 HLS 播放列表
- `enable_plex_server`：启用 Plex 集成
- `plex.base_url`：Plex 服务器基础 URL
- `plex.token`：Plex Token
- `debug_enabled`：显示内置调试浮层
- `direct_playback`：包含 `enabled` 和 `audio_whitelist` 的对象

### 最小本地示例

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

### 启用 Plex 的示例

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

### Plex 扫描行为

- 当 Plex 海报可用时，会跳过本地海报缩略图生成
- 已缓存的本地缩略图仍然可以复用
- 预览帧生成仍保持启用
- Plex 集成依然是可选的，仅本地模式仍可正常工作

### 如何获取 Plex Token

#### 方法 1：使用现有 Plex Web 会话

1. 打开 Plex Web 并登录。
2. 打开浏览器开发者工具。
3. 进入 Network 标签页。
4. 刷新页面。
5. 查看发往 Plex 服务器的请求。
6. 在 URL 或请求头中找到 `X-Plex-Token`。

#### 方法 2：从浏览器存储中查看

检查：

- Local Storage
- Session Storage
- DevTools 中的请求 URL 和请求头

#### 方法 3：直接查看本机请求

如果你在同一台机器上已有 Plex Web 活跃会话，可在 DevTools 中检查 Plex 请求并寻找：

```text
X-Plex-Token=...
```

安全说明：

- 把 Plex Token 当作密码处理
- 不要提交到 git
- 仅保存在 `movies_config.json` 中

---

## 播放模式

### 1. 原生直接播放

用于 `.mp4`、`.m4v`、`.webm` 等浏览器安全文件。

行为：

- 直接从 `/video/<id>` 提供本地文件
- 支持 HTTP Range 请求
- 当浏览器可原生播放文件时，避免转码开销

最适合：

- MP4/H.264 风格文件
- 浏览器已可直接支持的文件
- 音频编码与 direct-play 白名单匹配的文件

### 2. 无 Plex 的内置本地转码

这是未启用 Plex 时的回退路径，或你希望完全保持本地方案时的路径。

当前实现：

- `.mkv` 和 `.ts` 可通过 `/hls/<id>/index.m3u8` 暴露为本地 HLS
- 同类文件也可以通过 `/video/<id>?fmp4=1` 以 fragmented MP4 方式流式传输
- HLS 分片按需使用 `ffmpeg` 生成
- 可先尝试硬件编码，再回退到 `libx264`
- fMP4 输出使用 `libx264` 加 AAC 生成

### 3. 基于 Plex 的播放

启用 Plex 集成后：

- 前端可使用 `plex_stream_url` 进行兼容性优先的播放
- Plex 生成上游 HLS 播放列表
- 本服务器会重写播放列表并代理嵌套播放列表与分片请求
- 浏览器仍然只与本应用通信，而不是直接访问 Plex

最适合：

- 在编解码器或容器支持较弱的设备上播放 MKV 或 TS 内容
- 更希望依赖 Plex 字幕选择或流规范化的情况

### 播放选择策略

- 对于音频编码匹配 `direct_playback.audio_whitelist` 的浏览器安全文件，优先直接播放
- 对于 `.mkv`、`.ts`、HLS、fMP4 或不受支持的音频编码，仍优先使用 Plex
- iOS 原生 HLS 回退的等待时间更长，以给 Plex 流预热留出时间

### 默认播放逻辑

- 当直链 URL 是真实文件路径且音频编码在白名单内时，`.mp4`、`.m4v`、`.webm` 和 `.avi` 优先使用 `Direct`
- 若上述浏览器安全扩展名缺少音频编码元数据，应用仍然优先使用 `Direct`
- 对于 `.mkv`、`.ts`、HLS/fMP4 直链，以及已知音频编码超出白名单的文件，优先使用 `Plex`
- 如果没有 Plex 匹配，应用会回退到 `Direct`

---

## 调试浮层

在 `movies_config.json` 中启用 `debug_enabled`，即可在右下角保留一个常驻调试浮层。

该面板会显示：

- 服务器当前是偏向直接播放还是 Plex
- 配置的 direct-play 音频白名单
- 当前播放候选项和视频 ID
- 最近的扫描进度指标

可使用以下命令查看当前配置值：

```bash
curl -s http://localhost:9245/api/config | python3 -m json.tool
```

如果你通过 `/movie/` 等前缀提供服务，请使用带前缀的路径。

---

## 认证模型

应用会根据请求类型使用不同的传输方式：

- API 请求使用 `X-Device-Id` 请求头
- HLS 和 Plex 代理请求使用 `X-Device-Id` 请求头
- 原生直链媒体请求使用 `movies_device_id` Cookie 作为回退

之所以这样拆分，是因为原生 `<video src="...">` 请求无法附带任意自定义请求头。

---

## 反向代理与上下文路径支持

应用支持部署在如下子路径下：

- `https://example.com/movie/`
- `https://example.com/cinema/`

路由会保留当前挂载前缀，用于：

- 直链媒体
- 本地 HLS
- Plex HLS 代理请求
- 海报和字幕资源

---

## 通过 Tailscale 远程访问 Plex

如果自定义 UI 可远程访问，但 Plex 仅能在私有局域网中访问，那么 movies server 所在主机仍必须能直接访问 Plex 后端。

### 同一台主机

```json
"plex": {
  "base_url": "http://127.0.0.1:32400"
}
```

### Plex 位于另一台局域网机器

在能够访问 Plex 的 Tailscale 节点上广播路由：

```bash
sudo tailscale up --advertise-routes=192.168.50.0/24
```

然后在 movies server 主机上验证可达性：

```bash
curl http://192.168.50.10:32400/identity
```

说明：

- 浏览器不需要能直接访问 Plex
- movies server 进程必须能够访问 `plex.base_url`
- UI 的反向代理地址或 MagicDNS 名称本身不会让 Plex 自动可达

---

## 缓存策略

### 图片缓存

缩略图、预览帧和 Plex 海报图片都以长期 immutable 缓存头提供。

### 元数据缓存

图库元数据快照会缓存在 IndexedDB 中，并受存储上限约束：

- 1 天 TTL
- 最多 8 条快照记录
- 估算总大小约 18 MB 上限
- 超限时淘汰较旧条目

每个缓存快照会存储：

- 服务端 `catalogStatus`
- 文件夹列表缓存
- 已加载的 `videos`
- `serverTotal`、`serverOffset`、`serverExhausted` 等分页计数器

淘汰是机会式进行的，而非定时任务：

- 过期条目会在读取时或后续清理时删除
- 新快照保存后会运行清理
- 浏览器存储压力或手动清除站点数据也可能移除 IndexedDB 数据

---

## 扫描行为

目录扫描被设计为即使仍会遍历每个配置根目录，也能保持增量成本。

当前行为：

- 未变化文件会复用缓存的 `mtime + size` 签名
- 周期性扫描不再在处理前对完整路径列表排序
- 已删除文件会从内存目录和持久化索引中移除
- 已删除文件也会触发已生成缩略图和预览资源的清理
- 索引保存会复用缓存的文件签名数据，而不是再次对每个文件做 stat

扫描仍会执行的内容：

- 遍历配置的媒体根目录，以检测新增、变更和删除的文件
- 当预览图缺失时，排队生成预览图

不会执行的内容：

- 周期性扫描不会对大型媒体文件做校验和
- 对于未变化文件，除非缓存资源缺失，否则不会重新生成缩略图或元数据

### 强制完整重扫

使用：

```text
/rescan?full=1
```

适用场景：

- 有人手动删除了缩略图或预览缓存目录
- 你怀疑保存的扫描清单已经过期
- 你想强制完整重新验证所有扫描派生状态

### 查看扫描状态

```bash
curl -s http://localhost:9245/api/status | python3 -m json.tool
```

如果你通过 `/movie/` 提供服务，请使用带前缀的路径。

### 触发重扫

普通增量重扫：

```bash
curl -s http://localhost:9245/rescan | python3 -m json.tool
```

强制完整重扫：

```bash
curl -s "http://localhost:9245/rescan?full=1" | python3 -m json.tool
```

### 重扫界面

`Rescan` 按钮会打开一个操作对话框，而不是立刻启动增量扫描。

可用操作：

- `Rescan`：对新增或变更文件执行增量扫描
- `Full Scan`：清除已保存扫描状态并强制完整重新验证元数据
- `Refresh Database`：清除浏览器 IndexedDB 快照并重新加载最新目录数据

### 缺失挂载恢复

若已配置 `mount_script` 且某个媒体请求命中缺失目录，服务器会：

1. 检测父目录不存在
2. 调用一次已配置的挂载脚本
3. 重新检查目标路径
4. 只有在目录仍不可用时，才返回 `Media folder is not mounted` 和 HTTP 404

前端会把播放 404 视为本次尝试的终止状态，并显示重试提示，而不是反复持续请求服务器。

---

## 前端开发说明

当前 `index.html` 直接加载 `movies.js`，因此前端改动无需重建 `movies.min.js` 也会生效。

---

## 私密模式

- 私密文件夹在设备未授权前会被隐藏
- 解锁状态绑定到设备 ID
- 已授权设备保存在服务端
- `passcode.py` 可轮换私密模式口令并清空授权

示例：

```bash
python3 passcode.py mynewpasscode
```

---

## 生成文件

以下文件由运行时生成，不应提交：

- `movies_config.json`
- `movies_state.json`
- `movies_auth_state.json`
- `movies_catalog_index.json`
- `cache/`

---

## 故障排查

### 界面改动没有出现

- 先正常刷新页面
- 若 JS 包已变更，请确认 `index.html` 引用了期望的包版本

### 私密内容的直接播放失败

- 再次解锁私密模式，以刷新 `movies_device_id` Cookie

### Plex 播放失败但直接播放可用

- 确认 movies server 主机可访问 `plex.base_url`
- 确认配置中已启用 Plex
- 确认配置的 Token 有效

### 直接播放失败但 Plex 可用

- 该容器或编解码器很可能不适合该设备上的浏览器原生播放
- 对这些文件保持启用 Plex，或通过本地转码/Plex 强制走兼容路径

### 本地转码不工作

- 确认已安装 `ffmpeg` 和 `ffprobe`
- 确认已启用 `on_demand_transcode`
- 确认源文件属于当前支持的容器：`.mkv` 或 `.ts`

---

## 许可证

本项目基于 MIT License 发布。若你要发布或重新分发它，请添加包含 MIT 文本的 `LICENSE` 文件。
