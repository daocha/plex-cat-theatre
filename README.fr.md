# Cat Theatre Movies Server

> Serveur auto-hébergé de navigation et de streaming vidéo construit avec Flask, Waitress et `ffmpeg`, avec intégration Plex facultative pour une lecture axée sur la compatibilité.

**Langues**

[English](./README.md) | [简体中文](./README.zh-CN.md) | [繁體中文（香港）](./README.zh-HK.md) | [繁體中文（台灣）](./README.zh-TW.md) | `Français` | [한국어](./README.ko.md) | [日本語](./README.ja.md) | [Deutsch](./README.de.md) | [ไทย](./README.th.md) | [Tiếng Việt](./README.vi.md) | [Nederlands](./README.nl.md)

---

## Vue D’ensemble

Cat Theatre est volontairement léger :

- faible surface de dépendances Python
- aucune base de données requise
- catalogage centré sur le système de fichiers
- flux de scan portable basé sur le polling plutôt que sur des watchers spécifiques à l’OS
- intégration Plex ajoutée en couche optionnelle plutôt qu’exigée pour la lecture principale

Il est conçu pour :

- des bibliothèques médias locales réparties sur un ou plusieurs dossiers
- la génération de vignettes et d’images de prévisualisation
- le contrôle d’accès aux dossiers privés par appareil
- un déploiement derrière un reverse proxy sous un préfixe comme `/movie/`
- des stratégies de lecture mixtes : lecture directe de fichier, transcodage local intégré ou HLS basé sur Plex

---

## Fonctionnalités

- scan de médias multi-racines
- génération de vignettes d’affiche et d’images de prévisualisation
- dossiers privés avec déverrouillage par appareil
- lecture directe native pour les formats sûrs pour le navigateur
- transcodage local intégré pour `.mkv` et `.ts` lorsqu’il est activé
- intégration Plex pour la lecture, les affiches, les sous-titres et le proxy HLS
- routage conscient du chemin de contexte pour les reverse proxies
- cache d’images du navigateur plus cache de métadonnées IndexedDB

### Notes UX Et Lecture

- le panneau de debug intégré se trouve en bas à droite et peut glisser vers le bord le plus proche
- la lecture choisit automatiquement le chemin le plus sûr pour le fichier et l’appareil courants
- les surcharges manuelles Direct/Plex sont stockées par vidéo dans IndexedDB
- les vignettes et métadonnées mises en cache restent dans les limites de stockage du navigateur

---

## Structure Du Projet

- `movies_server.py` : point d’entrée Flask et routage
- `movies_server_core.py` : helpers serveur partagés pour l’auth, la config, les cookies et la gestion du chemin de montage
- `movies_catalog.py` : scan du catalogue, génération des vignettes, extraction des sous-titres et helpers de transcodage local
- `movies_server_plex.py` : adaptateur Plex, mappage affiches/sous-titres et proxy Plex HLS
- `movies.js` : source frontend
- `movies.min.js` : bundle frontend minifié
- `movies.css` : styles de la galerie et du lecteur
- `passcode.py` : helper pour faire tourner le code de la section privée

---

## Prérequis

### Python

```bash
pip install -r requirements.txt
```

Paquets Python actuels :

- `Flask`
- `waitress`

### Binaires Système

Requis pour la sonde de métadonnées, les aperçus, les vignettes et le transcodage local :

- `ffmpeg`
- `ffprobe`

Vérifiez qu’ils sont disponibles :

```bash
which ffmpeg
which ffprobe
```

---

## Démarrage Rapide

1. Copiez l’exemple de configuration :

```bash
cp movies_config.sample.json movies_config.json
```

2. Modifiez `movies_config.json` selon votre environnement.

3. Démarrez le serveur :

```bash
python3 movies_server.py --config movies_config.json
```

4. Ouvrez l’interface :

```text
http://localhost:9245
```

Si vous déployez l’application derrière un reverse proxy sous un préfixe comme `/movie/`, ouvrez l’URL préfixée à la place.

---

## Configuration

L’exemple de configuration est volontairement nettoyé et n’inclut pas :

- de vrais chemins du système de fichiers
- de vrais tokens Plex
- de vrais codes secrets
- de valeurs spécifiques à un appareil

### Champs Importants

