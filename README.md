# Cat Theatre Movies Server

> Lightweight self-hosted movie browser and streaming server built with Flask, Waitress, and `ffmpeg`.

**Languages**

`English` | [简体中文](./README.zh-CN.md) | [繁體中文（香港）](./README.zh-HK.md) | [繁體中文（台灣）](./README.zh-TW.md) | [Français](./README.fr.md) | [한국어](./README.ko.md) | [日本語](./README.ja.md) | [Deutsch](./README.de.md) | [ไทย](./README.th.md) | [Tiếng Việt](./README.vi.md) | [Nederlands](./README.nl.md)

---

## What It Is

Cat Theatre is designed for local media libraries that need:

- file-system-first cataloging
- thumbnail and preview generation
- device-based private-folder access
- reverse-proxy deployment under a path prefix such as `/movie/`
- direct playback, local transcoding, or Plex-backed playback

It stays intentionally small:

- no database required
- small Python dependency surface
- portable polling-based scans instead of OS-specific watcher requirements
- Plex is optional, not required for core playback

---

## Highlights

| Area | What You Get |
| --- | --- |
| Library | Multi-root scanning, private folders, browser-side snapshot cache |
| Media | Thumbnails, preview frames, subtitle extraction, direct-play safety checks |
| Playback | Native direct play, local HLS/fMP4 transcoding, optional Plex HLS |
| Deployment | Reverse-proxy path-prefix support, mount recovery hook, low dependency footprint |

---

## Project Layout

- `movies_server.py`: Flask entrypoint and route wiring
- `movies_server_core.py`: shared server helpers, config loading, auth helpers, path handling
- `movies_catalog.py`: scanning, metadata probing, thumbs, previews, subtitles, local transcode helpers
- `movies_server_plex.py`: Plex adapter, poster/subtitle mapping, Plex HLS proxy support
- `movies.js`: frontend source
- `movies.min.js`: minified frontend bundle
- `movies.css`: gallery and player styles
- `passcode.py`: private-passcode helper

---

## Requirements

### Python

```bash
pip install -r requirements.txt
```

Packages:

- `Flask`
- `waitress`

### System Tools

```bash
which ffmpeg
which ffprobe
```

Required for:

- thumbnail generation
- preview generation
- metadata probing
- on-demand transcoding

---

## Quick Start

### 1. Copy the sample config

```bash
cp movies_config.sample.json movies_config.json
```

### 2. Edit the config

Minimum fields to review:

- `root`
- `thumbs_dir`
- `private_folder`
- `private_passcode`
- `mount_script`
- `enable_plex_server`
- `direct_playback`

### 3. Start the server

```bash
python3 movies_server.py --config movies_config.json
```

### 4. Open the UI

```text
http://localhost:9245
```

If you deploy behind a reverse proxy under `/movie/`, open the prefixed path instead.

---

## Configuration Notes

### Important Fields

- `root`: media roots to scan
- `thumbs_dir`: where thumbnails and preview frames are stored
- `private_folder`: folder prefixes treated as private
- `private_passcode`: private-mode passcode hash
- `mount_script`: optional remount command used when playback hits an offline media folder
- `auto_scan_on_start`: scan automatically on startup
- `on_demand_transcode`: enable local transcoding
- `on_demand_hls`: enable local HLS playlists
- `enable_plex_server`: enable Plex integration
- `plex.base_url`: Plex server URL
- `plex.token`: Plex token
- `debug_enabled`: show the floating debug panel
- `direct_playback.enabled`: enable direct playback path
- `direct_playback.audio_whitelist`: allowed direct-play audio codecs

### Minimal Local-Only Example

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

### Plex Example

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

### Plex Scan Behavior

- local poster thumbnail generation is skipped when Plex posters are available
- existing cached local thumbs can still be reused
- preview-frame generation still runs
- Plex stays optional; local-only mode still works

---

## Playback Paths

### 1. Native Direct Playback

Best for browser-safe files such as `.mp4`, `.m4v`, and `.webm`.

- streams from `/video/<id>`
- supports range requests
- uses the direct-play audio whitelist

### 2. Local Transcoding Without Plex

Used when Plex is disabled or when you want a fully local stack.

- local HLS via `/hls/<id>/index.m3u8`
- fragmented MP4 fallback via `/video/<id>?fmp4=1`
- source-container support is currently centered on `.mkv` and `.ts`

### 3. Plex-Backed Playback

Used for compatibility-sensitive playback.

- Plex HLS playlist proxying
- Plex posters
- Plex subtitles
- Plex-backed fallback path for harder formats

---

## Plex Token

Common ways to get it:

### Existing Plex Web Session

1. Open Plex Web and sign in.
2. Open browser DevTools.
3. Refresh the page.
4. Inspect a request to your Plex server.
5. Find `X-Plex-Token` in the URL or headers.

### Browser Storage

Check:

- Local Storage
- Session Storage
- request URLs in DevTools

Security:

- treat the Plex token like a password
- do not commit it
- keep it only in `movies_config.json`

---

## UX Notes

- The debug panel starts in the bottom-right and can be dragged.
- Playback mode selection can switch between direct and Plex paths.
- Browser snapshot caching speeds up reloads while respecting storage limits.
- Mobile zoom layouts support both classic and snapshot-style transitions where enabled.

---

## Operational Notes

### Private Mode

- unlock is device-based
- browser cache is cleared when locking or unlocking
- private visibility follows server authorization state

### NAS / Mount Recovery

- if `mount_script` is configured, playback can attempt self-recovery before returning a missing-media error

### Reverse Proxy

- the app supports path-prefix mounting
- routes stay valid under prefixes such as `/movie/`

---

## Running Behind Launchd / LaunchAgent

Typical start command:

```bash
python3 movies_server.py --config movies_config.json
```

Recommended:

- keep logs outside the repo
- restart after config changes that affect server behavior

---

## Development

Useful checks:

```bash
python3 -m py_compile movies_server.py movies_server_core.py movies_server_plex.py movies_catalog.py
node --check movies.js
```

If you use `movies.min.js`, regenerate it after frontend changes.
