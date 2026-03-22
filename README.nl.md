# Cat Theatre Movies Server

> Lichtgewicht zelfgehoste filmbrowser en streamingserver gebouwd met Flask, Waitress en `ffmpeg`, met optionele _`Plex`_-integratie voor compatibiliteitsgerichte weergave.

---

![Screenshot 2026-03-22 at 9 39 12 PM](https://github.com/user-attachments/assets/124f21b7-71b0-46fc-9d76-c73f700c25f3)

---

**Talen**

[English](./README.md) | [简体中文](./README.zh-CN.md) | [繁體中文（香港）](./README.zh-HK.md) | [繁體中文（台灣）](./README.zh-TW.md) | [Français](./README.fr.md) | [한국어](./README.ko.md) | [日本語](./README.ja.md) | [Deutsch](./README.de.md) | [ไทย](./README.th.md) | [Tiếng Việt](./README.vi.md) | `Nederlands`

---

## Overzicht

Cat Theatre is bewust lichtgewicht:

- klein Python-afhankelijkheidsoppervlak
- geen database nodig
- catalogisering met het bestandssysteem als uitgangspunt
- draagbare polling-gebaseerde scanstroom in plaats van afhankelijkheid van OS-specifieke watchers
- optionele Plex-integratie als extra laag in plaats van vereiste voor kernweergave

Het is ontworpen voor:

- lokale mediabibliotheken verspreid over één of meer mappen
- generatie van thumbnails en previewframes
- apparaatgebaseerde toegangscontrole voor privémappen
- deployment achter een reverse proxy onder een prefix zoals `/movie/`
- gemengde afspeelstrategieën: direct bestandsafspelen, ingebouwde lokale transcoding of Plex-gebaseerde HLS

---

## Functies

- mediascan over meerdere roots
- generatie van posterthumbnails en previewframes
- privémappen met apparaatgebaseerde ontgrendeling
- native direct playback voor browserveilige formaten
- ingebouwde lokale transcoding voor `.mkv` en `.ts` wanneer ingeschakeld
- Plex-integratie voor afspelen, posters, ondertitels en HLS-proxying
- contextpadbewuste routing voor reverse proxies
- browserafbeeldingscache plus IndexedDB-metadatacache

### Opmerkingen Over UX En Afspelen

- het ingebouwde debugpaneel staat rechtsonder en kan naar de dichtstbijzijnde rand schuiven
- afspelen kiest automatisch het veiligere pad voor het huidige bestand en apparaat
- handmatige Direct/Plex-overschrijvingen worden per video in IndexedDB opgeslagen
- gecachte thumbnails en metadata blijven binnen de opslaglimieten van de browser

---

## Vereisten

### Python

```bash
pip install -r requirements.txt
```

Huidige Python-pakketten:

- `Flask`
- `waitress`

### Systeembinaries

Vereist voor metadataonderzoek, previews, thumbnails en lokale transcoding:

- `ffmpeg`
- `ffprobe`

Controleer of ze beschikbaar zijn:

```bash
which ffmpeg
which ffprobe
```

---

## Snel Starten

Voorkeursmanier om te starten:

```bash
./startup.sh
```

Dit bootstrapscript kan:

- bij de eerste keer opstarten `movies_config.json` maken vanuit de voorbeeldconfiguratie
- een lokale `.venv` aanmaken
- Python-afhankelijkheden in die lokale virtuele omgeving installeren
- `ffmpeg` en `ffprobe` controleren
- optioneel helpen bij het genereren van de hash voor de privémodus-passcode
- de server starten met je lokale configuratie

Je kunt nog steeds de handmatige stappen hieronder gebruiken:

1. Kopieer de voorbeeldconfiguratie:

```bash
cp movies_config.sample.json movies_config.json
```

2. Bewerk `movies_config.json` voor jouw omgeving.

3. Start de server:

```bash
python3 movies_server.py --config movies_config.json
```

4. Open de UI:

```text
http://localhost:9245
```

Als je de app achter een reverse proxy onder een prefix zoals `/movie/` inzet, open dan de URL met prefix.

---

## Projectstructuur

- `movies_server.py`: Flask-entrypoint en routekoppeling
- `movies_server_core.py`: gedeelde serverhelpers voor auth, config, cookies en afhandeling van mountpaden
- `movies_catalog.py`: catalogusscan, thumbnailgeneratie, ondertitelextractie en lokale transcodinghelpers
- `movies_server_plex.py`: Plex-adapter, poster-/ondertitelmapping en Plex HLS-proxying
- `movies.js`: frontendbroncode
- `movies.min.js`: geminificeerde frontendbundle
- `movies.css`: stijlen voor galerij en speler
- `passcode.py`: helper voor het roteren van de privémodus-passcode

---

## Configuratie

De voorbeeldconfiguratie is bewust opgeschoond en bevat niet:

- echte bestandssysteempaden
- echte Plex-tokens
- echte pincodes
- apparaatspecifieke waarden

### Belangrijke Velden

- `root`: mediaroots om te scannen
- `thumbs_dir`: map voor thumbnails en previewframes
- `private_folder`: mapprefixen die als privé worden behandeld
- `private_passcode`: hash van de privémodus-passcode
- `mount_script`: optioneel commando dat wordt gebruikt wanneer afspelen een ontbrekende mediamap raakt
- `transcode`: schakelt de achtergrondtranscodeworker aan de cataloguskant in voor broncontainers zoals `.mkv` en `.ts`; dit kan aparte getranscodeerde sidecarbestanden naast de mediabibliotheek genereren, dus normaal laat je dit best op `false`, vooral wanneer Plex-integratie is ingeschakeld
- `auto_scan_on_start`: media opnieuw scannen bij opstarten
- `on_demand_transcode`: runtime-transcoding in de speler voor broncontainers inschakelen, waarbij zo mogelijk hardware-encoding wordt gebruikt en anders wordt teruggevallen op software-encoding
- `on_demand_hls`: ingebouwde HLS-playlists voor broncontainers inschakelen
- `enable_plex_server`: Plex-integratie inschakelen
- `plex.base_url`: basis-URL van de Plex-server
- `plex.token`: Plex-token
- `debug_enabled`: de ingebouwde debug-overlay tonen
- `direct_playback`: object met `enabled` en `audio_whitelist`

### Minimale Alleen-Lokaal Voorbeeld

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

### Voorbeeld Met Plex-Integratie

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

### Plex-scan Gedrag

- lokale generering van posterthumbnails wordt overgeslagen wanneer Plex-posters beschikbaar zijn
- bestaande lokaal gecachte thumbnails kunnen nog steeds worden hergebruikt
- generatie van previewframes blijft ingeschakeld
- Plex-integratie blijft optioneel en alleen-lokaal modus blijft werken

### Hoe Je Een Plex-token Krijgt

#### Methode 1: Bestaande Plex Web-sessie

1. Open Plex Web en log in.
2. Open de ontwikkelaarstools van de browser.
3. Ga naar het tabblad Network.
4. Vernieuw de pagina.
5. Inspecteer een request dat naar je Plex-server is verzonden.
6. Zoek `X-Plex-Token` in de URL of headers.

#### Methode 2: Browseropslag

Controleer:

- Local Storage
- Session Storage
- request-URL’s en headers in DevTools

#### Methode 3: Directe Lokale Request

Als je al een actieve Plex Web-sessie op dezelfde machine hebt, inspecteer dan Plex-requests in DevTools en zoek naar:

```text
X-Plex-Token=...
```

Beveiligingsnotities:

- behandel het Plex-token als een wachtwoord
- commit het niet in git
- bewaar het alleen in `movies_config.json`

---

## Afspeelmodi

### 1. Native Direct Playback

Gebruikt voor browserveilige bestanden zoals `.mp4`, `.m4v` en `.webm`.

Gedrag:

- levert het lokale bestand direct via `/video/<id>`
- ondersteunt HTTP-range-requests
- vermijdt transcoding-overhead wanneer de browser het bestand native kan afspelen

Het beste voor:

- bestanden van het type MP4/H.264
- browsers die het bestand al direct ondersteunen
- bestanden waarvan de audiocodecs overeenkomen met de direct-play-whitelist

### 2. Ingebouwde Lokale Transcoding Zonder Plex

Dit is het fallbackpad wanneer Plex niet is ingeschakeld, of wanneer je bewust volledig lokaal wilt blijven.

Huidige implementatie:

- `.mkv` en `.ts` kunnen als lokale HLS worden aangeboden via `/hls/<id>/index.m3u8`
- dezelfde bestanden kunnen ook als fragmented MP4 worden gestreamd via `/video/<id>?fmp4=1`
- HLS-segmenten worden on demand gegenereerd met `ffmpeg`
- hardware-encoding kan eerst geprobeerd worden en terugvallen op `libx264`
- fMP4-uitvoer wordt gegenereerd met `libx264` plus AAC

### 3. Plex-gebaseerd Afspelen

Wanneer Plex-integratie is ingeschakeld:

- kan de frontend `plex_stream_url` gebruiken voor compatibiliteitsgerichte weergave
- genereert Plex de upstream HLS-playlist
- herschrijft deze server de playlist en proxyt geneste playlists en segmentrequests
- praat de browser nog steeds met deze app en niet direct met Plex

Het beste voor:

- MKV- of TS-inhoud op apparaten met zwakkere codec- of containersupport
- gevallen waarin Plex-ondertitelselectie of streamnormalisatie de voorkeur heeft

### Beleid Voor Afspeelselectie

- direct playback wint voor browserveilige bestanden waarvan de audiocodecs overeenkomen met `direct_playback.audio_whitelist`
- Plex blijft de voorkeur houden voor `.mkv`, `.ts`, HLS, fMP4 of niet-ondersteunde audiocodecs
- de iOS-native HLS-fallbacktiming is langer zodat de Plex-stream tijd heeft om op te warmen

### Standaard Afspeellogica

- `Direct` heeft de voorkeur voor `.mp4`, `.m4v`, `.webm` en `.avi` wanneer de directe URL een echt bestandspad is en de audiocodecs whitelist-veilig zijn
- als audiocodecmetadata ontbreekt voor een van die browserveilige extensies, geeft de app nog steeds de voorkeur aan `Direct`
- `Plex` heeft de voorkeur voor `.mkv`, `.ts`, HLS/fMP4-directe URL’s en bestanden waarvan de bekende audiocodecs buiten de whitelist vallen
- als er geen Plex-match bestaat, valt de app terug op `Direct`

---

## Debug-overlay

Schakel `debug_enabled` in `movies_config.json` in om een permanente debug-overlay rechtsonder te houden.

Het paneel rapporteert:

- of de server direct playback of Plex verkiest
- de geconfigureerde direct-play-audiowhitelist
- de huidige afspeelkandidaat en video-ID
- recente scanvoortgangsmetingen

Controleer actieve configwaarden met:

```bash
curl -s http://localhost:9245/api/config | python3 -m json.tool
```

Als je de app onder `/movie/` serveert, gebruik dan het pad met prefix.

---

## Authenticatiemodel

De app gebruikt verschillende transportmethoden afhankelijk van het requesttype:

- API-requests gebruiken de header `X-Device-Id`
- HLS- en Plex-proxyrequests gebruiken de header `X-Device-Id`
- native directe mediarequests gebruiken de cookie `movies_device_id` als fallback

Deze splitsing bestaat omdat native `<video src="...">`-requests geen willekeurige aangepaste headers kunnen meesturen.

---

## Reverse Proxy- En Contextpadondersteuning

De app ondersteunt deployment onder subpaden zoals:

- `https://example.com/movie/`
- `https://example.com/cinema/`

Routing behoudt het actieve mount-prefix voor:

- directe media
- lokale HLS
- Plex HLS-proxyrequests
- poster- en ondertitelassets

---

## Externe Plex-toegang Met Tailscale

Als de aangepaste UI op afstand bereikbaar is maar Plex alleen bereikbaar is op een privé-LAN, dan moet de host van de movies server nog steeds de Plex-backend direct kunnen bereiken.

### Zelfde Host

```json
"plex": {
  "base_url": "http://127.0.0.1:32400"
}
```

### Plex Op Een Andere LAN-machine

Adverteer de route vanaf een Tailscale-node die Plex kan bereiken:

```bash
sudo tailscale up --advertise-routes=192.168.50.0/24
```

Controleer daarna bereikbaarheid vanaf de host van de movies server:

```bash
curl http://192.168.50.10:32400/identity
```

Opmerkingen:

- de browser heeft geen directe netwerktoegang tot Plex nodig
- het movies-server-proces moet `plex.base_url` kunnen bereiken
- reverse-proxy- of MagicDNS-namen voor de UI maken Plex niet vanzelf bereikbaar

---

## Cachingstrategie

### Afbeeldingscache

Thumbnails, previewframes en Plex-posterafbeeldingen worden geleverd met langdurige immutable-cacheheaders.

### Metadatacache

Galerijmetadata-snapshots worden in IndexedDB gecachet met begrensde opslag:

- TTL van 1 dag
- maximaal 8 snapshotrecords
- maximaal ongeveer 18 MB geschatte totale grootte
- oudere items worden verwijderd wanneer limieten worden overschreden

Elke gecachte snapshot slaat op:

- server-`catalogStatus`
- maplijstcache
- geladen `videos`
- pagineringstellers zoals `serverTotal`, `serverOffset` en `serverExhausted`

Opschoning gebeurt opportunistisch in plaats van gepland:

- verlopen items worden verwijderd bij lezen of latere pruning
- pruning draait nadat nieuwe snapshots zijn opgeslagen
- browseropslagdruk of handmatig wissen van sitedata kan IndexedDB-data ook verwijderen

---

## Scangedrag

De catalogusscan is ontworpen om incrementeel in kosten te blijven, ook al loopt hij nog steeds door elke geconfigureerde root.

Huidig gedrag:

- ongewijzigde bestanden hergebruiken gecachte `mtime + size`-handtekeningen
- periodieke scans sorteren niet langer eerst de volledige padlijst
- verwijderde bestanden worden uit de in-memorycatalogus en de opgeslagen index verwijderd
- verwijderde bestanden triggeren ook het opruimen van gegenereerde thumbnail- en previewbestanden
- indexopslagen hergebruiken gecachte bestandshandtekeningdata in plaats van elk bestand opnieuw te statten

Wat de scan nog steeds doet:

- geconfigureerde mediaroots doorlopen om toegevoegde, gewijzigde en verwijderde bestanden te detecteren
- previewgeneratie in de wachtrij zetten wanneer previewafbeeldingen ontbreken

Wat hij niet doet:

- geen checksums van grote mediabestanden tijdens periodieke scans
- geen thumbnails of metadata opnieuw genereren voor ongewijzigde bestanden tenzij cachebestanden ontbreken

### Volledige Rescan Forceren

Gebruik:

```text
/rescan?full=1
```

Dit is nuttig wanneer:

- iemand handmatig de thumbnail- of previewcachemap heeft verwijderd
- je vermoedt dat het opgeslagen scanmanifest verouderd is
- je een volledige hervalidatie van scan-afgeleide toestand wilt forceren

### Scanstatus Controleren

```bash
curl -s http://localhost:9245/api/status | python3 -m json.tool
```

Als je de app onder `/movie/` serveert, gebruik dan het pad met prefix.

### Rescan Triggeren

Normale incrementele rescan:

```bash
curl -s http://localhost:9245/rescan | python3 -m json.tool
```

Geforceerde volledige rescan:

```bash
curl -s "http://localhost:9245/rescan?full=1" | python3 -m json.tool
```

### Rescan-UI

De knop `Rescan` opent een actiedialoog in plaats van direct een incrementele scan te starten.

Beschikbare acties:

- `Rescan`: incrementele scan voor nieuwe of gewijzigde bestanden
- `Full Scan`: wist opgeslagen scanstatus en forceert volledige metadatavalidatie
- `Refresh Database`: wist browser-IndexedDB-snapshots en laadt verse catalogusdata opnieuw

### Herstel Van Ontbrekende Mount

Als `mount_script` is geconfigureerd en een mediarequest een ontbrekende map raakt, zal de server:

1. detecteren dat de bovenliggende map niet bestaat
2. één keer het geconfigureerde mountscript aanroepen
3. het doelpad opnieuw controleren
4. alleen `Media folder is not mounted` met HTTP 404 retourneren als de map nog steeds niet beschikbaar is

De frontend behandelt afspeel-404’s als definitief voor die poging en toont een retry-bericht in plaats van de server herhaaldelijk te bestoken.

---

## Opmerkingen Voor Frontendontwikkeling

De app laadt momenteel `movies.js` direct vanuit `index.html`, dus frontendwijzigingen worden actief zonder `movies.min.js` opnieuw te bouwen.

---

## Privémodus

- privémappen zijn verborgen tenzij het apparaat is geautoriseerd
- ontgrendelstatus is gekoppeld aan een apparaat-ID
- goedgekeurde apparaten worden server-side opgeslagen
- `passcode.py` kan de privémodus-passcode roteren en goedkeuringen wissen

Voorbeeld:

```bash
python3 passcode.py mynewpasscode
```

---

## Gegenereerde Bestanden

Deze bestanden worden tijdens runtime gegenereerd en mogen niet worden gecommit:

- `movies_config.json`
- `movies_state.json`
- `movies_auth_state.json`
- `movies_catalog_index.json`
- `cache/`

---

## Probleemoplossing

### UI-wijzigingen Verschijnen Niet

- ververs de pagina eerst normaal
- als de JS-bundle is gewijzigd, controleer dan of `index.html` naar de verwachte bundelversie verwijst

### Direct Afspelen Van Privécontent Mislukt

- ontgrendel de privémodus opnieuw zodat de cookie `movies_device_id` wordt vernieuwd

### Plex-afspelen Mislukt Maar Direct Afspelen Werkt

- controleer of de host van de movies server `plex.base_url` kan bereiken
- controleer of Plex is ingeschakeld in de configuratie
- controleer of het geconfigureerde token geldig is

### Direct Afspelen Mislukt Maar Plex Werkt

- de container of codec is waarschijnlijk niet veilig voor native browserafspelen op dat apparaat
- laat Plex ingeschakeld voor die bestanden, of forceer het compatibiliteitspad via lokale transcoding of Plex

### Lokale Transcoding Werkt Niet

- controleer of `ffmpeg` en `ffprobe` zijn geïnstalleerd
- controleer of `on_demand_transcode` is ingeschakeld
- controleer of het bronbestand een van de momenteel ondersteunde containers is: `.mkv` of `.ts`

---

## Licentie

Dit project wordt uitgebracht onder de MIT License. Voeg bij publicatie of herdistributie een `LICENSE`-bestand met de MIT-tekst toe.