- `root` : racines médias à scanner
- `thumbs_dir` : répertoire des vignettes et images de prévisualisation
- `private_folder` : préfixes de dossiers considérés comme privés
- `private_passcode` : hachage du code secret du mode privé
- `mount_script` : commande optionnelle utilisée lorsqu’une lecture atteint un dossier média manquant
- `transcode` : active le worker de transcodage en arrière-plan côté catalogue pour les conteneurs source comme `.mkv` et `.ts` ; cela peut générer des fichiers transcodés séparés à côté de la bibliothèque média, donc il est généralement préférable de le laisser à `false`, surtout lorsque l’intégration Plex est activée
- `auto_scan_on_start` : rescanner les médias au démarrage
- `on_demand_transcode` : activer le transcodage d’exécution côté lecteur pour les conteneurs source, avec tentative d’encodage matériel en priorité puis repli logiciel si nécessaire
- `on_demand_hls` : activer les playlists HLS intégrées pour les conteneurs source
- `enable_plex_server` : activer l’intégration Plex
- `plex.base_url` : URL de base du serveur Plex
- `plex.token` : token Plex
- `debug_enabled` : afficher l’overlay de debug intégré
- `direct_playback` : objet avec `enabled` et `audio_whitelist`

### Exemple Minimal Local

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

### Exemple Avec Plex

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

### Comportement Du Scan Plex

- la génération locale de vignettes d’affiche est ignorée lorsque des affiches Plex sont disponibles
- les vignettes locales déjà mises en cache peuvent toujours être réutilisées
- la génération d’images de prévisualisation reste activée
- l’intégration Plex reste optionnelle et le mode purement local continue de fonctionner

### Comment Obtenir Un Token Plex

#### Méthode 1 : Session Plex Web Existante

1. Ouvrez Plex Web et connectez-vous.
2. Ouvrez les outils développeur du navigateur.
3. Allez dans l’onglet Réseau.
4. Rechargez la page.
5. Inspectez une requête envoyée à votre serveur Plex.
6. Trouvez `X-Plex-Token` dans l’URL ou les en-têtes.

#### Méthode 2 : Stockage Du Navigateur

Vérifiez :

- Local Storage
- Session Storage
- les URL et en-têtes des requêtes dans DevTools

#### Méthode 3 : Requête Locale Directe

Si vous avez déjà une session Plex Web active sur la même machine, inspectez les requêtes Plex dans DevTools et cherchez :

```text
X-Plex-Token=...
```

Notes de sécurité :

- traitez le token Plex comme un mot de passe
- ne le committez pas dans git
- conservez-le uniquement dans `movies_config.json`

---

## Modes De Lecture

### 1. Lecture Directe Native

Utilisée pour les fichiers sûrs pour le navigateur comme `.mp4`, `.m4v` et `.webm`.

Comportement :

- sert le fichier local directement depuis `/video/<id>`
- prend en charge les requêtes HTTP Range
- évite le coût du transcodage lorsque le navigateur peut lire le fichier nativement

Idéal pour :

- les fichiers de type MP4/H.264
- les navigateurs qui prennent déjà en charge le fichier directement
- les fichiers dont les codecs audio correspondent à la whitelist de lecture directe

### 2. Transcodage Local Intégré Sans Plex

C’est le chemin de secours lorsque Plex n’est pas activé, ou lorsque vous voulez volontairement rester entièrement local.

Implémentation actuelle :

- `.mkv` et `.ts` peuvent être exposés en HLS local sur `/hls/<id>/index.m3u8`
- ces mêmes fichiers peuvent aussi être diffusés en fragmented MP4 via `/video/<id>?fmp4=1`
- les segments HLS sont générés à la demande avec `ffmpeg`
- l’encodage matériel peut être tenté en premier puis retomber sur `libx264`
- la sortie fMP4 est générée avec `libx264` plus AAC

### 3. Lecture Basée Sur Plex

Lorsque l’intégration Plex est activée :

- le frontend peut utiliser `plex_stream_url` pour une lecture axée compatibilité
- Plex génère la playlist HLS amont
- ce serveur réécrit la playlist et proxifie les playlists imbriquées et les requêtes de segments
- le navigateur parle toujours à cette application, pas directement à Plex

Idéal pour :

- le contenu MKV ou TS sur des appareils avec une prise en charge plus faible des codecs ou conteneurs
- les cas où la sélection des sous-titres ou la normalisation du flux par Plex est préférée

### Politique De Sélection De Lecture

- la lecture directe gagne pour les fichiers sûrs pour le navigateur dont les codecs audio correspondent à `direct_playback.audio_whitelist`
- Plex reste préféré pour `.mkv`, `.ts`, HLS, fMP4 ou les codecs audio non pris en charge
- le délai de repli HLS natif iOS est plus long afin de laisser le temps au flux Plex de se préparer

