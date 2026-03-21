# Cat Theatre Movies Server

> Selbst gehosteter Film-Browser und Streaming-Server auf Basis von Flask, Waitress und `ffmpeg`, mit optionaler Plex-Integration für einen stärker kompatibilitätsorientierten Wiedergabepfad.

**Sprachen**

[English](./README.md) | [简体中文](./README.zh-CN.md) | [繁體中文（香港）](./README.zh-HK.md) | [繁體中文（台灣）](./README.zh-TW.md) | [Français](./README.fr.md) | [한국어](./README.ko.md) | [日本語](./README.ja.md) | `Deutsch` | [ไทย](./README.th.md) | [Tiếng Việt](./README.vi.md) | [Nederlands](./README.nl.md)

---

## Überblick

Cat Theatre ist bewusst leichtgewichtig:

- kleine Python-Abhängigkeitsfläche
- keine Datenbank erforderlich
- katalogisiert dateisystemorientiert
- portabler polling-basierter Scan-Ablauf statt Abhängigkeit von OS-spezifischen Watchern
- optionale Plex-Integration als zusätzliche Schicht statt Voraussetzung für die Kernwiedergabe

Es ist ausgelegt für:

- lokale Mediatheken über einen oder mehrere Ordner hinweg
- Generierung von Vorschaubildern und Preview-Frames
- gerätebasierte Zugriffskontrolle für private Ordner
- Deployment hinter einem Reverse Proxy unter einem Präfix wie `/movie/`
- gemischte Wiedergabestrategien: direkte Dateiwiedergabe, eingebautes lokales Transcoding oder Plex-basiertes HLS

---

## Funktionen

- Medien-Scan über mehrere Wurzeln
- Generierung von Poster-Thumbnails und Preview-Frames
- private Ordner mit gerätebasierter Entsperrung
- native Direktwiedergabe für browser-sichere Formate
- eingebautes lokales Transcoding für `.mkv` und `.ts`, wenn aktiviert
- Plex-Integration für Wiedergabe, Poster, Untertitel und HLS-Proxying
- routing mit Kontextpfad-Unterstützung für Reverse Proxies
- Browser-Bildcache plus IndexedDB-Metadatencache

### Hinweise Zu UX Und Wiedergabe

- das eingebaute Debug-Panel sitzt unten rechts und kann zur nächstgelegenen Kante verschoben werden
- die Wiedergabe bevorzugt automatisch den sichereren Pfad für aktuelle Datei und Gerät
- manuelle Direct/Plex-Overrides werden pro Video in IndexedDB gespeichert
- gecachte Thumbnails und Metadaten bleiben innerhalb der Browser-Speichergrenzen

---

## Projektstruktur

- `movies_server.py`: Flask-Einstiegspunkt und Routenverdrahtung
- `movies_server_core.py`: gemeinsame Server-Helfer für Auth, Konfiguration, Cookies und Mount-Pfad-Behandlung
- `movies_catalog.py`: Katalog-Scan, Thumbnail-Erzeugung, Untertitel-Extraktion und lokale Transcoding-Helfer
- `movies_server_plex.py`: Plex-Adapter, Poster-/Untertitel-Zuordnung und Plex-HLS-Proxying
- `movies.js`: Frontend-Quellcode
- `movies.min.js`: minifiziertes Frontend-Bundle
- `movies.css`: Styles für Galerie und Player
- `passcode.py`: Hilfsskript zum Rotieren des Private-Mode-Passcodes

---

## Anforderungen

### Python

```bash
pip install -r requirements.txt
```

Aktuelle Python-Pakete:

- `Flask`
- `waitress`

### System-Binärprogramme

Erforderlich für Metadaten-Ermittlung, Vorschauen, Thumbnails und lokales Transcoding:

- `ffmpeg`
- `ffprobe`

Prüfen, ob sie verfügbar sind:

```bash
which ffmpeg
which ffprobe
```

---

## Schnellstart

1. Beispielkonfiguration kopieren:

```bash
cp movies_config.sample.json movies_config.json
```

