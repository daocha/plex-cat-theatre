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
  <p><strong>Superlicht, privémodus 🔐, apparaatoverschrijdend, slim streamen</strong></p>
  <p>Geen app vereist. Eenvoudige serverinstallatie. Mobielvriendelijke interface om je NAS overal te bereiken, met optionele Plex-integratie</p>
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



> Geen zware afhankelijkheden, alles transparant. Lichtgewicht zelfgehoste filmbrowser en streamingserver gebouwd met Flask, Waitress en `ffmpeg`, met optionele _`Plex`_-integratie voor compatibiliteitsgerichte weergave.

---

![Screenshot 2026-03-22 at 9 39 12 PM](https://github.com/user-attachments/assets/124f21b7-71b0-46fc-9d76-c73f700c25f3)

---

## ✨ Waarom gebruiken

Cat Theatre is bewust lichtgewicht:

- 🩷 Voor _toegang op afstand_ is geen Plex-abonnement 💰 nodig
- ✅ Klein Python-afhankelijkheidsoppervlak
- ✅ Geen database nodig
- ✅ Catalogisering met het bestandssysteem als uitgangspunt
- ✅ Compatibel met 🖥️ desktop, 📱 mobiel en tablet
- ✅ Draagbare polling-gebaseerde scanstroom in plaats van afhankelijkheid van OS-specifieke watchers
- 🔶 Optionele Plex-integratie als extra laag in plaats van vereiste voor kernweergave

## ✴️ Functies

- 🎬 Lokale / NAS-mediabibliotheken verspreid over meerdere mappen
- 🌄 Generatie van thumbnails / posters en previewframes
- 🔐 Privémappen met apparaatgebaseerde ontgrendeling
- 🔗 Reverse-proxy-deployment onder een padprefix zoals `http://192.168.1.100/movie/`
- 📽️ Gemengde afspeelstrategieën: direct afspelen, ingebouwde lokale transcoding voor `.mkv` en `.ts`, of door Plex ondersteunde HLS-proxying. Eenvoudig per medium te wisselen
- 🌐 Browserafbeeldingscache plus IndexedDB-metadatacache

---
→ Instellen met een one-liner:
```
curl -fsSL https://raw.githubusercontent.com/daocha/plex-cat-theatre/main/install.sh | bash
```
---

## 🟢 Vereisten

### Python 3.9 of nieuwer

Huidige Python-pakketten:

- `Flask`
- `waitress`

### Systeembinaries voor metadata-analyse, previews, thumbnails en lokale transcoding:

- `ffmpeg`
- `ffprobe`

Controleer of ze beschikbaar zijn:

```bash
which ffmpeg
which ffprobe
```

---

## 🚀 Snel starten


### → Optie A: instellen met een one-liner:
```
curl -fsSL https://raw.githubusercontent.com/daocha/plex-cat-theatre/main/install.sh | bash
```

### → Optie B: installeren vanaf PyPI met pip

```bash
pip install plex-cat-theatre
plex-cat-theatre-init
plex-cat-theatre --config ~/movies_config.json
```

### → Optie C: voorkeursmanier om te starten

```bash
git clone https://github.com/daocha/plex-cat-theatre
cd plex-cat-theatre
./startup.sh
```

Dit bootstrapscript kan:

- bij de eerste start `movies_config.json` maken vanuit de voorbeeldconfiguratie
- een lokale `.venv` aanmaken
- Python-afhankelijkheden in die lokale virtuele omgeving installeren
- indien nodig config-relatieve mappen `cache/thumbnails` en `logs` aanmaken
- `ffmpeg` en `ffprobe` controleren
- optioneel helpen bij het genereren van de hash voor de privémodus-passcode
- de server starten met je lokale configuratie

Je kunt ook nog steeds de handmatige flow hieronder gebruiken:

1. Kopieer de voorbeeldconfiguratie:

```bash
cp movies_config.sample.json movies_config.json
```

2. Bewerk `movies_config.json` voor jouw omgeving.

### 🌐 Start de server:

```bash
# als je optie A of optie B volgt, voer dan uit
plex-cat-theatre --config ~/movies_config.json

# als je optie C volgt, voer dan uit
python3 movies_server.py --config movies_config.json
```

Open de interface:

```text
http://localhost:9245
```
### 🔑 Passcode wijzigen
```bash
# als je optie A of optie B volgt, voer dan uit
plex-cat-theatre-passcode newpasscode

# als je optie C volgt, voer dan uit
python3 passcode.py newpasscode
```
- privémappen blijven verborgen totdat het apparaat is geautoriseerd
- de ontgrendelstatus is gekoppeld aan een apparaat-ID
- goedgekeurde apparaten worden server-side opgeslagen
- het script kan de privémodus-passcode roteren en goedkeuringen wissen

---

## 🗂️ Projectstructuur

- `movies_server.py`: Flask-entrypoint en route-wiring
- `movies_server_core.py`: gedeelde serverhelpers voor auth, configuratie, cookies en mount-padafhandeling
- `movies_catalog.py`: catalogusscan, thumbnailgeneratie, ondertitelextractie en lokale transcode-helpers
- `movies_server_plex.py`: Plex-adapter, poster-/ondertitelmapping en Plex-HLS-proxying
- `movies.js`: frontendbron
- `movies.min.js`: geminificeerde frontendbundle
- `movies.css`: galerij- en spelerstijlen
- `passcode.py`: helper voor het roteren van de privémodus-passcode

---

## ⚙️ Configuratie

De voorbeeldconfiguratie is bewust opgeschoond en bevat niet:

- echte bestandssysteempaden
- echte Plex-tokens
- echte gehashte passcodes
- apparaatspecifieke waarden

### 📍 Belangrijke velden

<table>
  <tr>
    <td width="200"><code>root</code></td>
    <td>mediaroots om te scannen (ondersteunt meerdere mappen)</td>
  </tr>
  <tr>
    <td><code>thumbs_dir</code></td>
    <td>map voor thumbnails en previewframes. Standaard: <code>./cache/thumbnails</code></td>
  </tr>
  <tr>
    <td><code>private_folder</code></td>
    <td>mapprefixen die als privé worden behandeld. Voorbeeld: <code>Personal</code>. Alles onder de map <code>Personal</code> blijft vergrendeld totdat je dit in de interface ontgrendelt.</td>
  </tr>
  <tr>
    <td><code>private_passcode</code></td>
    <td>hash van de privémodus-passcode. Werk dit niet direct bij met platte tekst. Als je het wilt aanpassen, zie de sectie <code>Passcode wijzigen</code>.</td>
  </tr>
  <tr>
    <td><code>mount_script</code></td>
    <td>[optioneel] Commando dat wordt gebruikt wanneer afspelen een ontbrekende mediamap raakt doordat een map onbedoeld is ontkoppeld.</td>
  </tr>
  <tr>
    <td><code>transcode</code></td>
    <td>Schakelt de achtergrond-transcodeworker aan cataloguskant in voor broncontainers zoals `.mkv` en `.ts`; dit kan aparte getranscode sidecar-mediabestanden naast de bronbibliotheek genereren, dus dit blijft meestal beter op <code>false</code>, vooral wanneer Plex-integratie is ingeschakeld. Standaard: <code>false</code></td>
  </tr>
  <tr>
    <td><code>auto_scan_on_start</code></td>
    <td>Media opnieuw scannen bij opstarten. Standaard: <code>false</code></td>
  </tr>
  <tr>
    <td><code>on_demand_transcode</code></td>
    <td>Schakelt runtime-transcoding in de speler in voor broncontainers, gebruikt hardware-encoding indien beschikbaar en valt terug op software-encoding wanneer nodig. Standaard: <code>true</code></td>
  </tr>
  <tr>
    <td><code>on_demand_hls</code></td>
    <td>Schakelt ingebouwde HLS-playlists in voor broncontainers. Standaard: <code>true</code></td>
  </tr>
  <tr>
  <td><code>enable_plex_server</code></td>
  <td>📍 [optioneel] Schakelt Plex-integratie in. Standaard: <code>false</code>. Zorg ervoor dat je Plex Server correct hebt geïnstalleerd en geconfigureerd voordat je dit inschakelt.<br> Deze server ondersteunt native ondertitels, maar als je automatisch ondertitels wilt ophalen, is Plex daar meestal beter voor.
  <br> Voor een betere on-demand-transcodingervaring wordt sterk aangeraden een Plex-server te installeren voor naadloos media streamen.<br>
  Ook zonder Plex-server werkt deze server nog steeds goed, maar let op het volgende:
  <br>→ Voor media die je apparaat direct kan afspelen werkt seeken perfect.
  <br>→ Voor media die je apparaat niet direct kan afspelen, zoals <code>h.265 met DTS-audio</code> (h.265 met AAC of MP3 wordt niet geraakt), <code>.mkv</code>, <code>.ts</code> of <code>.wmv</code>, kan deze server nog steeds on-the-fly transcoderen, maar seeken is mogelijk niet beschikbaar.
  </td>
  </tr>
  <tr>
    <td><code>plex.base_url</code></td>
    <td>Basis-URL van de Plex-server.</td>
  </tr>
  <tr>
    <td><code>plex.token</code></td>
    <td>Plex-token</td>
  </tr>
  <tr>
    <td><code>debug_enabled</code></td>
    <td>Toon de ingebouwde debug-overlay</td>
  </tr>
  <tr>
    <td><code>direct_playback</code></td>
    <td>Object met <code>enabled</code> en <code>audio_whitelist</code>. Met <code>enabled=true</code> kun je media met de native speler afspelen zonder transcoding (snel). Aanbevolen is om de standaardinstellingen te gebruiken.</td>
  </tr>
</table>

### Minimale lokaal-only voorbeeldconfiguratie

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

### Voorbeeld met Plex-integratie

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

### 🅿️ Plex-scangedrag

- lokale posterthumbnailgeneratie wordt overgeslagen wanneer Plex-posters beschikbaar zijn
- bestaande lokaal gecachte thumbnails kunnen nog steeds worden hergebruikt
- previewframegeneratie blijft ingeschakeld
- Plex-integratie blijft optioneel en de volledig lokale modus werkt nog steeds

### → Hoe je een Plex-token krijgt

#### Methode 1: bestaande Plex Web-sessie

1. Open Plex Web en log in.
2. Open de ontwikkelaarstools van je browser.
3. Ga naar het tabblad Netwerk.
4. Vernieuw de pagina.
5. Inspecteer een request die naar je Plex-server wordt gestuurd.
6. Zoek `X-Plex-Token` in de URL of headers.

#### Methode 2: browseropslag

Controleer:

- lokale opslag (`Local Storage`)
- sessieopslag (`Session Storage`)
- request-URL's en headers in DevTools

#### Methode 3: directe lokale request

Als je al een actieve Plex Web-sessie hebt op dezelfde machine, inspecteer dan Plex-requests in DevTools en zoek naar:

```text
X-Plex-Token=...
```

‼️ Beveiligingsnotities:

- behandel het Plex-token als een wachtwoord
- commit het niet naar git
- bewaar het alleen in `movies_config.json`

---

## 🎥 Afspeelmodi

### 1. Native directe weergave

Gebruikt voor browserveilige bestanden zoals `.mp4`, `.m4v` en `.webm`.

Gedrag:

- serveert het lokale bestand direct vanaf `/video/<id>`
- ondersteunt HTTP-range-requests
- voorkomt transcoding-overhead wanneer de browser het bestand native kan afspelen

Beste voor:

- MP4/H.264-achtige bestanden
- browsers die het bestand al direct ondersteunen
- bestanden waarvan de audiocodecs overeenkomen met de direct-play-whitelist

### 2. Ingebouwde lokale transcoding zonder Plex

Dit is het fallback-pad wanneer Plex niet is ingeschakeld, of wanneer je bewust volledig lokaal wilt blijven.

Huidige implementatie:

- `.mkv` en `.ts` kunnen als lokale HLS worden aangeboden via `/hls/<id>/index.m3u8`
- dezelfde bestanden kunnen ook als gefragmenteerde MP4 worden gestreamd via `/video/<id>?fmp4=1`
- HLS-segmenten worden on demand gegenereerd met `ffmpeg`
- hardware-encoding kan eerst worden geprobeerd en anders terugvallen op `libx264`
- fMP4-output wordt gegenereerd met `libx264` plus AAC

### 3. Plex-ondersteunde weergave

Wanneer Plex-integratie is ingeschakeld:

- kan de frontend `plex_stream_url` gebruiken voor compatibiliteitsgevoelige weergave
- genereert Plex de upstream HLS-playlist
- herschrijft deze server de playlist en proxyt geneste playlist- en segmentrequests
- praat de browser nog steeds met deze app, niet rechtstreeks met Plex

Beste voor:

- MKV- of TS-content op apparaten met zwakkere codec- of containerondersteuning
- situaties waarin Plex-ondertitelselectie of streamnormalisatie de voorkeur heeft

### Beleid voor afspeelselectie

- directe weergave wint voor browserveilige bestanden waarvan de audiocodecs overeenkomen met `direct_playback.audio_whitelist`
- Plex blijft de voorkeur houden voor `.mkv`, `.ts`, HLS, fMP4 of niet-ondersteunde audiocodecs
- de timing van de iOS-native HLS-fallback is langer zodat de Plex-stream tijd krijgt om op te warmen

### Standaard afspeellogica

- `Direct` heeft de voorkeur voor `.mp4`, `.m4v`, `.webm` en `.avi` wanneer de directe URL een echt bestandspad is en de audiocodecs whitelist-veilig zijn
- als audiocodecmetadata ontbreekt voor een van die browserveilige extensies, kiest de app nog steeds voor `Direct`
- `Plex` heeft de voorkeur voor `.mkv`, `.ts`, HLS-/fMP4-directe URL's en bestanden waarvan de bekende audiocodecs buiten de whitelist vallen
- als er geen Plex-match bestaat, valt de app terug op `Direct`

---

## Authenticatiemodel

De app gebruikt verschillende transportmethoden afhankelijk van het type request:

- API-requests gebruiken de header `X-Device-Id`
- HLS- en Plex-proxyrequests gebruiken de header `X-Device-Id`
- native directe mediarequests gebruiken de cookie-fallback `movies_device_id`

Deze splitsing bestaat omdat native `<video src="...">`-requests geen willekeurige aangepaste headers kunnen meesturen.

---

## Ondersteuning voor reverse proxy en contextpad

De app ondersteunt deployment onder subpaden zoals:

- `https://example.com/movie/`
- `https://example.com/cinema/`

Routing behoudt het actieve mountprefix voor:

- directe media
- lokale HLS
- Plex-HLS-proxyrequests
- poster- en ondertitel-assets

---

## Externe Plex-toegang met Tailscale

Als de aangepaste interface op afstand bereikbaar is maar Plex alleen bereikbaar is op een privaat LAN, moet de host van de movies-server de Plex-backend nog steeds direct kunnen bereiken.

### Dezelfde host

```json
"plex": {
  "base_url": "http://127.0.0.1:32400"
}
```

### Plex op een andere LAN-machine

Adverteer de route vanaf een Tailscale-node die Plex kan bereiken:

```bash
sudo tailscale up --advertise-routes=192.168.50.0/24
```

Controleer daarna de bereikbaarheid vanaf de host van de movies-server:

```bash
curl http://192.168.50.10:32400/identity
```

📌 Notities:

- de browser heeft geen directe netwerktoegang tot Plex nodig
- het movies-serverproces moet `plex.base_url` kunnen bereiken
- reverse-proxy- of MagicDNS-namen voor de interface maken Plex niet vanzelf bereikbaar

---

## 💾 Cachingstrategie

### Afbeeldingscache

Thumbnails, previewframes en Plex-posterafbeeldingen worden geserveerd met langlevende immutable cacheheaders.

### Metadatacache

Galerijmetadata-snapshots worden in IndexedDB gecachet met begrensde opslag:

- TTL van 1 dag
- maximaal 8 snapshotrecords
- tot ongeveer 18 MB geschatte totale grootte
- oudere items worden verwijderd wanneer limieten worden overschreden

Elke gecachte snapshot slaat op:

- server-`catalogStatus`
- cache van de maplijst
- geladen `videos`
- pagineringscounters zoals `serverTotal`, `serverOffset` en `serverExhausted`

Evictie is opportunistisch in plaats van gepland:

- verlopen items worden verwijderd bij lezen of latere opschoning
- opschoning draait nadat nieuwe snapshots zijn opgeslagen
- browseropslagdruk of handmatig wissen van sitedata kan IndexedDB-data ook verwijderen

---

## 🔍 Scangedrag

De catalogusscan is ontworpen om incrementeel in kosten te blijven, ook al loopt hij nog steeds door elke geconfigureerde root.

Huidig gedrag:

- ongewijzigde bestanden hergebruiken gecachte `mtime + size`-signaturen
- periodieke scans sorteren de volledige padlijst niet langer voordat ze verwerken
- verwijderde bestanden worden uit de in-memorycatalogus en de persistente index verwijderd
- verwijderde bestanden triggeren ook opruiming van gegenereerde thumbnail- en preview-artefacten
- index-opslag hergebruikt gecachte bestandssignatuurdata in plaats van opnieuw `stat` op elk bestand uit te voeren

Wat de scan nog steeds doet:

- geconfigureerde mediaroots doorlopen om toegevoegde, gewijzigde en verwijderde bestanden te detecteren
- previewgeneratie in de wachtrij zetten wanneer previewafbeeldingen ontbreken

Wat hij niet doet:

- hij checksumt geen grote mediabestanden tijdens periodieke scans
- hij regenereert geen thumbnails of metadata voor ongewijzigde bestanden zolang gecachte artefacten aanwezig zijn

### → Rescan triggeren

Normale incrementele rescan:

```bash
curl -s http://localhost:9245/rescan | python3 -m json.tool
```

Geforceerde volledige rescan:

```bash
curl -s "http://localhost:9245/rescan?full=1" | python3 -m json.tool
```

### → Rescan-interface

De knop `Rescan` opent een actiedialoog in plaats van meteen een incrementele scan te starten.

Beschikbare acties:

- `Rescan`: incrementele scan naar nieuwe of gewijzigde bestanden
- `Full Scan`: wist opgeslagen scanstatus en forceert volledige metadatavalidatie
- `Refresh Database`: wist browser-IndexedDB-snapshots en laadt verse catalogusdata opnieuw

### ⛓️‍💥 Herstel van ontbrekende mount

Deze functie is bedoeld voor het geval sommige NAS-systemen automatische slaapstand gebruiken, waardoor een SMB-mount door sommige besturingssystemen automatisch kan worden uitgeworpen.

Als `mount_script` is geconfigureerd en een mediarequest een ontbrekende map raakt, zal de server:

1. detecteren dat de bovenliggende map niet bestaat
2. het geconfigureerde mountscript eenmaal uitvoeren
3. het doelpad opnieuw controleren
4. alleen `Media folder is not mounted` met HTTP 404 teruggeven als de map nog steeds niet beschikbaar is

De frontend behandelt playback-404's als definitief voor die poging en toont een retry-bericht in plaats van de server herhaaldelijk te bestoken.

---

## 📄 Gegenereerde bestanden

Deze bestanden worden tijdens runtime gegenereerd en mogen niet worden gecommit:

- `movies_config.json`
- `movies_state.json`
- `movies_auth_state.json`
- `movies_catalog_index.json`
- `cache/`

---

## 🛠️ Probleemoplossing


### → Debug-overlay

Schakel `debug_enabled` in `movies_config.json` in om een permanente debug-overlay in de rechteronderhoek te tonen.

Het paneel meldt:

- of de server directe weergave of Plex prefereert
- de geconfigureerde audio-whitelist voor direct play
- de huidige afspeelkandidaat en video-ID
- recente scanvoortgangsmetingen

Inspecteer actieve configuratiewaarden met:

```bash
curl -s http://localhost:9245/api/config | python3 -m json.tool
```

### → Interfacewijzigingen verschijnen niet

- De app laadt momenteel `movies.js` direct vanuit `index.html`, dus frontendwijzigingen werken zonder `movies.min.js` opnieuw te bouwen.
- ververs de pagina eerst normaal
- als de JS-bundel is gewijzigd, controleer dan of `index.html` naar de verwachte bundelversie verwijst

### → Directe privéweergave faalt

- ontgrendel de privémodus opnieuw zodat de `movies_device_id`-cookie wordt vernieuwd

### → Plex-weergave faalt maar directe weergave werkt

- controleer of de host van de movies-server `plex.base_url` kan bereiken
- controleer of Plex in de configuratie is ingeschakeld
- controleer of het geconfigureerde token geldig is

### → Directe weergave faalt maar Plex werkt

- de container of codec is waarschijnlijk niet veilig voor native browserweergave op dat apparaat
- laat Plex ingeschakeld voor die bestanden, of forceer het compatibiliteitspad via lokale transcoding of Plex

### → Lokale transcoding werkt niet

- controleer of `ffmpeg` en `ffprobe` zijn geïnstalleerd
- controleer of `on_demand_transcode` is ingeschakeld
- controleer of het bronbestand een van de momenteel ondersteunde containers is: `.mkv` of `.ts`

---

## 📦 Releaseversies

Pakketversies worden afgeleid van Git-tags.

- TestPyPI/testing: gebruik een ontwikkelversie zoals `2026.3.26.dev1`
- PyPI-prerelease: gebruik een release candidate zoals `2026.3.26rc1`
- PyPI-stable: gebruik een stabiele versie zoals `2026.3.26`
- Git-tags moeten `v2026.3.26.dev1`, `v2026.3.26rc1` en `v2026.3.26` zijn
  
---

## ©️ Licentie

Dit project wordt uitgebracht onder de MIT-licentie. Voeg een `LICENSE`-bestand met de MIT-tekst toe wanneer je het publiceert of opnieuw distribueert.
