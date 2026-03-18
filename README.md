# Cat Theatre Movies Server 🎬

A self-hosted movie browser and streaming server built with Flask, Waitress, and `ffmpeg`, with optional Plex integration for compatibility-focused playback.

The project is intentionally lightweight:

- small Python dependency surface
- no database requirement
- file-system-first cataloging
- portable polling-based scan flow instead of OS-specific watcher dependence
- optional Plex integration layered on top rather than required for core playback

It is designed for:

- 📂 local media libraries spread across one or more folders
- 🖼️ thumbnail and preview generation
- 🔐 private-folder access control by device
- 🌐 reverse-proxy deployment under a path prefix such as `/movie/`
- 🎧 mixed playback strategies: direct file playback, built-in local transcoding, or Plex-backed HLS

## Features

- 🔍 Multi-root media scanning
- 🎞️ Poster thumbnails and preview frame generation
- 🗝️ Private folders with device-based unlock
- ✅ Native direct playback for browser-safe formats (AAC/MP3 whitelist)
- 🧊 Built-in local transcoding for `.mkv` and `.ts` when enabled
- 💎 Deep Plex Server integration for playback, posters, subtitles, and HLS proxying
- 🔁 Context-path-aware routing for reverse proxies
- 🗄️ Aggressive browser image caching plus IndexedDB metadata cache with configurable TTL

### UX & Playback Notes ✨

- The built-in debug panel lives in the bottom-right, stays fully visible on load, and slides to the nearest edge when you drag it far enough (~30% hidden). Tap the exposed edge to slide it back in without changing its vertical position, and a small dot reminds you the panel is off-screen.
- Video playback automatically chooses the safer path: direct play for supported browsers, Plex HLS for heavy containers, and manual toggles are stored per-video in IndexedDB with no TTL.
- Cached thumbnails and metadata respect your browser storage limits while keeping frequently-used results fresh.

## Project Structure

- `movies_server.py`: Flask app entrypoint and route wiring
- `movies_server_core.py`: shared server helpers for auth, config, cookies, and mount-path handling
- `movies_catalog.py`: catalog scanning, thumbnail generation, subtitle extraction, and local transcode helpers
- `movies_server_plex.py`: Plex adapter, poster/subtitle mapping, Plex HLS proxying
- `movies.js`: frontend source
- `movies.min.js`: frontend bundle loaded by `index.html`
- `movies.css`: gallery and player styles
- `passcode.py`: helper for rotating the private-mode passcode

## Requirements

### Python

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Current `requirements.txt` covers the Python packages used by the server:

- `Flask`
- `waitress`

### System Binaries

The built-in transcoding and preview generation paths require:

- `ffmpeg`
- `ffprobe`

Verify they are available:

```bash
which ffmpeg
which ffprobe
```

## Quick Start

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

## Configuration

The sample config is intentionally sanitized and does not include:

- real file-system paths
- real Plex tokens
- real passcodes
- device-specific values

Important fields:

- `root`: media roots to scan
- `thumbs_dir`: directory for thumbnails and preview frames
- `private_folder`: folder prefixes treated as private
- `private_passcode`: private-mode passcode hash
- `auto_scan_on_start`: rescan media on startup
- `on_demand_transcode`: enable built-in transcoding for source containers
- `on_demand_hls`: enable built-in HLS playlists for source containers
- `enable_plex_server`: enable Plex integration
- `plex.base_url`: Plex server base URL
- `plex.token`: Plex token
- `debug_enabled`: show the built-in debug overlay (bottom-right) that reports scan status and candidate selection
- `direct_playback`: object with `enabled` (default `true`) and `audio_whitelist` (default `["aac","mp3"]`); direct playback is allowed only when a file's audio codecs are a subset of this whitelist

### Minimal Local-Only Example

Use this mode when you do not want Plex involved at all:

