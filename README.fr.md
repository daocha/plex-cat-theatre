# Cat Theatre Movies Server

> Serveur auto-hébergé de navigation et de streaming vidéo basé sur Flask, Waitress et `ffmpeg`, avec intégration Plex optionnelle pour la compatibilité de lecture.

**Langues**

[English](./README.md) | `Français`

---

## Vue d'ensemble

Cat Theatre reste léger :

- peu de dépendances Python
- aucune base de données requise
- catalogage centré sur le système de fichiers
- scan par polling portable
- Plex reste optionnel

Il convient à :

- des bibliothèques locales réparties sur plusieurs dossiers
- la génération de miniatures et d'aperçus
- les dossiers privés déverrouillés par appareil
- les déploiements sous préfixe de chemin comme `/movie/`
- la lecture directe, le transcodage local et la lecture Plex HLS

---

## Fonctionnalités

- scan multi-racine
- miniatures d'affiche et images d'aperçu
- dossiers privés
- lecture directe native
- transcodage local pour `.mkv` et `.ts`
- intégration Plex
- prise en charge des sous-chemins de reverse proxy
- cache d'images navigateur et cache IndexedDB

---

## Structure du projet

- `movies_server.py`
- `movies_server_core.py`
- `movies_catalog.py`
- `movies_server_plex.py`
- `movies.js`
- `movies.min.js`
- `movies.css`
- `passcode.py`

---

## Prérequis

```bash
pip install -r requirements.txt
which ffmpeg
which ffprobe
```

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

## Configuration

Champs importants :

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

## Modes de lecture

- lecture directe : `/video/<id>`
- transcodage local : `/hls/<id>/index.m3u8` ou `/video/<id>?fmp4=1`
- lecture Plex : Plex génère le HLS, cette application le proxy

### Logique de lecture par défaut

- `Direct` est préféré pour `.mp4`, `.m4v`, `.webm` et `.avi` lorsque l'URL directe pointe vers un vrai fichier et que les codecs audio respectent la liste blanche
- si les métadonnées audio manquent pour ces extensions considérées sûres par le navigateur, l'application préfère quand même `Direct`
- `Plex` est préféré pour `.mkv`, `.ts`, les URL directes HLS/fMP4 et les fichiers dont les codecs audio connus ne sont pas dans la liste blanche
- s'il n'existe pas de correspondance Plex, l'application revient sur `Direct`

---

## Cache et scan

- cache long pour les images
- snapshots IndexedDB avec TTL d'un jour
- jusqu'à 8 snapshots
- environ 18 Mo maximum
- `/rescan?full=1` force une revalidation complète

---

## Mode privé et debug

- les dossiers privés sont masqués par défaut
- le déverrouillage est lié à l'appareil
- `passcode.py` peut faire tourner le mot de passe
- `debug_enabled` affiche l'overlay de debug

---

## Dépannage

- en cas d'échec Plex, vérifier `plex.base_url` et le token
- en cas d'échec du transcodage local, vérifier `ffmpeg`, `ffprobe` et `on_demand_transcode`