2. `movies_config.json` an deine Umgebung anpassen.

3. Server starten:

```bash
python3 movies_server.py --config movies_config.json
```

4. UI öffnen:

```text
http://localhost:9245
```

Wenn du die App hinter einem Reverse Proxy unter einem Präfix wie `/movie/` betreibst, öffne stattdessen die URL mit Präfix.

---

## Konfiguration

Die Beispielkonfiguration ist absichtlich bereinigt und enthält nicht:

- echte Dateisystempfade
- echte Plex-Tokens
- echte Passcodes
- gerätespezifische Werte

### Wichtige Felder

- `root`: zu scannende Medienwurzeln
- `thumbs_dir`: Verzeichnis für Thumbnails und Preview-Frames
- `private_folder`: Ordnerpräfixe, die als privat behandelt werden
- `private_passcode`: Passcode-Hash für den Privatmodus
- `mount_script`: optionaler Befehl, der aufgerufen wird, wenn bei der Wiedergabe ein Medienordner fehlt
- `transcode`: aktiviert den katalogseitigen Hintergrund-Transcode-Worker für Quellcontainer wie `.mkv` und `.ts`; dabei können separate transkodierte Sidecar-Dateien neben der Medienbibliothek erzeugt werden, deshalb sollte dies normalerweise auf `false` bleiben, insbesondere wenn Plex-Integration aktiviert ist
- `auto_scan_on_start`: Medien beim Start erneut scannen
- `on_demand_transcode`: Laufzeit-Transcoding im Player für Quellcontainer aktivieren, wobei nach Möglichkeit Hardware-Encoding verwendet und sonst auf Software-Encoding zurückgefallen wird
- `on_demand_hls`: eingebaute HLS-Playlists für Quellcontainer aktivieren
- `enable_plex_server`: Plex-Integration aktivieren
- `plex.base_url`: Basis-URL des Plex-Servers
- `plex.token`: Plex-Token
- `debug_enabled`: eingeblendetes Debug-Overlay anzeigen
- `direct_playback`: Objekt mit `enabled` und `audio_whitelist`

### Minimales Lokales Beispiel

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

### Beispiel Mit Plex-Integration

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

### Plex-Scan-Verhalten

- lokale Poster-Thumbnail-Erzeugung wird übersprungen, wenn Plex-Poster verfügbar sind
- vorhandene lokale Caches können weiterhin wiederverwendet werden
- Preview-Frame-Erzeugung bleibt aktiviert
- Plex-Integration bleibt optional, lokaler Betrieb funktioniert weiterhin

### So Bekommt Man Einen Plex-Token

#### Methode 1: Vorhandene Plex-Web-Sitzung

1. Plex Web öffnen und anmelden.
2. Entwicklerwerkzeuge des Browsers öffnen.
3. Zum Netzwerk-Tab wechseln.
4. Seite neu laden.
5. Eine Anfrage an den Plex-Server untersuchen.
6. `X-Plex-Token` in URL oder Headern finden.

#### Methode 2: Browser-Speicher

Prüfen:

- Local Storage
- Session Storage
- Request-URLs und Header in DevTools

#### Methode 3: Direkte Lokale Anfrage

Wenn bereits eine aktive Plex-Web-Sitzung auf demselben Rechner läuft, Plex-Anfragen in DevTools untersuchen und nach Folgendem suchen:

```text
X-Plex-Token=...
```

Sicherheitshinweise:

- Plex-Token wie ein Passwort behandeln
- nicht in git committen
- nur in `movies_config.json` speichern

---

## Wiedergabemodi

### 1. Native Direktwiedergabe

Verwendet für browser-sichere Dateien wie `.mp4`, `.m4v` und `.webm`.

Verhalten:

- liefert die lokale Datei direkt über `/video/<id>` aus
- unterstützt HTTP-Range-Requests
- vermeidet Transcoding-Overhead, wenn der Browser die Datei nativ abspielen kann

Am besten geeignet für:

- Dateien im Stil von MP4/H.264
- Browser, die die Datei bereits direkt unterstützen
- Dateien, deren Audiocodecs zur Direktwiedergabe-Whitelist passen

