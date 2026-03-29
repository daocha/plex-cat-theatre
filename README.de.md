<div align="center">
  <img width="700" alt="7844F597-CBA9-4EAD-80DE-19991552F906" src="https://github.com/user-attachments/assets/2f1fc4cf-8b63-47d0-aebf-53355dd8f032" />

  <h1>Cat Theatre Movies Server 🐱</h1>
  <p>
    <a href="https://github.com/daocha/plex-cat-theatre/blob/main/README.md">English</a> |
    <a href="https://github.com/daocha/plex-cat-theatre/blob/main/README.de.md">Deutsch</a> |
    <a href="https://github.com/daocha/plex-cat-theatre/blob/main/README.fr.md">Français</a> |
    <a href="https://github.com/daocha/plex-cat-theatre/blob/main/README.ja.md">日本語</a> |
    <a href="https://github.com/daocha/plex-cat-theatre/blob/main/README.ko.md">한국어</a> |
    <a href="https://github.com/daocha/plex-cat-theatre/blob/main/README.nl.md">Nederlands</a> |
    <a href="https://github.com/daocha/plex-cat-theatre/blob/main/README.th.md">ไทย</a> |
    <a href="https://github.com/daocha/plex-cat-theatre/blob/main/README.vi.md">Tiếng Việt</a> |
    <a href="https://github.com/daocha/plex-cat-theatre/blob/main/README.zh-CN.md">简体中文</a> |
    <a href="https://github.com/daocha/plex-cat-theatre/blob/main/README.zh-HK.md">繁體中文（香港）</a> |
    <a href="https://github.com/daocha/plex-cat-theatre/blob/main/README.zh-TW.md">繁體中文（台灣）</a>
  </p>
  <p><strong>Superleicht, Privatmodus 🔐, geräteübergreifend, smartes Streaming</strong></p>
  <p>Keine App erforderlich. Einfache Server-Installation. Mobilfreundliche Oberfläche, die dein NAS überall erreichbar macht, mit optionaler Plex-Integration</p>
  <p>
    <img src="https://img.shields.io/badge/stability-experimental-orange.svg" alt="Experimental" />
    <a href="https://opensource.org/licenses/MIT">
      <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="MIT License" />
    </a>
    <a href="http://github.com/daocha/plex-cat-theatre/releases/latest">
      <img src="https://img.shields.io/github/v/release/daocha/plex-cat-theatre?label=Latest&color=green" alt="Latest Release" />
    </a>
    <img src="https://img.shields.io/badge/python-3.9+-blue" alt="Python 3.9+" />
  </p>
</div>



> Keine schweren Abhängigkeiten, alles transparent. Leichtgewichtiger selbst gehosteter Film-Browser und Streaming-Server auf Basis von Flask, Waitress und `ffmpeg`, mit optionaler _`Plex`_-Integration für einen auf Kompatibilität ausgelegten Wiedergabepfad.

---