### Logique De Lecture Par Défaut

- `Direct` est préféré pour `.mp4`, `.m4v`, `.webm` et `.avi` lorsque l’URL directe est un vrai chemin de fichier et que les codecs audio sont sûrs selon la whitelist
- si les métadonnées de codec audio sont absentes pour l’une de ces extensions sûres pour le navigateur, l’application préfère quand même `Direct`
- `Plex` est préféré pour `.mkv`, `.ts`, les URL directes HLS/fMP4 et les fichiers dont les codecs audio connus sont hors whitelist
- s’il n’existe aucune correspondance Plex, l’application retombe sur `Direct`

---

## Overlay De Debug

Activez `debug_enabled` dans `movies_config.json` pour conserver un overlay de debug permanent dans le coin inférieur droit.

Le panneau indique :

- si le serveur favorise la lecture directe ou Plex
- la whitelist audio configurée pour la lecture directe
- le candidat de lecture courant et l’ID de la vidéo
- les métriques récentes de progression du scan

Inspectez les valeurs de configuration actives avec :

```bash
curl -s http://localhost:9245/api/config | python3 -m json.tool
```

Si vous servez l’application sous `/movie/`, utilisez le chemin préfixé.

---

## Modèle D’Authentification

L’application utilise différents moyens de transport selon le type de requête :

- les requêtes API utilisent l’en-tête `X-Device-Id`
- les requêtes HLS et proxy Plex utilisent l’en-tête `X-Device-Id`
- les requêtes média directes natives utilisent le cookie `movies_device_id` en repli

Cette séparation existe parce que les requêtes natives `<video src="...">` ne peuvent pas joindre des en-têtes personnalisés arbitraires.

---

## Support Reverse Proxy Et Chemin De Contexte

L’application prend en charge un déploiement sous des sous-chemins comme :

- `https://example.com/movie/`
- `https://example.com/cinema/`

Le routage conserve le préfixe de montage actif pour :

- les médias directs
- le HLS local
- les requêtes de proxy Plex HLS
- les ressources d’affiche et de sous-titres

---

## Accès Plex Distant Avec Tailscale

Si l’interface personnalisée est accessible à distance mais que Plex n’est accessible que sur un LAN privé, l’hôte du movies server doit tout de même pouvoir joindre directement le backend Plex.

### Même Hôte

```json
"plex": {
  "base_url": "http://127.0.0.1:32400"
}
```

### Plex Sur Une Autre Machine Du LAN

Annoncez la route depuis un nœud Tailscale qui peut joindre Plex :

```bash
sudo tailscale up --advertise-routes=192.168.50.0/24
```

Puis vérifiez l’accessibilité depuis l’hôte du movies server :

```bash
curl http://192.168.50.10:32400/identity
```

Notes :

- le navigateur n’a pas besoin d’un accès réseau direct à Plex
- le processus movies server doit pouvoir joindre `plex.base_url`
- un reverse proxy ou un nom MagicDNS pour l’UI ne rend pas Plex joignable à lui seul

---

## Stratégie De Cache

### Cache D’Images

Les vignettes, images de prévisualisation et affiches Plex sont servies avec des en-têtes de cache immuables de longue durée.

### Cache Des Métadonnées

Les instantanés de métadonnées de la galerie sont mis en cache dans IndexedDB avec un stockage borné :

- TTL d’un jour
- jusqu’à 8 enregistrements d’instantanés
- jusqu’à environ 18 Mo de taille totale estimée
- éviction des entrées plus anciennes lorsque les limites sont dépassées

Chaque instantané en cache stocke :

- le `catalogStatus` du serveur
- le cache de liste des dossiers
- les `videos` chargées
- les compteurs de pagination comme `serverTotal`, `serverOffset` et `serverExhausted`

L’éviction est opportuniste plutôt que planifiée :

- les entrées expirées sont supprimées à la lecture ou lors d’un nettoyage ultérieur
- le nettoyage s’exécute après l’enregistrement de nouveaux instantanés
- la pression de stockage du navigateur ou l’effacement manuel des données du site peut aussi supprimer les données IndexedDB

---

## Comportement Du Scan

Le scan du catalogue est conçu pour rester incrémental en coût même s’il parcourt toujours chaque racine configurée.

Comportement actuel :

- les fichiers inchangés réutilisent les signatures `mtime + size` mises en cache
- les scans périodiques ne trient plus la liste complète des chemins avant traitement
- les fichiers supprimés sont retirés du catalogue en mémoire et de l’index persistant
- les fichiers supprimés déclenchent aussi le nettoyage des vignettes et aperçus générés
- les sauvegardes d’index réutilisent les données de signature de fichier mises en cache au lieu de refaire un stat sur chaque fichier