### 2. Eingebautes Lokales Transcoding Ohne Plex

Dies ist der Fallback-Pfad, wenn Plex nicht aktiviert ist oder wenn du bewusst vollständig lokal bleiben willst.

Aktuelle Implementierung:

- `.mkv` und `.ts` können als lokales HLS unter `/hls/<id>/index.m3u8` bereitgestellt werden
- dieselben Dateien können auch als fragmentiertes MP4 über `/video/<id>?fmp4=1` gestreamt werden
- HLS-Segmente werden bei Bedarf mit `ffmpeg` erzeugt
- Hardware-Encoding kann zuerst versucht werden und dann auf `libx264` zurückfallen
- fMP4-Ausgabe wird mit `libx264` plus AAC erzeugt

### 3. Plex-Gestützte Wiedergabe

Wenn Plex-Integration aktiviert ist:

- kann das Frontend `plex_stream_url` für kompatibilitätsorientierte Wiedergabe verwenden
- Plex erzeugt die vorgelagerte HLS-Playlist
- dieser Server schreibt die Playlist um und proxyt verschachtelte Playlists und Segment-Requests
- der Browser spricht weiterhin mit dieser App, nicht direkt mit Plex

Am besten geeignet für:

- MKV- oder TS-Inhalte auf Geräten mit schwächerer Codec- oder Container-Unterstützung
- Fälle, in denen Plex-Untertitelauswahl oder Stream-Normalisierung bevorzugt wird

### Richtlinie Für Die Wiedergabeauswahl

- Direktwiedergabe gewinnt bei browser-sicheren Dateien, deren Audiocodecs zu `direct_playback.audio_whitelist` passen
- Plex bleibt bevorzugt für `.mkv`, `.ts`, HLS, fMP4 oder nicht unterstützte Audiocodecs
- das iOS-native HLS-Fallback-Timing ist länger, damit der Plex-Stream Zeit zum Aufwärmen hat

### Standardlogik Für Die Wiedergabe

- `Direct` wird für `.mp4`, `.m4v`, `.webm` und `.avi` bevorzugt, wenn die Direct-URL ein echter Dateipfad ist und die Audiocodecs Whitelist-sicher sind
- fehlen Audiocodec-Metadaten bei einer dieser browser-sicheren Erweiterungen, bevorzugt die App trotzdem `Direct`
- `Plex` wird für `.mkv`, `.ts`, HLS/fMP4-Direct-URLs und Dateien bevorzugt, deren bekannte Audiocodecs außerhalb der Whitelist liegen
- existiert kein Plex-Match, fällt die App auf `Direct` zurück

---

## Debug-Overlay

Aktiviere `debug_enabled` in `movies_config.json`, um ein dauerhaftes Debug-Overlay unten rechts einzublenden.

Das Panel zeigt:

- ob der Server Direktwiedergabe oder Plex bevorzugt
- die konfigurierte Audio-Whitelist für Direktwiedergabe
- den aktuellen Wiedergabekandidaten und die Video-ID
- aktuelle Metriken zum Scan-Fortschritt

Aktive Konfigurationswerte prüfen mit:

```bash
curl -s http://localhost:9245/api/config | python3 -m json.tool
```

Wenn die App unter `/movie/` bereitgestellt wird, den Pfad mit Präfix verwenden.

---

## Authentifizierungsmodell

Die App verwendet je nach Request-Typ unterschiedliche Transportmethoden:

- API-Requests verwenden den Header `X-Device-Id`
- HLS- und Plex-Proxy-Requests verwenden den Header `X-Device-Id`
- native direkte Medien-Requests nutzen als Fallback das Cookie `movies_device_id`

Diese Aufteilung existiert, weil native `<video src="...">`-Requests keine beliebigen benutzerdefinierten Header mitsenden können.

---

## Reverse-Proxy- Und Kontextpfad-Unterstützung

Die App unterstützt Deployments unter Unterpfaden wie:

- `https://example.com/movie/`
- `https://example.com/cinema/`