![Screenshot 2026-03-22 at 9 39 12 PM](https://github.com/user-attachments/assets/124f21b7-71b0-46fc-9d76-c73f700c25f3)

---

## ✨ Warum nutzen?

Cat Theatre ist absichtlich leichtgewichtig:

- 🩷 Für den _Remote-Zugriff_ ist kein Plex-Abo 💰 erforderlich
- ✅ Kleine Python-Abhängigkeitsfläche
- ✅ Keine Datenbank erforderlich
- ✅ Dateisystemzentrierte Katalogisierung
- ✅ Kompatibel mit 🖥️ Desktop, 📱 Mobilgeräten und Tablets
- ✅ Portabler polling-basierter Scan-Ablauf statt Abhängigkeit von OS-spezifischen Watchern
- 🔶 Optionale Plex-Integration als zusätzliche Schicht statt Pflicht für die Kernwiedergabe

## ✴️ Funktionen

- 🎬 Lokale / NAS-Mediatheken über mehrere Ordner verteilt
- 🌄 Generierung von Thumbnails / Postern und Preview-Frames
- 🔐 Private Ordner mit gerätebasierter Entsperrung
- 🔗 Reverse-Proxy-Betrieb unter einem Pfadpräfix wie `http://192.168.1.100/movie/`
- 📽️ Gemischte Wiedergabestrategien: direkte Wiedergabe, integriertes lokales Transcoding für `.mkv` und `.ts` oder Plex-gestütztes HLS-Proxying. Einfach pro Medium umschaltbar
- 🌐 Browser-Bildcache plus IndexedDB-Metadatencache

---
→ Einrichtung per Einzeiler:
```
curl -fsSL https://raw.githubusercontent.com/daocha/plex-cat-theatre/main/install.sh | bash
```
---

## 🟢 Voraussetzungen

### Python 3.9 oder neuer

Aktuelle Python-Pakete:

- `Flask`
- `waitress`

### System-Binaries für Metadatenanalyse, Vorschauen, Thumbnails und lokales Transcoding:

- `ffmpeg`
- `ffprobe`

Prüfe, ob sie verfügbar sind:

```bash
which ffmpeg
which ffprobe
```

---

## 🚀 Schnellstart


### → Option A: Einrichtung per Einzeiler:
```
curl -fsSL https://raw.githubusercontent.com/daocha/plex-cat-theatre/main/install.sh | bash
```

### → Option B: Installation aus PyPI mit pip

```bash
pip install plex-cat-theatre
plex-cat-theatre-init
plex-cat-theatre --config ~/movies_config.json
```

### → Option C: Bevorzugte Startmethode

```bash
git clone https://github.com/daocha/plex-cat-theatre
cd plex-cat-theatre
./startup.sh
```

Dieses Bootstrap-Skript kann:

- beim ersten Start `movies_config.json` aus der Beispielkonfiguration erstellen
- ein lokales `.venv` anlegen
- Python-Abhängigkeiten in diese lokale virtuelle Umgebung installieren
- bei Bedarf config-relative Ordner `cache/thumbnails` und `logs` erstellen
- `ffmpeg` und `ffprobe` prüfen
- optional dabei helfen, den Hash für den Private-Mode-Passcode zu erzeugen
- den Server mit deiner lokalen Konfiguration starten

Du kannst weiterhin den manuellen Ablauf unten verwenden:

1. Kopiere die Beispielkonfiguration:

```bash
cp movies_config.sample.json movies_config.json
```

2. Passe `movies_config.json` an deine Umgebung an.

### 🌐 Server starten:

```bash
# wenn du Option A oder Option B verwendest, dann ausführen
plex-cat-theatre --config ~/movies_config.json

# wenn du Option C verwendest, dann ausführen
python3 movies_server.py --config movies_config.json
```

Öffne die Oberfläche:

```text
http://localhost:9245
```
### 🔑 Passcode ändern
```bash
# wenn du Option A oder Option B verwendest, dann ausführen
plex-cat-theatre-passcode newpasscode

# wenn du Option C verwendest, dann ausführen
python3 passcode.py newpasscode
```
- private Ordner bleiben verborgen, bis das Gerät autorisiert ist
- der Entsperrstatus ist an eine Geräte-ID gebunden
- autorisierte Geräte werden serverseitig gespeichert
- das Skript kann den Private-Mode-Passcode rotieren und Freigaben zurücksetzen

---

## 🗂️ Projektstruktur

- `movies_server.py`: Flask-Einstiegspunkt und Routenverkabelung
- `movies_server_core.py`: gemeinsame Server-Helfer für Auth, Konfiguration, Cookies und Mount-Pfad-Behandlung
- `movies_catalog.py`: Katalog-Scan, Thumbnail-Generierung, Untertitel-Extraktion und lokale Transcode-Helfer
- `movies_server_plex.py`: Plex-Adapter, Poster-/Untertitel-Zuordnung und Plex-HLS-Proxying
- `movies.js`: Frontend-Quellcode
- `movies.min.js`: minifiziertes Frontend-Bundle
- `movies.css`: Galerie- und Player-Stile
- `passcode.py`: Helfer zum Rotieren des Private-Mode-Passcodes

---

## ⚙️ Konfiguration

Die Beispielkonfiguration ist absichtlich bereinigt und enthält nicht:

- echte Dateisystempfade
- echte Plex-Tokens
- echte gehashte Passcodes
- gerätespezifische Werte

### 📍 Wichtige Felder

<table>
  <tr>
    <td width="200"><code>root</code></td>
    <td>zu scannende Medienwurzeln (mehrere Ordner werden unterstützt)</td>
  </tr>
  <tr>
    <td><code>thumbs_dir</code></td>
    <td>Verzeichnis für Thumbnails und Preview-Frames. Standard: <code>./cache/thumbnails</code></td>
  </tr>
  <tr>
    <td><code>private_folder</code></td>
    <td>Ordnerpräfixe, die als privat behandelt werden. Beispiel: <code>Personal</code>. Alles unter dem Ordner <code>Personal</code> bleibt gesperrt, bis du es in der Oberfläche entsperrst.</td>
  </tr>
  <tr>
    <td><code>private_passcode</code></td>
    <td>Passcode-Hash für den privaten Modus. Diesen Wert solltest du nicht direkt im Klartext ändern. Wenn du ihn aktualisieren willst, siehe Abschnitt <code>Passcode ändern</code>.</td>
  </tr>
  <tr>
    <td><code>mount_script</code></td>
    <td>[optional] Befehl, der ausgeführt wird, wenn bei der Wiedergabe ein fehlender Medienordner wegen eines versehentlich ausgehängten Mounts erkannt wird.</td>
  </tr>
  <tr>
    <td><code>transcode</code></td>
    <td>Aktiviert den katalogseitigen Hintergrund-Transcode-Worker für Quellcontainer wie `.mkv` und `.ts`; dabei können separate transkodierte Sidecar-Dateien neben der Quellbibliothek erzeugt werden. Daher sollte dies meist auf <code>false</code> bleiben, besonders wenn Plex-Integration aktiviert ist. Standard: <code>false</code></td>
  </tr>
  <tr>
    <td><code>auto_scan_on_start</code></td>
    <td>Medien beim Start neu scannen. Standard: <code>false</code></td>
  </tr>
  <tr>
    <td><code>on_demand_transcode</code></td>
    <td>Aktiviert Laufzeit-Transcoding im Player für Quellcontainer, nutzt wenn möglich Hardware-Encoding und fällt sonst auf Software-Encoding zurück. Standard: <code>true</code></td>
  </tr>
  <tr>
    <td><code>on_demand_hls</code></td>
    <td>Aktiviert integrierte HLS-Playlists für Quellcontainer. Standard: <code>true</code></td>
  </tr>
  <tr>
  <td><code>enable_plex_server</code></td>
  <td>📍 [optional] Aktiviert die Plex-Integration. Standard: <code>false</code>. Stelle bitte sicher, dass dein Plex-Server bereits korrekt installiert und konfiguriert ist, bevor du dies einschaltest.<br> Dieser Server unterstützt native Untertitel, aber wenn du Untertitel automatisch abrufen möchtest, ist Plex dafür meist die bessere Wahl.
  <br> Für ein besseres On-Demand-Transcoding-Erlebnis wird dringend empfohlen, einen Plex-Server zu installieren, um nahtloses Medien-Streaming zu ermöglichen.<br>
  Auch ohne Plex-Server funktioniert dieser Server weiterhin gut, beachte aber Folgendes:
  <br>→ Bei Medien, die dein Gerät direkt abspielen kann, funktioniert das Springen im Video problemlos.
  <br>→ Bei Medien, die dein Gerät nicht direkt abspielen kann, z. B. <code>h.265 mit DTS-Audio</code> (h.265 mit AAC oder MP3 ist nicht betroffen), <code>.mkv</code>, <code>.ts</code> oder <code>.wmv</code>, kann dieser Server weiterhin on-the-fly transkodieren, aber die Suchfunktion ist eventuell nicht verfügbar.
  </td>
  </tr>
  <tr>
    <td><code>plex.base_url</code></td>
    <td>Basis-URL des Plex-Servers.</td>
  </tr>
  <tr>
    <td><code>plex.token</code></td>
    <td>Plex-Token</td>
  </tr>
  <tr>
    <td><code>debug_enabled</code></td>
    <td>Zeigt das integrierte Debug-Overlay an</td>
  </tr>
  <tr>
    <td><code>direct_playback</code></td>
    <td>Objekt mit <code>enabled</code> und <code>audio_whitelist</code>. Mit <code>enabled=true</code> kann das Medium ohne Transcoding mit dem nativen Player abgespielt werden (schnell). Die Standardeinstellungen werden empfohlen.</td>
  </tr>
</table>

### Minimales Beispiel nur lokal

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

### Beispiel mit Plex-Integration

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

### 🅿️ Plex-Scanverhalten

- lokale Poster-Thumbnail-Generierung wird übersprungen, wenn Plex-Poster verfügbar sind
- vorhandene lokal gecachte Thumbnails können weiterhin wiederverwendet werden
- Preview-Frame-Generierung bleibt aktiviert
- Plex-Integration bleibt optional und der rein lokale Modus funktioniert weiterhin

### → So erhältst du ein Plex-Token

#### Methode 1: Vorhandene Plex-Web-Sitzung

1. Öffne Plex Web und melde dich an.
2. Öffne die Entwicklerwerkzeuge deines Browsers.
3. Wechsle zum Tab Netzwerk.
4. Lade die Seite neu.
5. Untersuche eine Anfrage, die an deinen Plex-Server gesendet wird.
6. Suche `X-Plex-Token` in der URL oder in den Headern.

#### Methode 2: Browser-Speicher

Prüfe:

- lokaler Speicher (`Local Storage`)
- Sitzungsspeicher (`Session Storage`)
- Anfrage-URLs und Header in den DevTools

#### Methode 3: Direkte lokale Anfrage

Wenn du auf demselben Rechner bereits eine aktive Plex-Web-Sitzung hast, untersuche Plex-Anfragen in den DevTools und suche nach:

```text
X-Plex-Token=...
```

‼️ Sicherheitshinweise:

- behandle das Plex-Token wie ein Passwort
- committe es nicht in git
- speichere es nur in `movies_config.json`

---

## 🎥 Wiedergabemodi

### 1. Native direkte Wiedergabe

Wird für browserfreundliche Dateien wie `.mp4`, `.m4v` und `.webm` verwendet.

Verhalten:

- liefert die lokale Datei direkt über `/video/<id>` aus
- unterstützt HTTP-Range-Requests
- vermeidet Transcoding-Overhead, wenn der Browser die Datei nativ abspielen kann

Am besten geeignet für:

- Dateien im Stil von MP4/H.264
- Browser, die die Datei bereits direkt unterstützen
- Dateien, deren Audio-Codecs der Direct-Play-Whitelist entsprechen

### 2. Integriertes lokales Transcoding ohne Plex

Dies ist der Fallback-Pfad, wenn Plex nicht aktiviert ist oder du bewusst vollständig lokal bleiben willst.

Aktuelle Implementierung:

- `.mkv` und `.ts` können als lokales HLS unter `/hls/<id>/index.m3u8` bereitgestellt werden
- dieselben Dateien können auch als fragmentiertes MP4 über `/video/<id>?fmp4=1` gestreamt werden
- HLS-Segmente werden bei Bedarf mit `ffmpeg` erzeugt
- Hardware-Encoding wird zuerst versucht und fällt bei Bedarf auf `libx264` zurück
- fMP4-Ausgabe wird mit `libx264` plus AAC erzeugt

### 3. Plex-gestützte Wiedergabe

Wenn die Plex-Integration aktiviert ist:

- kann das Frontend `plex_stream_url` für kompatibilitätssensible Wiedergabe verwenden
- erzeugt Plex die vorgelagerte HLS-Playlist
- schreibt dieser Server die Playlist um und proxyt verschachtelte Playlist- und Segment-Anfragen
- spricht der Browser weiterhin mit dieser App und nicht direkt mit Plex

Am besten geeignet für:

- MKV- oder TS-Inhalte auf Geräten mit schwächerer Codec- oder Container-Unterstützung
- Fälle, in denen Plex-Untertitelauswahl oder Stream-Normalisierung bevorzugt werden

### Richtlinie zur Wiedergabeauswahl

- direkte Wiedergabe gewinnt für browserfreundliche Dateien, deren Audio-Codecs zu `direct_playback.audio_whitelist` passen
- Plex bleibt bevorzugt für `.mkv`, `.ts`, HLS, fMP4 oder nicht unterstützte Audio-Codecs
- das Timing des iOS-nativen HLS-Fallbacks ist länger, damit der Plex-Stream Zeit zum Aufwärmen hat

### Standardlogik für Wiedergabe

- `Direct` wird für `.mp4`, `.m4v`, `.webm` und `.avi` bevorzugt, wenn die direkte URL ein echter Dateipfad ist und die Audio-Codecs whitelist-sicher sind
- wenn Audio-Codec-Metadaten für eine dieser browserfreundlichen Erweiterungen fehlen, bevorzugt die App trotzdem `Direct`
- `Plex` wird bevorzugt für `.mkv`, `.ts`, HLS-/fMP4-Direkt-URLs und Dateien, deren bekannte Audio-Codecs außerhalb der Whitelist liegen
- wenn kein Plex-Treffer existiert, fällt die App auf `Direct` zurück

---

## Authentifizierungsmodell

Die App verwendet je nach Anfrageart unterschiedliche Transportmethoden:

- API-Anfragen nutzen den Header `X-Device-Id`
- HLS- und Plex-Proxy-Anfragen nutzen den Header `X-Device-Id`
- native direkte Medienanfragen nutzen den Cookie-Fallback `movies_device_id`

Diese Aufteilung existiert, weil native `<video src="...">`-Anfragen keine beliebigen benutzerdefinierten Header anhängen können.

---

## Reverse-Proxy- und Kontextpfad-Unterstützung

Die App unterstützt Deployments unter Unterpfaden wie:

- `https://example.com/movie/`
- `https://example.com/cinema/`

Das Routing bewahrt das aktive Mount-Präfix für:

- direkte Medien
- lokales HLS
- Plex-HLS-Proxy-Anfragen
- Poster- und Untertitel-Assets

---

## Remote-Plex-Zugriff mit Tailscale

Wenn die benutzerdefinierte UI remote erreichbar ist, Plex aber nur in einem privaten LAN erreichbar ist, muss der Host des Movie-Servers das Plex-Backend trotzdem direkt erreichen können.

### Derselbe Host

```json
"plex": {
  "base_url": "http://127.0.0.1:32400"
}
```

### Plex auf einem anderen LAN-Rechner

Kündige die Route von einem Tailscale-Knoten an, der Plex erreichen kann:

```bash
sudo tailscale up --advertise-routes=192.168.50.0/24
```

Prüfe dann die Erreichbarkeit vom Host des Movie-Servers:

```bash
curl http://192.168.50.10:32400/identity
```

📌 Hinweise:

- der Browser benötigt keinen direkten Netzwerkzugriff auf Plex
- der Movie-Server-Prozess muss `plex.base_url` erreichen können
- Reverse-Proxy- oder MagicDNS-Namen für die UI machen Plex nicht automatisch erreichbar

---

## 💾 Caching-Strategie

### Bild-Caching

Thumbnails, Preview-Frames und Plex-Posterbilder werden mit langlebigen unveränderlichen Cache-Headern ausgeliefert.

### Metadaten-Caching

Galerie-Metadaten-Snapshots werden in IndexedDB mit begrenztem Speicher gecacht:

- TTL von 1 Tag
- bis zu 8 Snapshot-Datensätze
- insgesamt geschätzt bis zu etwa 18 MB
- ältere Einträge werden entfernt, wenn Grenzen überschritten werden

Jeder gecachte Snapshot speichert:

- serverseitigen `catalogStatus`
- Ordnerlisten-Cache
- geladene `videos`
- Paginierungszähler wie `serverTotal`, `serverOffset` und `serverExhausted`

Das Entfernen erfolgt opportunistisch statt geplant:

- abgelaufene Einträge werden beim Lesen oder späteren Bereinigen entfernt
- Bereinigung läuft, nachdem frische Snapshots gespeichert wurden
- Browser-Speicherdruck oder manuelles Löschen von Website-Daten kann IndexedDB-Daten ebenfalls entfernen

---

## 🔍 Scanverhalten

Der Katalog-Scan ist so ausgelegt, dass die Kosten inkrementell bleiben, auch wenn weiterhin jede konfigurierte Wurzel durchlaufen wird.

Aktuelles Verhalten:

- unveränderte Dateien verwenden gecachte Signaturen aus `mtime + size`
- periodische Scans sortieren die vollständige Pfadliste vor der Verarbeitung nicht mehr
- gelöschte Dateien werden aus dem In-Memory-Katalog und dem persistierten Index entfernt
- gelöschte Dateien lösen außerdem das Aufräumen erzeugter Thumbnail- und Preview-Artefakte aus
- beim Speichern des Index werden gecachte Dateisignaturen wiederverwendet, statt jede Datei erneut zu statten

Was der Scan weiterhin tut:

- konfigurierte Medienwurzeln durchlaufen, um neue, geänderte und gelöschte Dateien zu erkennen
- Preview-Generierung einreihen, wenn Vorschaubilder fehlen

Was er nicht tut:

- er berechnet bei periodischen Scans keine Checksummen großer Mediendateien
- er erzeugt Thumbnails oder Metadaten für unveränderte Dateien nicht neu, solange gecachte Artefakte vorhanden sind

### → Rescan auslösen

Normaler inkrementeller Rescan:

```bash
curl -s http://localhost:9245/rescan | python3 -m json.tool
```

Erzwungener vollständiger Rescan:

```bash
curl -s "http://localhost:9245/rescan?full=1" | python3 -m json.tool
```

### → Oberfläche für Rescan

Die Schaltfläche `Rescan` öffnet einen Aktionsdialog, statt sofort einen inkrementellen Scan zu starten.

Verfügbare Aktionen:

- `Rescan`: inkrementeller Scan nach neuen oder geänderten Dateien
- `Full Scan`: löscht den gespeicherten Scan-Zustand und erzwingt eine vollständige Metadaten-Neuvalidierung
- `Refresh Database`: löscht Browser-IndexedDB-Snapshots und lädt frische Katalogdaten neu

### ⛓️‍💥 Wiederherstellung bei fehlendem Mount

Diese Funktion ist für Fälle gedacht, in denen ein NAS mit Auto-Sleep konfiguriert ist und ein SMB-Mount vom Betriebssystem automatisch ausgehängt wird.

Wenn `mount_script` konfiguriert ist und eine Medienanfrage auf einen fehlenden Ordner trifft, wird der Server:

1. erkennen, dass der übergeordnete Ordner nicht existiert
2. das konfigurierte Mount-Skript einmal aufrufen
3. den Zielpfad erneut prüfen
4. nur dann `Media folder is not mounted` mit HTTP 404 zurückgeben, wenn der Ordner weiterhin nicht verfügbar ist

Das Frontend behandelt Wiedergabe-404s für diesen Versuch als endgültig und zeigt eine Retry-Meldung, statt den Server wiederholt zu bombardieren.

---

## 📄 Erzeugte Dateien

Diese Dateien werden zur Laufzeit erzeugt und sollten nicht committed werden:

- `movies_config.json`
- `movies_state.json`
- `movies_auth_state.json`
- `movies_catalog_index.json`
- `cache/`

---

## 🛠️ Fehlerbehebung


### → Debug-Overlay

Aktiviere `debug_enabled` in `movies_config.json`, um unten rechts dauerhaft ein Debug-Overlay anzuzeigen.

Das Panel meldet:

- ob der Server direkte Wiedergabe oder Plex bevorzugt
- die konfigurierte Audio-Whitelist für Direct Play
- den aktuellen Wiedergabekandidaten und die Video-ID
- aktuelle Kennzahlen zum Scan-Fortschritt

Prüfe aktive Konfigurationswerte mit:

```bash
curl -s http://localhost:9245/api/config | python3 -m json.tool
```

### → Änderungen an der Oberfläche erscheinen nicht

- Die App lädt `movies.js` derzeit direkt aus `index.html`, daher werden Frontend-Änderungen wirksam, ohne `movies.min.js` neu zu bauen.
- aktualisiere die Seite zunächst normal
- wenn sich das JS-Bundle geändert hat, prüfe, ob `index.html` auf die erwartete Bundle-Version verweist

### → Direkte private Wiedergabe schlägt fehl

- entsperre den privaten Modus erneut, damit das Cookie `movies_device_id` aktualisiert wird

### → Plex-Wiedergabe schlägt fehl, direkte Wiedergabe funktioniert aber

- prüfe, ob der Host des Movie-Servers `plex.base_url` erreichen kann
- prüfe, ob Plex in der Konfiguration aktiviert ist
- prüfe, ob das konfigurierte Token gültig ist

### → Direkte Wiedergabe schlägt fehl, Plex funktioniert aber

- der Container oder Codec ist auf diesem Gerät wahrscheinlich nicht sicher für native Browser-Wiedergabe
- lasse Plex für diese Dateien aktiviert oder erzwinge den Kompatibilitätspfad über lokales Transcoding oder Plex

### → Lokales Transcoding funktioniert nicht

- prüfe, ob `ffmpeg` und `ffprobe` installiert sind
- prüfe, ob `on_demand_transcode` aktiviert ist
- prüfe, ob die Quelldatei zu den aktuell unterstützten Containern gehört: `.mkv` oder `.ts`

---

## 📦 Release-Versionierung

Paketversionen werden aus Git-Tags abgeleitet.

- TestPyPI/Testing: verwende eine Entwicklungsversion wie `2026.3.26.dev1`
- PyPI-Prerelease: verwende einen Release Candidate wie `2026.3.26rc1`
- PyPI-Stable: verwende eine stabile Version wie `2026.3.26`
- Git-Tags sollten `v2026.3.26.dev1`, `v2026.3.26rc1` und `v2026.3.26` sein
  
---

## ©️ Lizenz

Dieses Projekt wird unter der MIT-Lizenz veröffentlicht. Füge beim Publizieren oder Weiterverteilen eine `LICENSE`-Datei mit dem MIT-Text hinzu.