```json
{
  "root": [
    "~/Movies"
  ],
  "thumbs_dir": "./cache/thumbs",
  "private_folder": [],
  "private_passcode": "",
  "on_demand_transcode": true,
  "on_demand_hls": true,
  "enable_plex_server": false,
  "auto_scan_on_start": true
}
```

### Plex-Integrated Example

Use this mode when you want Plex-backed playback for compatibility-sensitive formats:

```json
{
  "root": [
    "~/Movies"
  ],
  "thumbs_dir": "./cache/thumbs",
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

Plex scan behavior:

- local poster thumbnail generation is skipped to avoid unnecessary `ffmpeg` work
- existing cached local thumbnails can still be reused if they already exist
- preview-frame generation remains enabled, because Plex posters do not replace hover or tap previews
- Plex integration stays optional; the server still works in local-only mode without Plex

### How to Get a Plex Token

You need a Plex token for the optional Plex integration.

Common ways to get it:

#### Method 1: From an Existing Plex Web Session

1. Open the Plex web app in your browser and sign in.
2. Open browser developer tools.
3. Go to the Network tab.
4. Refresh the page.
5. Inspect any request sent to your Plex server.
6. Look for the `X-Plex-Token` value in the request URL or headers.

#### Method 2: From Browser Storage

In Plex Web, the token is often present in browser storage for the Plex app session. You can inspect:

- Local Storage
- Session Storage
- request headers or query parameters in DevTools

Search for `X-Plex-Token`.

#### Method 3: From a Direct Local Request

If you already have a working Plex web session on the same machine, you can sometimes see the token by visiting Plex-related requests in DevTools and checking the request URL for:

```text
X-Plex-Token=...
```

Security notes:

- treat the Plex token like a password
- do not commit it into git
- keep it only in `movies_config.json`, which is gitignored in this project

## Playback Modes

The application supports three playback paths.

### 1. Native Direct Playback

Used for browser-safe files such as `.mp4`, `.m4v`, and `.webm`.

Behavior:

- serves the local file directly from `/video/<id>`
- supports HTTP range requests for seeking
- avoids transcoding overhead when the browser can play the file natively

Best for:

- MP4/H.264-style files
- devices and browsers known to support the file directly
- audio codecs that match the `direct_playback.audio_whitelist` (default `["aac","mp3"]`); mismatched codecs such as DTS will fall through to the Plex-backed path for compatibility

### 2. Built-In Local Transcoding Without Plex

This is the fallback path when Plex is not enabled, or when you intentionally want to stay fully local.

Current implementation in `movies_server.py`:

- source-container handling is currently implemented for `.mkv` and `.ts`
- when `on_demand_hls` is enabled, those files can be exposed as local HLS at `/hls/<id>/index.m3u8`
- when `on_demand_transcode` is enabled, those files can also be streamed as fragmented MP4 from `/video/<id>?fmp4=1`
- local HLS segments are generated on demand with `ffmpeg`
- HLS segment encoding attempts the configured hardware codec first, then falls back to `libx264` if the hardware path fails
- fMP4 output is generated with software `libx264` + AAC

What this means in practice:

- yes, the server supports full on-demand transcoding without Plex
- yes, it supports a softer compatibility path through fragmented MP4 output
- no, this path is not a full Plex replacement in terms of media-session management or device-specific codec negotiation
- yes, it is complete enough to serve `.mkv` and `.ts` to browsers that cannot play those containers directly

### 3. Plex-Backed Playback

When Plex integration is enabled:

- the frontend can use `plex_stream_url` for compatibility-sensitive playback
- Plex generates the upstream HLS playlist
- this server rewrites the playlist and proxies nested playlist and segment requests through `/plex/hls/proxy`
- the browser still talks to this app, not directly to the Plex server
- periodic scans skip generating new local poster thumbnails, which reduces background scan cost

This keeps Plex integration strong without making Plex mandatory for the rest of the application:

- the gallery, scanning, auth, and direct/local playback stack still remain lightweight and self-contained
- Plex is used where it adds the most value: hard containers, subtitle selection, and compatibility-focused playback

Best for:

- MKV/TS content on devices with weak codec/container support
- cases where Plex subtitle selection or stream normalization is preferred

## Playback Selection Policy

Current frontend behavior:

- direct playback only wins for `.mp4`, `.m4v`, and `.webm` files whose audio codecs are in the configured `direct_playback.audio_whitelist` (default `["aac","mp3"]`); unsupported codecs such as DTS automatically route through Plex
- Plex stays preferred for `.mkv`/`.ts`, for direct links that are actually fMP4/HLS, or whenever the direct audio whitelist rejects the codec
- the fallback timer is tuned to be longer on native iOS HLS so the Plex stream has more time to warm up before the player switches candidates

This means:

- without Plex, the app still supports direct play and built-in local transcoding
- with Plex, harder containers can be routed through Plex while easy formats stay direct where appropriate

## Debug Overlay

Enable `debug_enabled` in `movies_config.json` to keep a permanent debug overlay in the lower-right corner of the viewer. The panel reports:

- whether the server is favoring direct playback or Plex
- the configured `direct_playback.audio_whitelist`
- the current playback candidate and video ID
- recent scan progress metrics (phase, processed entries, videos seen)

You can inspect the active config values with:

```bash
curl -s http://localhost:9245/api/config | python3 -m json.tool
```

If you serve the app under `/movie/`, use `http://localhost:9245/movie/api/config`. This JSON mirrors the same fields and shows whether `debug_enabled` is on.

