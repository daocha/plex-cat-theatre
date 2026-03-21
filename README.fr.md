# Serveur de films Cat Theatre

> Serveur léger d’exploration et de lecture vidéo auto-hébergé, basé sur Flask, Waitress et `ffmpeg`.

[English](./README.md)

---

## Points clés

- scan multi-dossiers
- miniatures et images de prévisualisation
- dossiers privés avec déverrouillage par appareil
- lecture directe, transcodage local ou lecture via Plex
- support des préfixes de proxy inverse comme `/movie/`

---

## Démarrage rapide

```bash
cp movies_config.sample.json movies_config.json
python3 movies_server.py --config movies_config.json
```

Ouvrir :

```text
http://localhost:9245
```

---

## Configuration importante

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

## Modes de lecture

### Lecture directe

- idéal pour `.mp4`, `.m4v`, `.webm`
- route : `/video/<id>`

### Transcodage local

- HLS : `/hls/<id>/index.m3u8`
- fMP4 : `/video/<id>?fmp4=1`

### Plex

- HLS Plex
- affiches Plex
- sous-titres Plex

---

## Vérification

```bash
python3 -m py_compile movies_server.py movies_server_core.py movies_server_plex.py movies_catalog.py
node --check movies.js
```
