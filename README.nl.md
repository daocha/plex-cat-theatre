# Cat Theatre Movies Server

> Zelfgehoste filmblader- en streamingserver gebouwd met Flask, Waitress en `ffmpeg`, met optionele Plex-integratie voor compatibiliteitsgerichte weergave.

**Talen**

[English](./README.md) | `Nederlands`

---

## Overzicht

Cat Theatre is bewust lichtgewicht:

- klein Python-afhankelijkheidsoppervlak
- geen database nodig
- bestandssysteemgerichte catalogus
- draagbare polling-scan
- Plex blijft optioneel

Geschikt voor:

- lokale mediabibliotheken over meerdere mappen
- generatie van miniaturen en previews
- apparaatgebonden private mappen
- reverse-proxy-uitrol onder een prefix zoals `/movie/`
- direct play, lokale transcodering en Plex HLS

---

## Functies

- scan met meerdere roots
- poster-miniaturen en previewframes
- private mappen
- native direct play
- lokale transcodering voor `.mkv` en `.ts`
- Plex-integratie
- ondersteuning voor reverse-proxy-subpaden
- browserbeeldcache en IndexedDB-metadatacache

---

## Projectstructuur

- `movies_server.py`
- `movies_server_core.py`
- `movies_catalog.py`
- `movies_server_plex.py`
- `movies.js`
- `movies.min.js`
- `movies.css`
- `passcode.py`

---

## Vereisten

```bash
pip install -r requirements.txt
which ffmpeg
which ffprobe
```

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

## Configuratie

Belangrijke velden:

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

## Afspeelmodi

- direct play: `/video/<id>`
- lokale transcodering: `/hls/<id>/index.m3u8` of `/video/<id>?fmp4=1`
- Plex-weergave: Plex maakt HLS, deze app proxyt het

### Standaard afspeellogica

- `Direct` heeft de voorkeur voor `.mp4`, `.m4v`, `.webm` en `.avi` wanneer de directe URL naar een echt bestand wijst en de audiocodecs binnen de whitelist vallen
- als audiometadata ontbreekt voor deze browserveilige extensies, kiest de app nog steeds voor `Direct`
- `Plex` heeft de voorkeur voor `.mkv`, `.ts`, directe HLS/fMP4-URL's en bestanden waarvan bekende audiocodecs buiten de whitelist vallen
- als er geen Plex-match is, valt de app terug op `Direct`

---

## Cache en scan

- langdurige afbeeldingscache
- IndexedDB-snapshots met TTL van 1 dag
- maximaal 8 snapshots
- ongeveer 18 MB limiet
- `/rescan?full=1` forceert volledige hercontrole

---

## Privémodus en debug

- private mappen zijn standaard verborgen
- ontgrendeling is apparaatgebaseerd
- `passcode.py` kan de passcode vervangen
- `debug_enabled` toont de debug-overlay

---

## Problemen oplossen

- controleer bij Plex-problemen `plex.base_url` en token
- controleer bij lokale transcodering `ffmpeg`, `ffprobe` en `on_demand_transcode`