## Authentication Model

The app uses different transport methods depending on the request type.

- API requests use the `X-Device-Id` header
- HLS and Plex proxy requests use the `X-Device-Id` header
- native direct media requests use the `movies_device_id` cookie fallback

This split exists because a native `<video src="...">` request cannot attach arbitrary custom headers, while XHR/fetch-based requests can.

## Reverse Proxy and Context Path Support

The app supports deployment under a subpath such as:

- `https://example.com/movie/`
- `https://example.com/cinema/`

Routing is designed to preserve the active mount prefix for:

- direct media
- local HLS
- Plex HLS proxy requests
- poster and subtitle assets

If you change the public context path, the app should continue to generate matching media URLs instead of assuming a hard-coded root path.

## Remote Plex Access With Tailscale Subnet Router

If the custom UI is reachable remotely but the Plex server is only reachable on a private LAN, Plex playback will only work if the movies server host can still reach the Plex backend directly.

### Same Host

If Plex and this app run on the same machine, use loopback:

```json
"plex": {
  "base_url": "http://127.0.0.1:32400"
}
```

No subnet router is needed in that case.

### Plex on Another Machine in the LAN

Advertise the LAN route from a Tailscale node that can reach Plex:

```bash
sudo tailscale up --advertise-routes=192.168.50.0/24
```

Approve the route in the Tailscale admin console, then verify reachability from the movies server host:

```bash
curl http://192.168.50.10:32400/identity
```

Then point the app to the Plex host on the routed LAN:

```json
"plex": {
  "base_url": "http://192.168.50.10:32400"
}
```

Notes:

- the browser does not need direct network access to Plex
- the movies server process must be able to reach `plex.base_url`
- a reverse proxy or MagicDNS name for the UI does not automatically make Plex reachable

## Caching Strategy

### Image Caching

Thumbnails, preview frames, and Plex poster images are served with long-lived immutable cache headers so repeat visits and normal refreshes can reuse disk cache more aggressively.

### Metadata Caching

Gallery metadata snapshots are cached in IndexedDB with bounded storage:

- 1-day TTL
- maximum record count
- maximum estimated total size
- eviction of older entries when limits are exceeded

This improves page bootstrap time, but image HTTP caching is the larger contributor to perceived gallery responsiveness.

## Scan Behavior

The catalog scan is designed to be incremental in cost even though it still walks each configured root.

Current behavior:

