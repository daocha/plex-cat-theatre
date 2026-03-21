# Cat Theatre Movies Server

> Selbstgehosteter Film-Browser und Streaming-Server auf Basis von Flask, Waitress und `ffmpeg`, mit optionaler Plex-Integration für kompatibilitätsorientierte Wiedergabe.

**Sprachen**

[English](./README.md) | `Deutsch`

---

## Überblick

Cat Theatre ist bewusst leichtgewichtig:

- kleine Python-Abhängigkeiten
- keine Datenbank notwendig
- dateisystemzentrierter Katalog
- portables Polling-Scanning
- Plex bleibt optional

Geeignet für:

- lokale Medienbibliotheken über mehrere Ordner hinweg
- Thumbnail- und Preview-Erzeugung
- gerätebasierte Freigabe privater Ordner
- Reverse-Proxy-Betrieb unter einem Präfix wie `/movie/`
- Direct Play, lokales Transcoding und Plex HLS

---

## Funktionen

- Multi-Root-Scan
- Poster-Thumbnails und Preview-Frames
- private Ordner
- natives Direct Play
- lokales Transcoding für `.mkv` und `.ts`
- Plex-Integration
- Unterstützung für Reverse-Proxy-Unterpfade
- Browser-Bildcache und IndexedDB-Metadatencache

---

## Projektstruktur

- `movies_server.py`
- `movies_server_core.py`
- `movies_catalog.py`
- `movies_server_plex.py`
- `movies.js`
- `movies.min.js`
- `movies.css`
- `passcode.py`

---

## Anforderungen

```bash
pip install -r requirements.txt
which ffmpeg
which ffprobe
```

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

## Konfiguration

Wichtige Felder:

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

## Wiedergabemodi

- Direct Play: `/video/<id>`
- lokales Transcoding: `/hls/<id>/index.m3u8` oder `/video/<id>?fmp4=1`
- Plex-Wiedergabe: Plex erzeugt HLS, diese App proxyt es

### Standardlogik für die Wiedergabe

- `Direct` wird für `.mp4`, `.m4v`, `.webm` und `.avi` bevorzugt, wenn die direkte URL auf eine echte Datei zeigt und die Audiocodecs zur Whitelist passen
- fehlen bei diesen browserfreundlichen Endungen die Audiometadaten, bevorzugt die App trotzdem `Direct`
- `Plex` wird für `.mkv`, `.ts`, direkte HLS/fMP4-URLs und Dateien mit bekannten Audiocodecs außerhalb der Whitelist bevorzugt
- gibt es keinen Plex-Treffer, fällt die App auf `Direct` zurück

---

## Cache und Scan

- langlebige Bild-Caches
- IndexedDB-Snapshots mit 1 Tag TTL
- bis zu 8 Snapshots
- etwa 18 MB Obergrenze
- `/rescan?full=1` erzwingt vollständige Neuvalidierung

---

## Privater Modus und Debug

- private Ordner sind standardmäßig verborgen
- Freischaltung ist gerätegebunden
- `passcode.py` kann den Passcode rotieren
- `debug_enabled` blendet das Debug-Overlay ein

---

## Fehlerbehebung

- bei Plex-Problemen `plex.base_url` und Token prüfen
- bei lokalem Transcoding `ffmpeg`, `ffprobe` und `on_demand_transcode` prüfen
