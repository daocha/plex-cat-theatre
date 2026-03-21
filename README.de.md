# Cat Theatre Filmserver

> Leichter selbstgehosteter Film-Browser und Streaming-Server auf Basis von Flask, Waitress und `ffmpeg`.

[English](./README.md)

---

## Kernfunktionen

- Bibliotheksscan über mehrere Wurzeln
- Thumbnails und Vorschauframes
- private Ordner mit gerätebasierter Freigabe
- Direktwiedergabe, lokale Transkodierung oder Plex-Wiedergabe
- Unterstützung für Reverse-Proxy-Präfixe wie `/movie/`

---

## Schnellstart

```bash
cp movies_config.sample.json movies_config.json
python3 movies_server.py --config movies_config.json
```

Öffnen:

```text
http://localhost:9245
```

---

## Wichtige Konfiguration

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

## Wiedergabemodi

### Direktwiedergabe

- geeignet für `.mp4`, `.m4v`, `.webm`
- Route: `/video/<id>`

### Lokale Transkodierung

- HLS: `/hls/<id>/index.m3u8`
- fMP4: `/video/<id>?fmp4=1`

### Plex

- Plex HLS
- Plex Poster
- Plex Untertitel

---

## Prüfkommandos

```bash
python3 -m py_compile movies_server.py movies_server_core.py movies_server_plex.py movies_catalog.py
node --check movies.js
```
