# Cat Theatre filmserver

> Lichte self-hosted filmbrowser en streamingserver op basis van Flask, Waitress en `ffmpeg`.

[English](./README.md)

---

## Belangrijkste functies

- bibliotheekscan over meerdere roots
- thumbnails en previewframes
- privé-mappen met apparaatgebaseerde ontgrendeling
- direct afspelen, lokale transcodering of Plex-weergave
- ondersteuning voor reverse-proxy-prefixen zoals `/movie/`

---

## Snel starten

```bash
cp movies_config.sample.json movies_config.json
python3 movies_server.py --config movies_config.json
```

Open:

```text
http://localhost:9245
```

---

## Belangrijke configuratie

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

## Afspeelmodi

### Direct afspelen

- geschikt voor `.mp4`, `.m4v`, `.webm`
- route: `/video/<id>`

### Lokale transcodering

- HLS: `/hls/<id>/index.m3u8`
- fMP4: `/video/<id>?fmp4=1`

### Plex

- Plex HLS
- Plex-posters
- Plex-ondertitels

---

## Controlecommando's

```bash
python3 -m py_compile movies_server.py movies_server_core.py movies_server_plex.py movies_catalog.py
node --check movies.js
```
