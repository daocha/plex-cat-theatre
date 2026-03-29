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
  <p><strong>超轻量，隐私模式 🔐，跨设备，智能流式播放</strong></p>
  <p>无需安装应用。服务端安装简单，界面对移动设备友好，可让你的 NAS 随处可连，并支持可选的 Plex 集成</p>
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



> 没有沉重依赖，一切都很透明。基于 Flask、Waitress 和 `ffmpeg` 构建的轻量级自托管电影浏览与流媒体服务器，并可选集成 _`Plex`_ 以提供更注重兼容性的播放方案。

---

![Screenshot 2026-03-22 at 9 39 12 PM](https://github.com/user-attachments/assets/124f21b7-71b0-46fc-9d76-c73f700c25f3)

---

## ✨ 为什么使用它

Cat Theatre 的设计目标就是保持轻量：

- 🩷 _远程访问_ 不需要 Plex 订阅 💰
- ✅ Python 依赖面小
- ✅ 不需要数据库
- ✅ 以文件系统为核心进行目录编制
- ✅ 兼容 🖥️ 桌面端、📱 手机与平板
- ✅ 使用可移植的轮询扫描流程，而不是依赖操作系统专属的文件监控
- 🔶 Plex 集成为可选附加层，而不是核心播放所必需

## ✴️ 功能特性

- 🎬 分布在多个文件夹中的本地 / NAS 媒体库
- 🌄 缩略图 / 海报与预览帧生成
- 🔐 基于设备解锁的私密文件夹
- 🔗 支持在 `http://192.168.1.100/movie/` 这类路径前缀下通过反向代理部署
- 📽️ 混合播放策略：直接播放、针对 `.mkv` 和 `.ts` 的内置本地转码，或由 Plex 支持的 HLS 代理。可按媒体轻松切换
- 🌐 浏览器图片缓存与 IndexedDB 元数据缓存

---
→ 一行命令安装：
```
curl -fsSL https://raw.githubusercontent.com/daocha/plex-cat-theatre/main/install.sh | bash
```
---

## 🟢 运行要求

### Python 3.9 或更高版本

当前 Python 包：

- `Flask`
- `waitress`

### 用于元数据探测、预览、缩略图和本地转码的系统二进制工具：

- `ffmpeg`
- `ffprobe`

确认它们可用：

```bash
which ffmpeg
which ffprobe
```

---

## 🚀 快速开始


### → 选项 A：一行命令安装：
```
curl -fsSL https://raw.githubusercontent.com/daocha/plex-cat-theatre/main/install.sh | bash
```

### → 选项 B：使用 pip 从 PyPI 安装

```bash
pip install plex-cat-theatre
plex-cat-theatre-init
plex-cat-theatre --config ~/movies_config.json
```

### → 选项 C：推荐启动方式

```bash
git clone https://github.com/daocha/plex-cat-theatre
cd plex-cat-theatre
./startup.sh
```

这个引导脚本可以：

- 首次运行时根据示例配置创建 `movies_config.json`
- 创建本地 `.venv`
- 将 Python 依赖安装到这个本地虚拟环境中
- 在需要时按配置文件位置创建 `cache/thumbnails` 和 `logs` 目录
- 检查 `ffmpeg` 和 `ffprobe`
- 可选地帮助你生成私密模式口令哈希
- 使用本地配置启动服务器

你仍然可以使用下面的手动流程：

1. 复制示例配置：

```bash
cp movies_config.sample.json movies_config.json
```

2. 按你的环境修改 `movies_config.json`。

### 🌐 启动服务器：

```bash
# 如果你使用选项 A 或选项 B，请运行
plex-cat-theatre --config ~/movies_config.json

# 如果你使用选项 C，请运行
python3 movies_server.py --config movies_config.json
```

打开界面：

```text
http://localhost:9245
```
### 🔑 更改口令
```bash
# 如果你使用选项 A 或选项 B，请运行
plex-cat-theatre-passcode newpasscode

# 如果你使用选项 C，请运行
python3 passcode.py newpasscode
```
- 私密文件夹在设备获准前都会保持隐藏
- 解锁状态绑定到设备 ID
- 已批准设备保存在服务端
- 该脚本可轮换私密模式口令并清除已有授权

---

## 🗂️ 项目结构

- `movies_server.py`：Flask 入口与路由连接
- `movies_server_core.py`：认证、配置、Cookie 与挂载路径处理的通用服务端辅助模块
- `movies_catalog.py`：目录扫描、缩略图生成、字幕提取与本地转码辅助逻辑
- `movies_server_plex.py`：Plex 适配器、海报/字幕映射与 Plex HLS 代理
- `movies.js`：前端源码
- `movies.min.js`：压缩后的前端 bundle
- `movies.css`：图库与播放器样式
- `passcode.py`：用于轮换私密模式口令的辅助脚本

---

## ⚙️ 配置

示例配置经过刻意脱敏，不包含：

- 真实文件系统路径
- 真实 Plex 令牌
- 真实口令哈希
- 设备相关值

### 📍 重要字段

<table>
  <tr>
    <td width="200"><code>root</code></td>
    <td>要扫描的媒体根目录（支持多个文件夹）</td>
  </tr>
  <tr>
    <td><code>thumbs_dir</code></td>
    <td>缩略图与预览帧目录。默认值：<code>./cache/thumbnails</code></td>
  </tr>
  <tr>
    <td><code>private_folder</code></td>
    <td>被视为私密的文件夹前缀。例如 <code>Personal</code>。位于 <code>Personal</code> 文件夹下的内容在你从界面解锁前都会被锁定。</td>
  </tr>
  <tr>
    <td><code>private_passcode</code></td>
    <td>私密模式口令哈希，不应直接用明文修改。如果你想更新它，请参考 <code>更改口令</code> 一节。</td>
  </tr>
  <tr>
    <td><code>mount_script</code></td>
    <td>[可选] 当播放命中缺失的媒体目录且原因是目录意外挂载丢失时要执行的命令。</td>
  </tr>
  <tr>
    <td><code>transcode</code></td>
    <td>启用目录侧后台转码 worker，用于 `.mkv`、`.ts` 等源容器；这可能会在源媒体库旁生成额外的转码 sidecar 文件，因此通常建议保持为 <code>false</code>，尤其是在启用 Plex 集成时。默认值：<code>false</code></td>
  </tr>
  <tr>
    <td><code>auto_scan_on_start</code></td>
    <td>启动时重新扫描媒体。默认值：<code>false</code></td>
  </tr>
  <tr>
    <td><code>on_demand_transcode</code></td>
    <td>启用播放器运行时转码，用于源容器；可优先使用硬件编码，不可用时回退到软件编码。默认值：<code>true</code></td>
  </tr>
  <tr>
    <td><code>on_demand_hls</code></td>
    <td>为源容器启用内置 HLS 播放列表。默认值：<code>true</code></td>
  </tr>
  <tr>
  <td><code>enable_plex_server</code></td>
  <td>📍 [可选] 启用 Plex 集成。默认值：<code>false</code>。启用前请先确认 Plex Server 已正确安装并配置。<br> 该服务器支持原生字幕，但如果你想自动抓取字幕，通常更适合交给 Plex 处理。
  <br> 如果你希望获得更好的按需转码体验，强烈建议安装 Plex server 以实现更顺畅的媒体流播放。<br>
  即使没有 Plex server，这个服务也仍然可以正常工作，但请注意：
  <br>→ 对于你的设备可以直接播放的媒体，拖动定位功能可正常工作。
  <br>→ 对于你的设备无法直接播放的媒体，例如 <code>h.265 + DTS 音频</code>（h.265 + AAC 或 MP3 不受影响）、<code>.mkv</code>、<code>.ts</code> 或 <code>.wmv</code>，此服务仍可在线转码，但拖动定位可能不可用。
  </td>
  </tr>
  <tr>
    <td><code>plex.base_url</code></td>
    <td>Plex 服务器基础 URL。</td>
  </tr>
  <tr>
    <td><code>plex.token</code></td>
    <td>Plex 令牌</td>
  </tr>
  <tr>
    <td><code>debug_enabled</code></td>
    <td>显示内置调试浮层</td>
  </tr>
  <tr>
    <td><code>direct_playback</code></td>
    <td>包含 <code>enabled</code> 与 <code>audio_whitelist</code> 的对象。当 <code>enabled=true</code> 时，可使用原生播放器直接播放媒体而无需转码（速度更快）。建议保留默认设置。</td>
  </tr>
</table>

### 最小本地模式示例

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

### 启用 Plex 集成的示例

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

### 🅿️ Plex 扫描行为

- 当 Plex 海报可用时，会跳过本地海报缩略图生成
- 现有的本地缓存缩略图仍可复用
- 预览帧生成仍保持启用
- Plex 集成仍然是可选的，纯本地模式依然可用

### → 如何获取 Plex 令牌

#### 方法 1：已有 Plex Web 会话

1. 打开 Plex Web 并登录。
2. 打开浏览器开发者工具。
3. 进入网络标签页。
4. 刷新页面。
5. 检查一条发往 Plex 服务器的请求。
6. 在 URL 或请求头中查找 `X-Plex-Token`。

#### 方法 2：浏览器存储

检查：

- 本地存储（`Local Storage`）
- 会话存储（`Session Storage`）
- DevTools 中的请求 URL 与请求头

#### 方法 3：本机直接请求

如果你已经在同一台机器上登录了 Plex Web，会话仍然有效，那么可以在 DevTools 中检查 Plex 请求并查找：

```text
X-Plex-Token=...
```

‼️ 安全提示：

- 请像对待密码一样对待 Plex 令牌
- 不要把它提交进 git
- 只把它保存在 `movies_config.json` 中

---

## 🎥 播放模式

### 1. 原生直接播放

用于 `.mp4`、`.m4v`、`.webm` 等浏览器安全文件。

行为：

- 通过 `/video/<id>` 直接提供本地文件
- 支持 HTTP Range 请求
- 当浏览器可以原生播放文件时，避免转码开销

最适合：

- MP4/H.264 一类文件
- 浏览器本身已支持直接播放的文件
- 音频编解码器符合 direct-play 白名单的文件

### 2. 不依赖 Plex 的内置本地转码

当 Plex 未启用，或你明确想保持完全本地时，会走这个回退路径。

当前实现：

- `.mkv` 与 `.ts` 可通过 `/hls/<id>/index.m3u8` 以本地 HLS 形式提供
- 同一批文件也可通过 `/video/<id>?fmp4=1` 以 fragmented MP4 形式流式播放
- HLS 分片按需用 `ffmpeg` 生成
- 会优先尝试硬件编码，必要时回退到 `libx264`
- fMP4 输出使用 `libx264` + AAC 生成

### 3. 由 Plex 支持的播放

启用 Plex 集成后：

- 前端可使用 `plex_stream_url` 处理更依赖兼容性的播放
- Plex 生成上游 HLS 播放列表
- 本服务会重写播放列表并代理嵌套播放列表与分片请求
- 浏览器仍然是与本应用通信，而不是直接连 Plex

最适合：

- 在编解码器或容器支持较弱设备上播放 MKV 或 TS 内容
- 更适合使用 Plex 做字幕选择或流标准化的场景

### 播放选择策略

- 对于浏览器安全且音频编解码器符合 `direct_playback.audio_whitelist` 的文件，优先直接播放
- 对于 `.mkv`、`.ts`、HLS、fMP4 或不受支持的音频编解码器，仍优先选择 Plex
- iOS 原生 HLS 回退会等待更久，以便给 Plex 流预热时间

### 默认播放逻辑

- 当直接 URL 是真实文件路径且音频编解码器在白名单内时，`.mp4`、`.m4v`、`.webm` 与 `.avi` 优先使用 `Direct`
- 如果这些浏览器安全扩展名缺少音频编解码器元数据，应用仍会优先 `Direct`
- 对于 `.mkv`、`.ts`、HLS/fMP4 直接 URL，以及已知音频编解码器不在白名单中的文件，则优先 `Plex`
- 如果找不到 Plex 匹配项，应用会回退到 `Direct`

---

## 认证模型

应用会根据请求类型使用不同的传输方式：

- API 请求使用 `X-Device-Id` 请求头
- HLS 与 Plex 代理请求使用 `X-Device-Id` 请求头
- 原生直接媒体请求使用 `movies_device_id` Cookie 回退

这样拆分是因为原生 `<video src="...">` 请求无法附带任意自定义请求头。

---

## 反向代理与上下文路径支持

应用支持部署在如下子路径下：

- `https://example.com/movie/`
- `https://example.com/cinema/`

路由会为以下资源保留当前挂载前缀：

- 直接媒体
- 本地 HLS
- Plex HLS 代理请求
- 海报与字幕资源

---

## 通过 Tailscale 远程访问 Plex

如果自定义界面可远程访问，但 Plex 只能在私有局域网中访问，那么 movies server 所在主机仍必须能够直接访问 Plex 后端。

### 同机部署

```json
"plex": {
  "base_url": "http://127.0.0.1:32400"
}
```

### Plex 位于另一台局域网机器

在能够访问 Plex 的 Tailscale 节点上通告路由：

```bash
sudo tailscale up --advertise-routes=192.168.50.0/24
```

然后在 movies server 主机上验证可达性：

```bash
curl http://192.168.50.10:32400/identity
```

📌 注意：

- 浏览器不需要直接访问 Plex
- movies server 进程必须能够访问 `plex.base_url`
- 界面的反向代理或 MagicDNS 名称本身不会让 Plex 自动变得可达

---

## 💾 缓存策略

### 图片缓存

缩略图、预览帧与 Plex 海报图片都会以长期 immutable cache header 提供。

### 元数据缓存

图库元数据快照会缓存在 IndexedDB 中，并带有受控的存储上限：

- 1 天 TTL
- 最多 8 条快照记录
- 总估算大小最多约 18 MB
- 超出限制时会淘汰较旧记录

每条缓存快照会保存：

- 服务端 `catalogStatus`
- 文件夹列表缓存
- 已加载的 `videos`
- 如 `serverTotal`、`serverOffset` 与 `serverExhausted` 之类的分页计数器

淘汰策略是机会式的，而不是定时任务：

- 过期项会在读取时或后续清理时被移除
- 新快照保存后会执行清理
- 浏览器存储压力或手动清除站点数据，也可能删除 IndexedDB 数据

---

## 🔍 扫描行为

目录扫描被设计为即使仍会遍历每个已配置根目录，整体成本也尽量保持增量化。

当前行为：

- 未变化文件会复用缓存的 `mtime + size` 签名
- 周期性扫描不再在处理前对完整路径列表排序
- 已删除文件会从内存目录与持久化索引中移除
- 已删除文件也会触发对已生成缩略图和预览产物的清理
- 保存索引时会复用缓存的文件签名数据，而不是重新对每个文件做 `stat`

扫描仍会做的事：

- 遍历已配置媒体根目录，检测新增、变更和删除文件
- 当缺少预览图时，将预览生成加入队列

扫描不会做的事：

- 周期性扫描时不会对大型媒体文件做 checksum
- 只要缓存产物还在，就不会为未变化文件重新生成缩略图或元数据

### → 触发重新扫描

普通增量重扫：

```bash
curl -s http://localhost:9245/rescan | python3 -m json.tool
```

强制完整重扫：

```bash
curl -s "http://localhost:9245/rescan?full=1" | python3 -m json.tool
```

### → 重扫界面

`Rescan` 按钮不会立即启动增量扫描，而是会打开一个操作对话框。

可用操作：

- `Rescan`：对新增或变更文件执行增量扫描
- `Full Scan`：清除已保存的扫描状态并强制完整元数据重新校验
- `Refresh Database`：清除浏览器 IndexedDB 快照并重新加载最新目录数据

### ⛓️‍💥 缺失挂载恢复

这个功能主要针对某些 NAS 启用了自动休眠，导致 SMB 挂载在某些操作系统中被自动弹出的情况。

如果已配置 `mount_script`，且某个媒体请求命中了缺失目录，服务器会：

1. 检测父目录不存在
2. 调用一次已配置的挂载脚本
3. 再次检查目标路径
4. 只有在目录仍不可用时，才返回 `Media folder is not mounted` 和 HTTP 404

前端会把播放阶段的 404 视为本次尝试的终止条件，并显示重试提示，而不是持续反复请求服务器。

---

## 📄 生成的文件

以下文件会在运行时生成，不应提交到仓库：

- `movies_config.json`
- `movies_state.json`
- `movies_auth_state.json`
- `movies_catalog_index.json`
- `cache/`

---

## 🛠️ 故障排查


### → 调试浮层

在 `movies_config.json` 中启用 `debug_enabled`，即可让右下角常驻调试浮层。

该面板会显示：

- 服务端当前偏向直接播放还是 Plex
- 已配置的 direct-play 音频白名单
- 当前播放候选项与视频 ID
- 最近的扫描进度指标

查看当前生效配置值：

```bash
curl -s http://localhost:9245/api/config | python3 -m json.tool
```

### → 界面改动没有出现

- 当前应用是直接从 `index.html` 加载 `movies.js`，因此前端改动无需重新构建 `movies.min.js` 即可生效。
- 先正常刷新页面
- 如果 JS bundle 已改动，确认 `index.html` 引用的是预期版本的 bundle

### → 私密内容的直接播放失败

- 请重新解锁私密模式，以刷新 `movies_device_id` Cookie

### → Plex 播放失败但直接播放正常

- 确认 movies server 主机可以访问 `plex.base_url`
- 确认配置中已启用 Plex
- 确认所配置 token 有效

### → 直接播放失败但 Plex 正常

- 该设备上的浏览器原生播放很可能不安全支持该容器或编解码器
- 可继续为这些文件启用 Plex，或通过本地转码 / Plex 强制走兼容路径

### → 本地转码不工作

- 确认已安装 `ffmpeg` 与 `ffprobe`
- 确认已启用 `on_demand_transcode`
- 确认源文件属于当前受支持容器：`.mkv` 或 `.ts`

---

## 📦 发布版本规则

包版本号来自 Git tag。

- TestPyPI / testing：使用开发版本，例如 `2026.3.26.dev1`
- PyPI 预发布：使用候选版本，例如 `2026.3.26rc1`
- PyPI 正式版：使用稳定版本，例如 `2026.3.26`
- Git tag 应为 `v2026.3.26.dev1`、`v2026.3.26rc1` 与 `v2026.3.26`
  
---

## ©️ 许可证

本项目基于 MIT License 发布。发布或再分发时，请附带包含 MIT 文本的 `LICENSE` 文件。