- unchanged files reuse cached `mtime + size` signatures so aspect probing and subtitle resolution are skipped
- periodic scans no longer sort the full path list before processing, which reduces needless traversal overhead
- deleted files are removed from the in-memory catalog and from the persisted catalog index
- deleted files also trigger cleanup of generated thumbnail and preview-cache artifacts
- index saves reuse cached file signature data instead of statting every file again during persistence

What the scan still does:

- it still walks the configured media roots to detect added, changed, and deleted files
- it still queues preview generation when preview images are missing

What it does not do:

- it does not checksum large media files during periodic scans
- it does not regenerate thumbnails, previews, or metadata for unchanged files unless their cached artifacts are missing

### Force Full Rescan

Normal rescans are incremental. If you want to force a true full rebuild of scan-derived state, use:

```text
/rescan?full=1
```

This is useful if:

- someone manually deleted the thumbnail or preview cache folder
- you suspect the saved scan manifest is stale
- you want to invalidate the saved scan caches and rebuild derived scan state from scratch

What `full=1` does:

- clears the saved scan signature and readiness caches in memory
- forces the next scan to treat files as needing full validation
- keeps the resumable checkpoint and persisted catalog behavior intact during the scan

Practical note:

- if the cache folder is deleted, a normal incremental rescan will usually regenerate missing derived assets anyway
- `full=1` is the explicit recovery mode when you want deterministic full revalidation

### Check Scan Status

To inspect current server and scan state in a readable way:

```bash
curl -s http://localhost:9245/api/status | python3 -m json.tool
```

If you serve the app under a context path such as `/movie/`, use:

```bash
curl -s http://localhost:9245/movie/api/status | python3 -m json.tool
```

This shows:

- whether the catalog is currently scanning
- the current `scan_progress` payload
- video counts
- private-mode and Plex status

### Trigger Rescan

Normal incremental rescan:

```bash
curl -s http://localhost:9245/rescan | python3 -m json.tool
```

Forced full rescan:

```bash
curl -s "http://localhost:9245/rescan?full=1" | python3 -m json.tool
```

If you use a context path such as `/movie/`, prepend it to the endpoint:

```bash
curl -s "http://localhost:9245/movie/rescan?full=1" | python3 -m json.tool
```

## Frontend Development Notes

If you edit `movies.js`, rebuild `movies.min.js` before serving changes:

```bash
npx terser movies.js -c -m -o movies.min.js
```

Then bump the `movies.min.js?v=...` value in `index.html` so browsers fetch the updated bundle instead of reusing the old cached asset.

## Private Mode

- private folders are hidden unless the device is authorized
- unlock state is tied to a device id
- approved devices are stored server-side
- `passcode.py` can rotate the private-mode passcode and clear approvals

Example:

```bash
python3 passcode.py mynewpasscode
```

## Generated Files

These files are runtime-generated and should not be committed:

- `movies_config.json`
- `movies_state.json`
- `movies_auth_state.json`
- `movies_catalog_index.json`
- `cache/`

## Troubleshooting

### UI Changes Do Not Appear

- refresh the page normally first
- if the JS bundle changed, confirm `index.html` references a new `movies.min.js?v=...` value

### Direct Private Playback Fails

- unlock private mode again so the `movies_device_id` cookie is refreshed

### Plex Playback Fails but Direct Playback Works

- verify the movies server host can reach `plex.base_url`
- verify Plex is enabled in config
- verify the configured token is valid

### Direct Playback Fails but Plex Works

- the container or codec is likely not safe for native browser playback on that device
- keep Plex enabled for those files, or force the compatibility path through local transcode or Plex

### Local Transcoding Does Not Work

- verify `ffmpeg` and `ffprobe` are installed
- verify `on_demand_transcode` is enabled
- verify the source file is one of the currently supported source containers: `.mkv` or `.ts`

## License

This repository does not currently declare a software license. Add one explicitly if you plan to redistribute it.