Ce que le scan fait encore :

- il parcourt les racines médias configurées pour détecter les fichiers ajoutés, modifiés et supprimés
- il met en file la génération des aperçus lorsque les images de prévisualisation sont absentes

Ce qu’il ne fait pas :

- il ne calcule pas de checksum sur les gros fichiers médias pendant les scans périodiques
- il ne régénère pas les vignettes ni les métadonnées pour les fichiers inchangés sauf si les artefacts en cache manquent

### Forcer Un Rescan Complet

Utilisez :

```text
/rescan?full=1
```

Utile lorsque :

- quelqu’un a supprimé manuellement le dossier de cache des vignettes ou aperçus
- vous soupçonnez que le manifeste de scan sauvegardé est obsolète
- vous voulez forcer une revalidation complète de l’état dérivé du scan

### Vérifier L’État Du Scan

```bash
curl -s http://localhost:9245/api/status | python3 -m json.tool
```

Si vous servez l’application sous `/movie/`, utilisez le chemin préfixé.

### Déclencher Un Rescan

Rescan incrémental normal :

```bash
curl -s http://localhost:9245/rescan | python3 -m json.tool
```

Rescan complet forcé :

```bash
curl -s "http://localhost:9245/rescan?full=1" | python3 -m json.tool
```

### Interface De Rescan

Le bouton `Rescan` ouvre une boîte de dialogue d’action au lieu de démarrer immédiatement un scan incrémental.

Actions disponibles :

- `Rescan` : scan incrémental des fichiers nouveaux ou modifiés
- `Full Scan` : efface l’état de scan sauvegardé et force une revalidation complète des métadonnées
- `Refresh Database` : efface les instantanés IndexedDB du navigateur et recharge des données de catalogue fraîches

### Récupération D’Un Montage Manquant

Si `mount_script` est configuré et qu’une requête média atteint un dossier manquant, le serveur :

1. détecte que le dossier parent n’existe pas
2. invoque une fois le script de montage configuré
3. revérifie le chemin cible
4. ne renvoie `Media folder is not mounted` avec HTTP 404 que si le dossier reste indisponible

Le frontend traite les 404 de lecture comme terminales pour cette tentative et affiche un message de nouvelle tentative au lieu de marteler le serveur en boucle.

---

## Notes De Développement Frontend

L’application charge actuellement `movies.js` directement depuis `index.html`, donc les changements frontend prennent effet sans reconstruire `movies.min.js`.

---

## Mode Privé

- les dossiers privés sont masqués tant que l’appareil n’est pas autorisé
- l’état de déverrouillage est lié à un ID d’appareil
- les appareils approuvés sont stockés côté serveur
- `passcode.py` peut faire tourner le code secret du mode privé et effacer les approbations

Exemple :

```bash
python3 passcode.py mynewpasscode
```

---

## Fichiers Générés

Ces fichiers sont générés à l’exécution et ne doivent pas être commités :

- `movies_config.json`
- `movies_state.json`
- `movies_auth_state.json`
- `movies_catalog_index.json`
- `cache/`

---

## Dépannage

### Les Changements D’UI N’Apparaissent Pas

- actualisez la page normalement d’abord
- si le bundle JS a changé, confirmez que `index.html` référence la version attendue

### La Lecture Directe Privée Échoue

- déverrouillez à nouveau le mode privé afin que le cookie `movies_device_id` soit rafraîchi

### La Lecture Plex Échoue Mais La Lecture Directe Fonctionne

- vérifiez que l’hôte du movies server peut joindre `plex.base_url`
- vérifiez que Plex est activé dans la configuration
- vérifiez que le token configuré est valide

### La Lecture Directe Échoue Mais Plex Fonctionne

- le conteneur ou codec n’est probablement pas sûr pour la lecture native du navigateur sur cet appareil
- gardez Plex activé pour ces fichiers, ou forcez le chemin de compatibilité via le transcodage local ou Plex

### Le Transcodage Local Ne Fonctionne Pas

- vérifiez que `ffmpeg` et `ffprobe` sont installés
- vérifiez que `on_demand_transcode` est activé
- vérifiez que le fichier source fait partie des conteneurs actuellement pris en charge : `.mkv` ou `.ts`

---

## Licence

Ce dépôt ne déclare actuellement aucune licence logicielle. Ajoutez-en une explicitement si vous prévoyez de le redistribuer.