Das Routing behält das aktive Mount-Präfix bei für:

- direkte Medien
- lokales HLS
- Plex-HLS-Proxy-Requests
- Poster- und Untertitel-Assets

---

## Remote-Plex-Zugriff Mit Tailscale

Wenn die benutzerdefinierte UI remote erreichbar ist, Plex aber nur in einem privaten LAN erreichbar ist, muss der Host des movies server den Plex-Backend-Server trotzdem direkt erreichen können.

### Derselbe Host

```json
"plex": {
  "base_url": "http://127.0.0.1:32400"
}
```

### Plex Auf Einem Anderen LAN-Rechner

Die Route von einem Tailscale-Knoten aus bewerben, der Plex erreichen kann:

```bash
sudo tailscale up --advertise-routes=192.168.50.0/24
```

Dann die Erreichbarkeit vom movies-server-Host prüfen:

```bash
curl http://192.168.50.10:32400/identity
```

Hinweise:

- der Browser benötigt keinen direkten Netzwerkzugriff auf Plex
- der movies-server-Prozess muss `plex.base_url` erreichen können
- Reverse-Proxy- oder MagicDNS-Namen für die UI machen Plex nicht automatisch erreichbar

---

## Caching-Strategie

### Bild-Caching

Thumbnails, Preview-Frames und Plex-Posterbilder werden mit langlebigen unveränderlichen Cache-Headern ausgeliefert.

### Metadaten-Caching

Galerie-Metadaten-Snapshots werden in IndexedDB mit begrenztem Speicher gecacht:

- 1 Tag TTL
- bis zu 8 Snapshot-Einträge
- bis zu etwa 18 MB geschätzte Gesamtgröße
- ältere Einträge werden entfernt, wenn Limits überschritten werden

Jeder gecachte Snapshot speichert:

- `catalogStatus` des Servers
- Ordnerlisten-Cache
- geladene `videos`
- Paginierungszähler wie `serverTotal`, `serverOffset` und `serverExhausted`

Die Bereinigung ist opportunistisch statt geplant:

- abgelaufene Einträge werden beim Lesen oder späteren Pruning entfernt
- Pruning läuft nach dem Speichern frischer Snapshots
- Browser-Speicherdruck oder manuelles Löschen von Seitendaten kann IndexedDB-Daten ebenfalls entfernen

---

## Scan-Verhalten

Der Katalog-Scan ist so ausgelegt, dass die Kosten inkrementell bleiben, obwohl jede konfigurierte Wurzel weiterhin durchlaufen wird.

Aktuelles Verhalten:

- unveränderte Dateien verwenden gecachte `mtime + size`-Signaturen wieder
- periodische Scans sortieren vor der Verarbeitung nicht mehr die vollständige Pfadliste
- gelöschte Dateien werden aus dem In-Memory-Katalog und dem persistierten Index entfernt
- gelöschte Dateien lösen außerdem die Bereinigung erzeugter Thumbnail- und Preview-Artefakte aus
- Index-Speicherungen verwenden gecachte Dateisignaturdaten wieder, statt jede Datei erneut zu statten

Was der Scan weiterhin tut:

- er durchläuft konfigurierte Medienwurzeln, um hinzugefügte, geänderte und gelöschte Dateien zu erkennen
- er stellt Preview-Generierung in die Queue, wenn Preview-Bilder fehlen

Was er nicht tut:

- er berechnet bei periodischen Scans keine Prüfsummen großer Mediendateien
- er regeneriert bei unveränderten Dateien weder Thumbnails noch Metadaten, außer wenn Cache-Artefakte fehlen

### Vollständigen Rescan Erzwingen

Verwende:

```text
/rescan?full=1
```

Das ist nützlich, wenn:

- jemand den Thumbnail- oder Preview-Cache-Ordner manuell gelöscht hat
- du vermutest, dass das gespeicherte Scan-Manifest veraltet ist
- du eine vollständige Revalidierung scan-abgeleiteter Zustände erzwingen willst

### Scan-Status Prüfen

