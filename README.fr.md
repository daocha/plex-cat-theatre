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
  <p><strong>Ultra léger, mode privé 🔐, multi-appareils, streaming intelligent</strong></p>
  <p>Aucune application requise. Installation simple du serveur. Interface adaptée au mobile pour connecter votre NAS partout, avec intégration Plex en option</p>
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



> Pas de dépendances lourdes, tout est transparent. Serveur léger auto-hébergé de navigation et de streaming vidéo construit avec Flask, Waitress et `ffmpeg`, avec intégration _`Plex`_ facultative pour une lecture axée sur la compatibilité.

---

![Screenshot 2026-03-22 at 9 39 12 PM](https://github.com/user-attachments/assets/124f21b7-71b0-46fc-9d76-c73f700c25f3)

---

## ✨ Pourquoi l'utiliser

Cat Theatre est volontairement léger :

- 🩷 Aucun abonnement Plex 💰 n'est nécessaire pour l'_accès distant_
- ✅ Surface de dépendances Python réduite
- ✅ Aucune base de données requise
- ✅ Catalogage centré sur le système de fichiers
- ✅ Compatible avec 🖥️ ordinateur, 📱 mobile et tablette
- ✅ Flux de scan portable basé sur le polling au lieu de dépendre de watchers spécifiques à l'OS
- 🔶 Intégration Plex en couche optionnelle au lieu d'être requise pour la lecture principale

## ✴️ Fonctionnalités

- 🎬 Bibliothèques média locales / NAS réparties sur plusieurs dossiers
- 🌄 Génération de vignettes / affiches et d'images de prévisualisation
- 🔐 Dossiers privés avec déverrouillage basé sur l'appareil
- 🔗 Déploiement derrière un reverse proxy sous un préfixe de chemin comme `http://192.168.1.100/movie/`
- 📽️ Stratégies de lecture mixtes : lecture directe, transcodage local intégré pour `.mkv` et `.ts`, ou proxy HLS piloté par Plex. Changement simple média par média
- 🌐 Cache d'images du navigateur plus cache de métadonnées IndexedDB

---
→ Installation en une ligne :
```
curl -fsSL https://raw.githubusercontent.com/daocha/plex-cat-theatre/main/install.sh | bash
```
---

## 🟢 Prérequis

### Python 3.9 ou plus récent

Paquets Python actuels :

- `Flask`
- `waitress`

### Binaires système requis pour l'analyse des métadonnées, les aperçus, les vignettes et le transcodage local :

- `ffmpeg`
- `ffprobe`

Vérifiez qu'ils sont disponibles :

```bash
which ffmpeg
which ffprobe
```

---

## 🚀 Démarrage rapide


### → Option A : installation en une ligne :
```
curl -fsSL https://raw.githubusercontent.com/daocha/plex-cat-theatre/main/install.sh | bash
```

### → Option B : installation depuis PyPI avec pip

```bash
pip install plex-cat-theatre
plex-cat-theatre-init
plex-cat-theatre --config ~/movies_config.json
```

### → Option C : méthode de démarrage recommandée

```bash
git clone https://github.com/daocha/plex-cat-theatre
cd plex-cat-theatre
./startup.sh
```

Ce script d'amorçage peut :

- créer `movies_config.json` à partir de l'exemple de configuration lors du premier lancement
- créer un `.venv` local
- installer les dépendances Python dans cet environnement virtuel local
- créer si nécessaire les dossiers `cache/thumbnails` et `logs` relatifs au fichier de configuration
- vérifier `ffmpeg` et `ffprobe`
- aider en option à générer le hash du code secret du mode privé
- démarrer le serveur avec votre configuration locale

Vous pouvez aussi suivre le flux manuel ci-dessous :

1. Copiez l'exemple de configuration :

```bash
cp movies_config.sample.json movies_config.json
```

2. Modifiez `movies_config.json` selon votre environnement.

### 🌐 Démarrer le serveur :

```bash
# si vous suivez l'option A ou l'option B, exécutez
plex-cat-theatre --config ~/movies_config.json

# si vous suivez l'option C, exécutez
python3 movies_server.py --config movies_config.json
```

Ouvrez l'interface :

```text
http://localhost:9245
```
### 🔑 Changer le code secret
```bash
# si vous suivez l'option A ou l'option B, exécutez
plex-cat-theatre-passcode newpasscode

# si vous suivez l'option C, exécutez
python3 passcode.py newpasscode
```
- les dossiers privés restent masqués tant que l'appareil n'est pas autorisé
- l'état de déverrouillage est lié à un identifiant d'appareil
- les appareils approuvés sont stockés côté serveur
- le script peut faire tourner le code secret du mode privé et effacer les approbations

---

## 🗂️ Structure du projet

- `movies_server.py` : point d'entrée Flask et branchement des routes
- `movies_server_core.py` : helpers serveur partagés pour l'auth, la config, les cookies et la gestion des chemins de montage
- `movies_catalog.py` : scan du catalogue, génération des vignettes, extraction des sous-titres et helpers de transcodage local
- `movies_server_plex.py` : adaptateur Plex, mappage des affiches/sous-titres et proxy HLS Plex
- `movies.js` : source du frontend
- `movies.min.js` : bundle frontend minifié
- `movies.css` : styles de la galerie et du lecteur
- `passcode.py` : helper pour faire tourner le code secret du mode privé

---

## ⚙️ Configuration

L'exemple de configuration est volontairement assaini et n'inclut pas :

- de vrais chemins du système de fichiers
- de vrais jetons Plex
- de vrais codes secrets hachés
- des valeurs spécifiques à l'appareil

### 📍 Champs importants

<table>
  <tr>
    <td width="200"><code>root</code></td>
    <td>racines média à scanner (plusieurs dossiers sont pris en charge)</td>
  </tr>
  <tr>
    <td><code>thumbs_dir</code></td>
    <td>répertoire pour les vignettes et images de prévisualisation. Valeur par défaut : <code>./cache/thumbnails</code></td>
  </tr>
  <tr>
    <td><code>private_folder</code></td>
    <td>préfixes de dossiers traités comme privés. Exemple : <code>Personal</code>. Tout ce qui se trouve sous le dossier <code>Personal</code> reste verrouillé jusqu'à son déverrouillage depuis l'interface.</td>
  </tr>
  <tr>
    <td><code>private_passcode</code></td>
    <td>hash du code secret du mode privé. Vous ne devez pas le modifier directement en clair. Pour le mettre à jour, voir la section <code>Changer le code secret</code>.</td>
  </tr>
  <tr>
    <td><code>mount_script</code></td>
    <td>[optionnel] Commande utilisée lorsqu'une lecture tombe sur un dossier média manquant à cause d'un montage accidentellement démonté.</td>
  </tr>
  <tr>
    <td><code>transcode</code></td>
    <td>Active le worker de transcodage en arrière-plan côté catalogue pour les conteneurs source comme `.mkv` et `.ts` ; cela peut générer des fichiers transcodés annexes à côté de la bibliothèque source, il est donc généralement préférable de laisser cette option à <code>false</code>, surtout lorsque l'intégration Plex est activée. Valeur par défaut : <code>false</code></td>
  </tr>
  <tr>
    <td><code>auto_scan_on_start</code></td>
    <td>Relance un scan des médias au démarrage. Valeur par défaut : <code>false</code></td>
  </tr>
  <tr>
    <td><code>on_demand_transcode</code></td>
    <td>Active le transcodage à l'exécution dans le lecteur pour les conteneurs source, avec encodage matériel si disponible et repli vers l'encodage logiciel si nécessaire. Valeur par défaut : <code>true</code></td>
  </tr>
  <tr>
    <td><code>on_demand_hls</code></td>
    <td>Active les playlists HLS intégrées pour les conteneurs source. Valeur par défaut : <code>true</code></td>
  </tr>
  <tr>
  <td><code>enable_plex_server</code></td>
  <td>📍 [optionnel] Active l'intégration Plex. Valeur par défaut : <code>false</code>. Assurez-vous que Plex Server est déjà installé et correctement configuré avant d'activer cette option.<br> Ce serveur prend en charge les sous-titres natifs, mais si vous souhaitez récupérer automatiquement des sous-titres, il vaut mieux laisser Plex s'en charger.
  <br> Pour une meilleure expérience de transcodage à la demande, il est fortement recommandé d'installer un serveur Plex afin de profiter d'un streaming plus fluide.<br>
  Même sans serveur Plex, ce serveur reste pleinement utilisable, mais notez ceci :
  <br>→ Pour les médias que votre appareil peut lire directement, la fonction de recherche fonctionne parfaitement.
  <br>→ Pour les médias que votre appareil ne peut pas lire directement, par exemple <code>h.265 avec audio DTS</code> (h.265 avec AAC ou MP3 n'est pas concerné), <code>.mkv</code>, <code>.ts</code> ou <code>.wmv</code>, ce serveur peut toujours transcoder à la volée, mais la recherche peut ne pas être disponible.
  </td>
  </tr>
  <tr>
    <td><code>plex.base_url</code></td>
    <td>URL de base du serveur Plex.</td>
  </tr>
  <tr>
    <td><code>plex.token</code></td>
    <td>Jeton Plex</td>
  </tr>
  <tr>
    <td><code>debug_enabled</code></td>
    <td>Affiche l'overlay de debug intégré</td>
  </tr>
  <tr>
    <td><code>direct_playback</code></td>
    <td>Objet avec <code>enabled</code> et <code>audio_whitelist</code>. Avec <code>enabled=true</code>, cela permet de lire le média avec le lecteur natif sans transcodage (rapide). Il est recommandé de conserver les réglages par défaut.</td>
  </tr>
</table>

### Exemple minimal en local uniquement

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

### Exemple avec intégration Plex

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

### 🅿️ Comportement du scan Plex

- la génération locale des vignettes d'affiche est ignorée lorsque des affiches Plex sont disponibles
- les vignettes locales déjà mises en cache peuvent toujours être réutilisées
- la génération d'images de prévisualisation reste activée
- l'intégration Plex reste optionnelle et le mode local seul continue de fonctionner

### → Comment obtenir un jeton Plex

#### Méthode 1 : session Plex Web existante

1. Ouvrez Plex Web et connectez-vous.
2. Ouvrez les outils de développement du navigateur.
3. Allez dans l'onglet Réseau.
4. Rechargez la page.
5. Inspectez une requête envoyée à votre serveur Plex.
6. Repérez `X-Plex-Token` dans l'URL ou dans les en-têtes.

#### Méthode 2 : stockage du navigateur

Vérifiez :

- le stockage local (`Local Storage`)
- le stockage de session (`Session Storage`)
- les URL et en-têtes des requêtes dans les DevTools

#### Méthode 3 : requête locale directe

Si vous avez déjà une session Plex Web active sur la même machine, inspectez les requêtes Plex dans les DevTools et cherchez :

```text
X-Plex-Token=...
```

‼️ Notes de sécurité :

- traitez le jeton Plex comme un mot de passe
- ne le committez pas dans git
- conservez-le uniquement dans `movies_config.json`

---

## 🎥 Modes de lecture

### 1. Lecture directe native

Utilisée pour les fichiers sûrs pour le navigateur comme `.mp4`, `.m4v` et `.webm`.

Comportement :

- sert directement le fichier local depuis `/video/<id>`
- prend en charge les requêtes HTTP range
- évite le coût du transcodage lorsque le navigateur peut lire le fichier nativement

Idéal pour :

- les fichiers de type MP4/H.264
- les navigateurs qui savent déjà lire le fichier directement
- les fichiers dont les codecs audio correspondent à la whitelist de lecture directe

### 2. Transcodage local intégré sans Plex

Il s'agit du chemin de repli lorsque Plex n'est pas activé, ou lorsque vous souhaitez rester entièrement en local.

Implémentation actuelle :

- `.mkv` et `.ts` peuvent être exposés en HLS local via `/hls/<id>/index.m3u8`
- ces mêmes fichiers peuvent aussi être diffusés en MP4 fragmenté via `/video/<id>?fmp4=1`
- les segments HLS sont générés à la demande avec `ffmpeg`
- l'encodage matériel peut être tenté d'abord puis revenir à `libx264`
- la sortie fMP4 est générée avec `libx264` plus AAC

### 3. Lecture adossée à Plex

Quand l'intégration Plex est activée :

- le frontend peut utiliser `plex_stream_url` pour une lecture plus tolérante côté compatibilité
- Plex génère la playlist HLS en amont
- ce serveur réécrit la playlist et proxifie les requêtes de playlists imbriquées et de segments
- le navigateur parle toujours à cette application, pas directement à Plex

Idéal pour :

- les contenus MKV ou TS sur des appareils ayant un support limité des codecs ou des conteneurs
- les cas où la sélection des sous-titres ou la normalisation des flux par Plex est préférable

### Politique de sélection de lecture

- la lecture directe est prioritaire pour les fichiers sûrs pour le navigateur dont les codecs audio correspondent à `direct_playback.audio_whitelist`
- Plex reste prioritaire pour `.mkv`, `.ts`, HLS, fMP4 ou les codecs audio non pris en charge
- le délai de repli HLS natif iOS est plus long afin de laisser au flux Plex le temps de se préparer

### Logique de lecture par défaut

- `Direct` est préféré pour `.mp4`, `.m4v`, `.webm` et `.avi` lorsque l'URL directe pointe vers un vrai fichier et que les codecs audio sont compatibles avec la whitelist
- si les métadonnées de codec audio sont absentes pour l'une de ces extensions sûres pour le navigateur, l'application préfère quand même `Direct`
- `Plex` est préféré pour `.mkv`, `.ts`, les URL directes HLS/fMP4 et les fichiers dont les codecs audio connus sortent de la whitelist
- s'il n'existe aucune correspondance Plex, l'application revient à `Direct`

---

## Modèle d'authentification

L'application utilise différentes méthodes de transport selon le type de requête :

- les requêtes API utilisent l'en-tête `X-Device-Id`
- les requêtes HLS et de proxy Plex utilisent l'en-tête `X-Device-Id`
- les requêtes média directes natives utilisent le cookie de repli `movies_device_id`

Cette séparation existe parce que les requêtes natives `<video src="...">` ne peuvent pas joindre d'en-têtes personnalisés arbitraires.

---

## Support du reverse proxy et des chemins de contexte

L'application prend en charge un déploiement sous des sous-chemins comme :

- `https://example.com/movie/`
- `https://example.com/cinema/`

Le routage conserve le préfixe de montage actif pour :

- les médias directs
- le HLS local
- les requêtes de proxy HLS Plex
- les ressources d'affiches et de sous-titres

---

## Accès Plex distant avec Tailscale

Si l'interface personnalisée est accessible à distance mais que Plex n'est joignable que sur un LAN privé, l'hôte du serveur de films doit toujours pouvoir joindre directement le backend Plex.

### Même hôte

```json
"plex": {
  "base_url": "http://127.0.0.1:32400"
}
```

### Plex sur une autre machine du LAN

Annoncez la route depuis un nœud Tailscale capable d'atteindre Plex :

```bash
sudo tailscale up --advertise-routes=192.168.50.0/24
```

Puis vérifiez la connectivité depuis l'hôte du serveur de films :

```bash
curl http://192.168.50.10:32400/identity
```

📌 Notes :

- le navigateur n'a pas besoin d'un accès réseau direct à Plex
- le processus du serveur de films doit pouvoir atteindre `plex.base_url`
- un nom reverse proxy ou MagicDNS pour l'interface ne rend pas Plex joignable à lui seul

---

## 💾 Stratégie de cache

### Cache des images

Les vignettes, images de prévisualisation et affiches Plex sont servies avec des en-têtes de cache immuables de longue durée.

### Cache des métadonnées

Les instantanés de métadonnées de la galerie sont mis en cache dans IndexedDB avec un stockage borné :

- TTL d'un jour
- jusqu'à 8 instantanés
- jusqu'à environ 18 Mo de taille totale estimée
- les entrées les plus anciennes sont évincées lorsque les limites sont dépassées

Chaque instantané mis en cache stocke :

- le `catalogStatus` du serveur
- le cache de la liste des dossiers
- les `videos` chargées
- les compteurs de pagination comme `serverTotal`, `serverOffset` et `serverExhausted`

L'éviction est opportuniste plutôt que planifiée :

- les entrées expirées sont supprimées lors de la lecture ou d'un nettoyage ultérieur
- le nettoyage s'exécute après l'enregistrement de nouveaux instantanés
- la pression sur le stockage du navigateur ou l'effacement manuel des données du site peut aussi supprimer les données IndexedDB

---

## 🔍 Comportement du scan

Le scan du catalogue est conçu pour rester incrémental en coût même s'il parcourt toujours chaque racine configurée.

Comportement actuel :

- les fichiers inchangés réutilisent les signatures mises en cache `mtime + size`
- les scans périodiques ne trient plus la liste complète des chemins avant traitement
- les fichiers supprimés sont retirés du catalogue en mémoire et de l'index persisté
- les fichiers supprimés déclenchent aussi le nettoyage des vignettes et aperçus générés
- l'enregistrement de l'index réutilise les signatures de fichiers mises en cache au lieu de refaire un `stat` sur chaque fichier

Ce que le scan fait encore :

- il parcourt les racines média configurées pour détecter les fichiers ajoutés, modifiés et supprimés
- il met en file la génération de previews lorsque les images de prévisualisation sont absentes

Ce qu'il ne fait pas :

- il ne calcule pas de checksum sur les gros fichiers média lors des scans périodiques
- il ne régénère pas les vignettes ou métadonnées des fichiers inchangés tant que les artefacts mis en cache existent

### → Déclencher un rescan

Rescan incrémental normal :

```bash
curl -s http://localhost:9245/rescan | python3 -m json.tool
```

Rescan complet forcé :

```bash
curl -s "http://localhost:9245/rescan?full=1" | python3 -m json.tool
```

### → Interface de nouvelle analyse

Le bouton `Rescan` ouvre une boîte de dialogue d'action au lieu de lancer immédiatement un scan incrémental.

Actions disponibles :

- `Rescan` : scan incrémental des fichiers nouveaux ou modifiés
- `Full Scan` : efface l'état de scan enregistré et force une revalidation complète des métadonnées
- `Refresh Database` : efface les instantanés IndexedDB du navigateur et recharge des données de catalogue fraîches

### ⛓️‍💥 Récupération d'un montage manquant

Cette fonctionnalité est conçue pour le cas où certains NAS seraient configurés avec une mise en veille automatique, ce qui peut entraîner l'éjection automatique d'un montage SMB par certains systèmes.

Si `mount_script` est configuré et qu'une requête média tombe sur un dossier manquant, le serveur :

1. détectera que le dossier parent n'existe pas
2. invoquera une fois le script de montage configuré
3. revérifiera le chemin cible
4. retournera `Media folder is not mounted` avec HTTP 404 uniquement si le dossier reste indisponible

Le frontend traite les 404 de lecture comme définitifs pour cette tentative et affiche un message de nouvelle tentative au lieu de marteler le serveur en boucle.

---

## 📄 Fichiers générés

Ces fichiers sont générés à l'exécution et ne doivent pas être commités :

- `movies_config.json`
- `movies_state.json`
- `movies_auth_state.json`
- `movies_catalog_index.json`
- `cache/`

---

## 🛠️ Dépannage


### → Overlay de debug

Activez `debug_enabled` dans `movies_config.json` pour garder un overlay de debug permanent dans le coin inférieur droit.

Le panneau indique :

- si le serveur favorise la lecture directe ou Plex
- la whitelist audio configurée pour la lecture directe
- le candidat de lecture actuel et l'identifiant vidéo
- les métriques récentes d'avancement du scan

Inspectez les valeurs de configuration actives avec :

```bash
curl -s http://localhost:9245/api/config | python3 -m json.tool
```

### → Les changements d'interface n'apparaissent pas

- L'application charge actuellement `movies.js` directement depuis `index.html`, donc les changements frontend prennent effet sans reconstruire `movies.min.js`.
- rechargez d'abord la page normalement
- si le bundle JS a changé, vérifiez que `index.html` référence bien la version attendue du bundle

### → La lecture directe privée échoue

- déverrouillez à nouveau le mode privé afin que le cookie `movies_device_id` soit rafraîchi

### → La lecture Plex échoue mais la lecture directe fonctionne

- vérifiez que l'hôte du serveur de films peut joindre `plex.base_url`
- vérifiez que Plex est activé dans la configuration
- vérifiez que le jeton configuré est valide

### → La lecture directe échoue mais Plex fonctionne

- le conteneur ou le codec n'est probablement pas sûr pour une lecture native dans le navigateur sur cet appareil
- gardez Plex activé pour ces fichiers, ou forcez le chemin de compatibilité via le transcodage local ou Plex

### → Le transcodage local ne fonctionne pas

- vérifiez que `ffmpeg` et `ffprobe` sont installés
- vérifiez que `on_demand_transcode` est activé
- vérifiez que le fichier source fait partie des conteneurs actuellement pris en charge : `.mkv` ou `.ts`

---

## 📦 Gestion des versions de release

Les versions du paquet sont dérivées des tags Git.

- TestPyPI/testing : utilisez une version de développement comme `2026.3.26.dev1`
- Prérelease PyPI : utilisez une release candidate comme `2026.3.26rc1`
- Stable PyPI : utilisez une version stable comme `2026.3.26`
- Les tags Git doivent être `v2026.3.26.dev1`, `v2026.3.26rc1` et `v2026.3.26`
  
---

## ©️ Licence

Ce projet est publié sous licence MIT. Ajoutez un fichier `LICENSE` contenant le texte MIT lors de la publication ou de la redistribution.
