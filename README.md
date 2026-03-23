# Cat Theatre Movies Server

> Lightweight self-hosted movie browser and streaming server built with Flask, Waitress, and `ffmpeg`, with optional _`Plex`_ integration for compatibility-focused playback.

---

![Screenshot 2026-03-22 at 9 39 12 PM](https://github.com/user-attachments/assets/124f21b7-71b0-46fc-9d76-c73f700c25f3)

---

**Languages**

`English` | [简体中文](./README.zh-CN.md) | [繁體中文（香港）](./README.zh-HK.md) | [繁體中文（台灣）](./README.zh-TW.md) | [Français](./README.fr.md) | [한국어](./README.ko.md) | [日本語](./README.ja.md) | [Deutsch](./README.de.md) | [ไทย](./README.th.md) | [Tiếng Việt](./README.vi.md) | [Nederlands](./README.nl.md)

---

## Overview

Cat Theatre is intentionally lightweight:

- small Python dependency surface
- no database requirement
- file-system-first cataloging
- portable polling-based scan flow instead of OS-specific watcher dependence
- optional Plex integration layered on top rather than required for core playback

It is designed for:

- local media libraries spread across one or more folders
- thumbnail and preview generation
- private-folder access control by device
- reverse-proxy deployment under a path prefix such as `/movie/`
- mixed playback strategies: direct file playback, built-in local transcoding, or Plex-backed HLS

---

## Features

- multi-root media scanning
- poster thumbnails and preview frame generation
- private folders with device-based unlock
- native direct playback for browser-safe formats
- built-in local transcoding for `.mkv` and `.ts` when enabled
- Plex integration for playback, posters, subtitles, and HLS proxying
- context-path-aware routing for reverse proxies
- browser image caching plus IndexedDB metadata caching

### UX And Playback Notes

- the built-in debug panel lives in the bottom-right and can slide to the nearest edge
- playback automatically prefers the safer path for the current file and device
- manual direct/Plex overrides are stored per video in IndexedDB
- cached thumbnails and metadata stay within browser storage limits

---

## Requirements

### Python

```bash
pip install -r requirements.txt
```

Current Python packages:

- `Flask`
- `waitress`

### System Binaries

Required for metadata probing, previews, thumbnails, and local transcoding:

- `ffmpeg`
- `ffprobe`

Verify they are available:

```bash
which ffmpeg
which ffprobe
```

---

## Quick Start

If you install the published PyPI package, use:

```bash
pip install plex-cat-theatre
plex-cat-theatre-init
plex-cat-theatre --config ~/movies_config.json
```

Preferred startup method:

```bash
./startup.sh
```

This bootstrap script can:

- create `movies_config.json` from the sample config on first run
- create a local `.venv`
- install Python dependencies into that local virtual environment
- check `ffmpeg` and `ffprobe`
- optionally help you generate the private-mode passcode hash
- start the server with your local config

You can still use the manual flow below:

1. Copy the sample config:

```bash
cp movies_config.sample.json movies_config.json
```

2. Edit `movies_config.json` for your environment.

3. Start the server:

```bash
python3 movies_server.py --config movies_config.json
```

4. Open the UI:

```text
http://localhost:9245
```

If you deploy the app behind a reverse proxy under a prefix such as `/movie/`, open the prefixed URL instead.

---

## Project Structure

- `movies_server.py`: Flask entrypoint and route wiring
- `movies_server_core.py`: shared server helpers for auth, config, cookies, and mount-path handling
- `movies_catalog.py`: catalog scanning, thumbnail generation, subtitle extraction, and local transcode helpers
- `movies_server_plex.py`: Plex adapter, poster/subtitle mapping, and Plex HLS proxying
- `movies.js`: frontend source
- `movies.min.js`: minified frontend bundle
- `movies.css`: gallery and player styles
- `passcode.py`: helper for rotating the private-mode passcode

---

## Configuration

The sample config is intentionally sanitized and does not include:

- real file-system paths
- real Plex tokens
- real passcodes
- device-specific values

### Important Fields

- `root`: media roots to scan
- `thumbs_dir`: directory for thumbnails and preview frames
- `private_folder`: folder prefixes treated as private
- `private_passcode`: private-mode passcode hash
- `mount_script`: optional command used when playback hits a missing media folder
- `transcode`: enable the catalog-side background transcode worker for source containers such as `.mkv` and `.ts`; this can generate separate transcoded sidecar media files alongside the source library, so it is usually best left `false`, especially when Plex integration is enabled
- `auto_scan_on_start`: rescan media on startup
- `on_demand_transcode`: enable runtime player transcoding for source containers, using hardware encode when available and falling back to software encode when needed
- `on_demand_hls`: enable built-in HLS playlists for source containers
- `enable_plex_server`: enable Plex integration
- `plex.base_url`: Plex server base URL
- `plex.token`: Plex token
- `debug_enabled`: show the built-in debug overlay
- `direct_playback`: object with `enabled` and `audio_whitelist`

### Minimal Local-Only Example

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

### Plex-Integrated Example

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

### Plex Scan Behavior

- local poster thumbnail generation is skipped when Plex posters are available
- existing cached local thumbnails can still be reused
- preview-frame generation remains enabled
- Plex integration stays optional and local-only mode still works

### How To Get A Plex Token

#### Method 1: Existing Plex Web Session

1. Open Plex Web and sign in.
2. Open browser developer tools.
3. Go to the Network tab.
4. Refresh the page.
5. Inspect a request sent to your Plex server.
6. Find `X-Plex-Token` in the URL or headers.

#### Method 2: Browser Storage

Check:

- Local Storage
- Session Storage
- request URLs and headers in DevTools

#### Method 3: Direct Local Request

If you already have an active Plex Web session on the same machine, inspect Plex requests in DevTools and look for:

```text
X-Plex-Token=...
```

Security notes:

- treat the Plex token like a password
- do not commit it into git
- keep it only in `movies_config.json`

---

## Playback Modes

### 1. Native Direct Playback

Used for browser-safe files such as `.mp4`, `.m4v`, and `.webm`.

Behavior:

- serves the local file directly from `/video/<id>`
- supports HTTP range requests
- avoids transcoding overhead when the browser can play the file natively

Best for:

- MP4/H.264-style files
- browsers that already support the file directly
- files whose audio codecs match the direct-play whitelist

### 2. Built-In Local Transcoding Without Plex

This is the fallback path when Plex is not enabled, or when you intentionally want to stay fully local.

Current implementation:

- `.mkv` and `.ts` can be exposed as local HLS at `/hls/<id>/index.m3u8`
- the same files can also be streamed as fragmented MP4 from `/video/<id>?fmp4=1`
- HLS segments are generated on demand with `ffmpeg`
- hardware encode can be tried first and fall back to `libx264`
- fMP4 output is generated with `libx264` plus AAC

### 3. Plex-Backed Playback

When Plex integration is enabled:

- the frontend can use `plex_stream_url` for compatibility-sensitive playback
- Plex generates the upstream HLS playlist
- this server rewrites the playlist and proxies nested playlist and segment requests
- the browser still talks to this app, not directly to Plex

Best for:

- MKV or TS content on devices with weaker codec or container support
- cases where Plex subtitle selection or stream normalization is preferred

### Playback Selection Policy

- direct playback wins for browser-safe files whose audio codecs match `direct_playback.audio_whitelist`
- Plex remains preferred for `.mkv`, `.ts`, HLS, fMP4, or unsupported audio codecs
- iOS-native HLS fallback timing is longer so the Plex stream has time to warm up

### Default Playback Logic

- `Direct` is preferred for `.mp4`, `.m4v`, `.webm`, and `.avi` when the direct URL is a real file path and the audio codecs are whitelist-safe
- if audio codec metadata is missing for one of those browser-safe extensions, the app still prefers `Direct`
- `Plex` is preferred for `.mkv`, `.ts`, HLS/fMP4 direct URLs, and files whose known audio codecs fall outside the whitelist
- if no Plex match exists, the app falls back to `Direct`

---

## Debug Overlay

Enable `debug_enabled` in `movies_config.json` to keep a permanent debug overlay in the lower-right corner.

The panel reports:

- whether the server is favoring direct playback or Plex
- the configured direct-play audio whitelist
- the current playback candidate and video ID
- recent scan progress metrics

Inspect active config values with:

```bash
curl -s http://localhost:9245/api/config | python3 -m json.tool
```

If you serve the app under `/movie/`, use the prefixed path instead.

---

## Authentication Model

The app uses different transport methods depending on request type:

- API requests use the `X-Device-Id` header
- HLS and Plex proxy requests use the `X-Device-Id` header
- native direct media requests use the `movies_device_id` cookie fallback

This split exists because native `<video src="...">` requests cannot attach arbitrary custom headers.

---

## Reverse Proxy And Context Path Support

The app supports deployment under subpaths such as:

- `https://example.com/movie/`
- `https://example.com/cinema/`

Routing preserves the active mount prefix for:

- direct media
- local HLS
- Plex HLS proxy requests
- poster and subtitle assets

---

## Remote Plex Access With Tailscale

If the custom UI is reachable remotely but Plex is only reachable on a private LAN, the movies server host must still be able to reach the Plex backend directly.

### Same Host

```json
"plex": {
  "base_url": "http://127.0.0.1:32400"
}
```

### Plex On Another LAN Machine

Advertise the route from a Tailscale node that can reach Plex:

```bash
sudo tailscale up --advertise-routes=192.168.50.0/24
```

Then verify reachability from the movies server host:

```bash
curl http://192.168.50.10:32400/identity
```

Notes:

- the browser does not need direct network access to Plex
- the movies server process must be able to reach `plex.base_url`
- reverse-proxy or MagicDNS names for the UI do not make Plex reachable by themselves

---

## Caching Strategy

### Image Caching

Thumbnails, preview frames, and Plex poster images are served with long-lived immutable cache headers.

### Metadata Caching

Gallery metadata snapshots are cached in IndexedDB with bounded storage:

- 1-day TTL
- up to 8 snapshot records
- up to about 18 MB estimated total size
- older entries evicted when limits are exceeded

Each cached snapshot stores:

- server `catalogStatus`
- folder list cache
- loaded `videos`
- pagination counters such as `serverTotal`, `serverOffset`, and `serverExhausted`

Eviction is opportunistic rather than scheduled:

- expired entries are removed on read or later pruning
- pruning runs after fresh snapshots are saved
- browser storage pressure or manual site-data clearing can also remove IndexedDB data

---

## Scan Behavior

The catalog scan is designed to stay incremental in cost even though it still walks each configured root.

Current behavior:

- unchanged files reuse cached `mtime + size` signatures
- periodic scans no longer sort the full path list before processing
- deleted files are removed from the in-memory catalog and persisted index
- deleted files also trigger cleanup of generated thumbnail and preview artifacts
- index saves reuse cached file signature data instead of statting every file again

What the scan still does:

- walks configured media roots to detect added, changed, and deleted files
- queues preview generation when preview images are missing

What it does not do:

- it does not checksum large media files during periodic scans
- it does not regenerate thumbnails or metadata for unchanged files unless cached artifacts are missing

### Force Full Rescan

Use:

```text
/rescan?full=1
```

This is useful when:

- someone manually deleted the thumbnail or preview cache folder
- you suspect the saved scan manifest is stale
- you want to force full revalidation of scan-derived state

### Check Scan Status

```bash
curl -s http://localhost:9245/api/status | python3 -m json.tool
```

If you serve the app under `/movie/`, use the prefixed path.

### Trigger Rescan

Normal incremental rescan:

```bash
curl -s http://localhost:9245/rescan | python3 -m json.tool
```

Forced full rescan:

```bash
curl -s "http://localhost:9245/rescan?full=1" | python3 -m json.tool
```

### Rescan UI

The `Rescan` button opens an action dialog instead of immediately starting an incremental scan.

Available actions:

- `Rescan`: incremental scan for new or changed files
- `Full Scan`: clears saved scan state and forces full metadata revalidation
- `Refresh Database`: clears browser IndexedDB snapshots and reloads fresh catalog data

### Missing Mount Recovery

If `mount_script` is configured and a media request hits a missing folder, the server will:

1. detect that the parent folder does not exist
2. invoke the configured mount script once
3. re-check the target path
4. return `Media folder is not mounted` with HTTP 404 only if the folder is still unavailable

The frontend treats playback 404s as terminal for that attempt and shows a retry message instead of repeatedly hammering the server.

---

## Frontend Development Notes

The app currently loads `movies.js` directly from `index.html`, so frontend changes take effect without rebuilding `movies.min.js`.

---

## Private Mode

- private folders are hidden unless the device is authorized
- unlock state is tied to a device ID
- approved devices are stored server-side
- `passcode.py` can rotate the private-mode passcode and clear approvals

Example:

```bash
python3 passcode.py mynewpasscode
```

---

## Generated Files

These files are runtime-generated and should not be committed:

- `movies_config.json`
- `movies_state.json`
- `movies_auth_state.json`
- `movies_catalog_index.json`
- `cache/`

---

## Troubleshooting

### UI Changes Do Not Appear

- refresh the page normally first
- if the JS bundle changed, confirm `index.html` references the expected bundle version

### Direct Private Playback Fails

- unlock private mode again so the `movies_device_id` cookie is refreshed

### Plex Playback Fails But Direct Playback Works

- verify the movies server host can reach `plex.base_url`
- verify Plex is enabled in config
- verify the configured token is valid

### Direct Playback Fails But Plex Works

- the container or codec is likely not safe for native browser playback on that device
- keep Plex enabled for those files, or force the compatibility path through local transcode or Plex

### Local Transcoding Does Not Work

- verify `ffmpeg` and `ffprobe` are installed
- verify `on_demand_transcode` is enabled
- verify the source file is one of the currently supported containers: `.mkv` or `.ts`

---

## License

This project is released under the MIT License. Add a `LICENSE` file containing the MIT text when publishing or redistributing it.