```bash
curl -s http://localhost:9245/api/status | python3 -m json.tool
```

Wenn die App unter `/movie/` bereitgestellt wird, den Pfad mit Präfix verwenden.

### Rescan Auslösen

Normaler inkrementeller Rescan:

```bash
curl -s http://localhost:9245/rescan | python3 -m json.tool
```

Erzwungener vollständiger Rescan:

```bash
curl -s "http://localhost:9245/rescan?full=1" | python3 -m json.tool
```

### Rescan-UI

Der Button `Rescan` öffnet einen Aktionsdialog, statt sofort einen inkrementellen Scan zu starten.

Verfügbare Aktionen:

- `Rescan`: inkrementeller Scan für neue oder geänderte Dateien
- `Full Scan`: löscht den gespeicherten Scan-Zustand und erzwingt vollständige Metadaten-Revalidierung
- `Refresh Database`: löscht Browser-IndexedDB-Snapshots und lädt frische Katalogdaten neu

### Wiederherstellung Bei Fehlendem Mount

Wenn `mount_script` konfiguriert ist und eine Medienanfrage auf einen fehlenden Ordner trifft, wird der Server:

1. erkennen, dass der übergeordnete Ordner nicht existiert
2. das konfigurierte Mount-Skript einmal aufrufen
3. den Zielpfad erneut prüfen
4. nur dann `Media folder is not mounted` mit HTTP 404 zurückgeben, wenn der Ordner weiterhin nicht verfügbar ist

Das Frontend behandelt Wiedergabe-404s als endgültig für diesen Versuch und zeigt eine Retry-Nachricht, statt den Server wiederholt zu bombardieren.

---

## Hinweise Zur Frontend-Entwicklung

Die App lädt derzeit `movies.js` direkt aus `index.html`, daher wirken Frontend-Änderungen ohne Neubau von `movies.min.js`.

---

## Privatmodus

- private Ordner sind verborgen, solange das Gerät nicht autorisiert ist
- der Entsperrstatus ist an eine Geräte-ID gebunden
- genehmigte Geräte werden serverseitig gespeichert
- `passcode.py` kann den Privatmodus-Passcode rotieren und Genehmigungen löschen

Beispiel:

```bash
python3 passcode.py mynewpasscode
```

---

## Generierte Dateien

Diese Dateien werden zur Laufzeit erzeugt und sollten nicht committed werden:

- `movies_config.json`
- `movies_state.json`
- `movies_auth_state.json`
- `movies_catalog_index.json`
- `cache/`

---

## Fehlerbehebung

### UI-Änderungen Erscheinen Nicht

- Seite zuerst normal aktualisieren
- wenn sich das JS-Bundle geändert hat, prüfen, ob `index.html` die erwartete Bundle-Version referenziert

### Direkte Private Wiedergabe Schlägt Fehl

- Privatmodus erneut entsperren, damit das Cookie `movies_device_id` aktualisiert wird

### Plex-Wiedergabe Schlägt Fehl, Direkte Wiedergabe Funktioniert Aber

- prüfen, ob der movies-server-Host `plex.base_url` erreichen kann
- prüfen, ob Plex in der Konfiguration aktiviert ist
- prüfen, ob das konfigurierte Token gültig ist

### Direkte Wiedergabe Schlägt Fehl, Plex Funktioniert Aber

- Container oder Codec sind für native Browser-Wiedergabe auf diesem Gerät wahrscheinlich nicht sicher
- Plex für diese Dateien aktiviert lassen oder den Kompatibilitätspfad über lokales Transcoding oder Plex erzwingen

### Lokales Transcoding Funktioniert Nicht

- prüfen, ob `ffmpeg` und `ffprobe` installiert sind
- prüfen, ob `on_demand_transcode` aktiviert ist
- prüfen, ob die Quelldatei zu den aktuell unterstützten Containern gehört: `.mkv` oder `.ts`

---

## Lizenz

Dieses Repository deklariert derzeit keine Softwarelizenz. Füge explizit eine hinzu, wenn du es weiterverteilen willst.
