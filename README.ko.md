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
  <p><strong>초경량, 프라이버시 모드 🔐, 크로스 디바이스, 스마트 스트리밍</strong></p>
  <p>앱이 필요 없습니다. 서버 설치가 간단하고, 모바일 친화적인 화면으로 어디서나 NAS에 연결할 수 있으며, 필요하면 Plex 통합도 사용할 수 있습니다</p>
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



> 무거운 의존성 없이, 모든 것이 투명합니다. Flask, Waitress, `ffmpeg`로 구성된 경량 자체 호스팅 영화 브라우저 및 스트리밍 서버이며, 호환성 중심 재생을 위해 선택적으로 _`Plex`_ 통합을 사용할 수 있습니다.

---

![Screenshot 2026-03-22 at 9 39 12 PM](https://github.com/user-attachments/assets/124f21b7-71b0-46fc-9d76-c73f700c25f3)

---

## ✨ 왜 사용할까

Cat Theatre는 의도적으로 가볍게 설계되었습니다.

- 🩷 _원격 액세스_ 를 위해 Plex 구독 💰 이 필요하지 않습니다
- ✅ Python 의존성이 작음
- ✅ 데이터베이스가 필요 없음
- ✅ 파일 시스템 중심 카탈로그 구성
- ✅ 🖥️ 데스크톱, 📱 모바일, 태블릿과 호환
- ✅ OS 전용 watcher에 의존하지 않고 이식 가능한 폴링 기반 스캔 흐름 사용
- 🔶 핵심 재생에 필수인 대신 Plex 통합을 선택적 계층으로 추가

## ✴️ 기능

- 🎬 여러 폴더에 분산된 로컬 / NAS 미디어 라이브러리
- 🌄 썸네일 / 포스터 및 미리보기 프레임 생성
- 🔐 기기 기반으로 잠금 해제되는 비공개 폴더
- 🔗 `http://192.168.1.100/movie/` 같은 경로 프리픽스 아래 리버스 프록시 배포 지원
- 📽️ 혼합 재생 전략: 직접 재생, `.mkv`와 `.ts`용 내장 로컬 트랜스코딩, 또는 Plex 기반 HLS 프록시. 미디어별로 쉽게 전환 가능
- 🌐 브라우저 이미지 캐시와 IndexedDB 메타데이터 캐시

---
→ 원라이너로 설치:
```
curl -fsSL https://raw.githubusercontent.com/daocha/plex-cat-theatre/main/install.sh | bash
```
---

## 🟢 요구 사항

### Python 3.9 이상

현재 Python 패키지:

- `Flask`
- `waitress`

### 메타데이터 분석, 미리보기, 썸네일, 로컬 트랜스코딩에 필요한 시스템 바이너리:

- `ffmpeg`
- `ffprobe`

사용 가능 여부 확인:

```bash
which ffmpeg
which ffprobe
```

---

## 🚀 빠른 시작


### → 옵션 A: 원라이너로 설치:
```
curl -fsSL https://raw.githubusercontent.com/daocha/plex-cat-theatre/main/install.sh | bash
```

### → 옵션 B: pip로 PyPI에서 설치

```bash
pip install plex-cat-theatre
plex-cat-theatre-init
plex-cat-theatre --config ~/movies_config.json
```

### → 옵션 C: 권장 시작 방법

```bash
git clone https://github.com/daocha/plex-cat-theatre
cd plex-cat-theatre
./startup.sh
```

이 부트스트랩 스크립트는 다음을 수행할 수 있습니다.

- 첫 실행 시 샘플 설정으로부터 `movies_config.json` 생성
- 로컬 `.venv` 생성
- Python 의존성을 해당 로컬 가상환경에 설치
- 필요할 때 설정 파일 기준의 `cache/thumbnails` 및 `logs` 폴더 생성
- `ffmpeg` 및 `ffprobe` 확인
- 선택적으로 비공개 모드 패스코드 해시 생성 지원
- 로컬 설정으로 서버 시작

아래의 수동 흐름도 계속 사용할 수 있습니다.

1. 샘플 설정을 복사합니다:

```bash
cp movies_config.sample.json movies_config.json
```

2. 환경에 맞게 `movies_config.json`을 수정합니다.

### 🌐 서버 시작:

```bash
# 옵션 A 또는 옵션 B를 따르는 경우 실행
plex-cat-theatre --config ~/movies_config.json

# 옵션 C를 따르는 경우 실행
python3 movies_server.py --config movies_config.json
```

화면 열기:

```text
http://localhost:9245
```
### 🔑 패스코드 변경
```bash
# 옵션 A 또는 옵션 B를 따르는 경우 실행
plex-cat-theatre-passcode newpasscode

# 옵션 C를 따르는 경우 실행
python3 passcode.py newpasscode
```
- 비공개 폴더는 기기가 승인되기 전까지 숨겨집니다
- 잠금 해제 상태는 기기 ID에 연결됩니다
- 승인된 기기는 서버 측에 저장됩니다
- 이 스크립트로 비공개 모드 패스코드를 교체하고 승인 상태를 초기화할 수 있습니다

---

## 🗂️ 프로젝트 구조

- `movies_server.py`: Flask 엔트리포인트와 라우트 연결
- `movies_server_core.py`: 인증, 설정, 쿠키, 마운트 경로 처리를 위한 공용 서버 헬퍼
- `movies_catalog.py`: 카탈로그 스캔, 썸네일 생성, 자막 추출, 로컬 트랜스코드 헬퍼
- `movies_server_plex.py`: Plex 어댑터, 포스터 / 자막 매핑, Plex HLS 프록시
- `movies.js`: 프런트엔드 소스
- `movies.min.js`: 최소화된 프런트엔드 번들
- `movies.css`: 갤러리와 플레이어 스타일
- `passcode.py`: 비공개 모드 패스코드 회전을 위한 헬퍼

---

## ⚙️ 설정

샘플 설정은 의도적으로 정리되어 있어 다음 값이 포함되지 않습니다.

- 실제 파일 시스템 경로
- 실제 Plex 토큰
- 실제 해시된 패스코드
- 기기별 값

### 📍 중요한 필드

<table>
  <tr>
    <td width="200"><code>root</code></td>
    <td>스캔할 미디어 루트(여러 폴더 지원)</td>
  </tr>
  <tr>
    <td><code>thumbs_dir</code></td>
    <td>썸네일과 미리보기 프레임 저장 디렉터리. 기본값: <code>./cache/thumbnails</code></td>
  </tr>
  <tr>
    <td><code>private_folder</code></td>
    <td>비공개로 취급할 폴더 접두사. 예: <code>Personal</code>. <code>Personal</code> 폴더 아래의 모든 항목은 UI에서 잠금 해제하기 전까지 잠깁니다.</td>
  </tr>
  <tr>
    <td><code>private_passcode</code></td>
    <td>비공개 모드 패스코드 해시입니다. 평문으로 직접 수정하면 안 됩니다. 변경하려면 <code>패스코드 변경</code> 섹션을 참고하세요.</td>
  </tr>
  <tr>
    <td><code>mount_script</code></td>
    <td>[선택 사항] 미디어 재생 중 누락된 폴더를 만났고 그 원인이 마운트 해제일 때 실행할 명령입니다.</td>
  </tr>
  <tr>
    <td><code>transcode</code></td>
    <td>`.mkv`, `.ts` 같은 소스 컨테이너에 대해 카탈로그 측 백그라운드 트랜스코드 워커를 활성화합니다. 이 경우 원본 라이브러리 옆에 별도 트랜스코드 sidecar 파일이 생성될 수 있으므로, 특히 Plex 통합을 켠 경우에는 보통 <code>false</code>로 두는 것이 좋습니다. 기본값: <code>false</code></td>
  </tr>
  <tr>
    <td><code>auto_scan_on_start</code></td>
    <td>시작 시 미디어를 다시 스캔합니다. 기본값: <code>false</code></td>
  </tr>
  <tr>
    <td><code>on_demand_transcode</code></td>
    <td>소스 컨테이너에 대한 런타임 플레이어 트랜스코딩을 활성화합니다. 가능하면 하드웨어 인코딩을 우선 사용하고, 필요하면 소프트웨어 인코딩으로 폴백합니다. 기본값: <code>true</code></td>
  </tr>
  <tr>
    <td><code>on_demand_hls</code></td>
    <td>소스 컨테이너에 대한 내장 HLS 플레이리스트를 활성화합니다. 기본값: <code>true</code></td>
  </tr>
  <tr>
  <td><code>enable_plex_server</code></td>
  <td>📍 [선택 사항] Plex 통합을 활성화합니다. 기본값: <code>false</code>. 활성화하기 전에 Plex Server가 올바르게 설치되고 구성되었는지 확인하세요.<br> 이 서버는 기본 자막을 지원하지만, 자막을 자동으로 가져오려면 Plex를 사용하는 편이 더 낫습니다.
  <br> 더 나은 온디맨드 트랜스코딩 경험을 원한다면 원활한 미디어 스트리밍을 위해 Plex server 설치를 강력히 권장합니다.<br>
  Plex server가 없어도 이 서버는 잘 동작하지만 다음 사항에 유의하세요.
  <br>→ 기기에서 직접 재생 가능한 미디어는 탐색 기능이 잘 동작합니다.
  <br>→ 기기에서 직접 재생할 수 없는 미디어, 예를 들어 <code>DTS 오디오가 포함된 h.265</code>(AAC 또는 MP3가 포함된 h.265는 영향 없음), <code>.mkv</code>, <code>.ts</code>, <code>.wmv</code>는 실시간 트랜스코딩이 가능하지만 탐색 기능이 없을 수 있습니다.
  </td>
  </tr>
  <tr>
    <td><code>plex.base_url</code></td>
    <td>Plex 서버 기본 URL</td>
  </tr>
  <tr>
    <td><code>plex.token</code></td>
    <td>Plex 토큰</td>
  </tr>
  <tr>
    <td><code>debug_enabled</code></td>
    <td>내장 디버그 오버레이 표시</td>
  </tr>
  <tr>
    <td><code>direct_playback</code></td>
    <td><code>enabled</code>와 <code>audio_whitelist</code>를 포함하는 객체입니다. <code>enabled=true</code>이면 트랜스코딩 없이 네이티브 플레이어로 미디어를 재생할 수 있습니다(빠름). 기본 설정 사용을 권장합니다.</td>
  </tr>
</table>

### 최소 로컬 전용 예시

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

### Plex 통합 예시

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

### 🅿️ Plex 스캔 동작

- Plex 포스터를 사용할 수 있으면 로컬 포스터 썸네일 생성은 건너뜁니다
- 기존에 캐시된 로컬 썸네일은 계속 재사용할 수 있습니다
- 미리보기 프레임 생성은 계속 활성화됩니다
- Plex 통합은 여전히 선택 사항이며, 로컬 전용 모드도 계속 사용할 수 있습니다

### → Plex 토큰 얻는 방법

#### 방법 1: 기존 Plex Web 세션

1. Plex Web을 열고 로그인합니다.
2. 브라우저 개발자 도구를 엽니다.
3. 네트워크 탭으로 이동합니다.
4. 페이지를 새로고침합니다.
5. Plex 서버로 전송되는 요청 하나를 확인합니다.
6. URL 또는 헤더에서 `X-Plex-Token`을 찾습니다.

#### 방법 2: 브라우저 저장소

확인할 항목:

- 로컬 저장소 (`Local Storage`)
- 세션 저장소 (`Session Storage`)
- DevTools의 요청 URL 및 헤더

#### 방법 3: 로컬 직접 요청

같은 기기에서 이미 Plex Web 세션이 활성화되어 있다면, DevTools에서 Plex 요청을 확인하고 다음을 찾으세요:

```text
X-Plex-Token=...
```

‼️ 보안 메모:

- Plex 토큰은 비밀번호처럼 취급하세요
- git에 커밋하지 마세요
- `movies_config.json`에만 보관하세요

---

## 🎥 재생 모드

### 1. 네이티브 직접 재생

`.mp4`, `.m4v`, `.webm`처럼 브라우저 안전 파일에 사용됩니다.

동작:

- `/video/<id>`에서 로컬 파일을 직접 제공합니다
- HTTP range request를 지원합니다
- 브라우저가 파일을 네이티브로 재생할 수 있으면 트랜스코딩 오버헤드를 피합니다

적합한 경우:

- MP4 / H.264 계열 파일
- 브라우저가 이미 직접 재생을 지원하는 파일
- 오디오 코덱이 direct-play 화이트리스트와 일치하는 파일

### 2. Plex 없이 내장 로컬 트랜스코딩

Plex가 비활성화되어 있거나 완전 로컬 모드로 유지하고 싶을 때 사용하는 폴백 경로입니다.

현재 구현:

- `.mkv`와 `.ts`를 `/hls/<id>/index.m3u8`에서 로컬 HLS로 제공할 수 있습니다
- 같은 파일을 `/video/<id>?fmp4=1`에서 fragmented MP4로 스트리밍할 수도 있습니다
- HLS 세그먼트는 `ffmpeg`로 온디맨드 생성됩니다
- 먼저 하드웨어 인코딩을 시도하고 필요하면 `libx264`로 폴백합니다
- fMP4 출력은 `libx264`와 AAC로 생성됩니다

### 3. Plex 기반 재생

Plex 통합이 활성화되면:

- 프런트엔드는 호환성 민감한 재생에 `plex_stream_url`을 사용할 수 있습니다
- Plex가 상위 HLS 플레이리스트를 생성합니다
- 이 서버가 플레이리스트를 다시 쓰고 중첩 플레이리스트와 세그먼트 요청을 프록시합니다
- 브라우저는 여전히 Plex가 아니라 이 앱과 통신합니다

적합한 경우:

- 코덱 또는 컨테이너 지원이 약한 기기에서 MKV 또는 TS 콘텐츠를 재생할 때
- Plex 자막 선택 또는 스트림 정규화가 더 적합한 경우

### 재생 선택 정책

- 브라우저 안전 파일 중 오디오 코덱이 `direct_playback.audio_whitelist`와 일치하면 직접 재생이 우선입니다
- `.mkv`, `.ts`, HLS, fMP4 또는 지원되지 않는 오디오 코덱에는 Plex가 계속 우선입니다
- iOS 네이티브 HLS 폴백 타이밍은 더 길어서 Plex 스트림이 준비될 시간을 줍니다

### 기본 재생 로직

- 직접 URL이 실제 파일 경로이고 오디오 코덱이 화이트리스트에 안전하면 `.mp4`, `.m4v`, `.webm`, `.avi`는 `Direct`를 우선합니다
- 이런 브라우저 안전 확장자 중 하나에서 오디오 코덱 메타데이터가 없어도 앱은 여전히 `Direct`를 선호합니다
- `.mkv`, `.ts`, HLS / fMP4 직접 URL, 또는 알려진 오디오 코덱이 화이트리스트 밖인 파일은 `Plex`를 우선합니다
- Plex 매칭이 없으면 앱은 `Direct`로 폴백합니다

---

## 인증 모델

앱은 요청 유형에 따라 다른 전송 방식을 사용합니다.

- API 요청은 `X-Device-Id` 헤더를 사용합니다
- HLS 및 Plex 프록시 요청은 `X-Device-Id` 헤더를 사용합니다
- 네이티브 직접 미디어 요청은 `movies_device_id` 쿠키 폴백을 사용합니다

이렇게 나누는 이유는 네이티브 `<video src="...">` 요청에 임의의 커스텀 헤더를 붙일 수 없기 때문입니다.

---

## 리버스 프록시 및 컨텍스트 경로 지원

앱은 다음과 같은 서브패스 배포를 지원합니다.

- `https://example.com/movie/`
- `https://example.com/cinema/`

라우팅은 다음 항목에 대해 현재 마운트 프리픽스를 유지합니다.

- 직접 미디어
- 로컬 HLS
- Plex HLS 프록시 요청
- 포스터 및 자막 자산

---

## Tailscale을 통한 원격 Plex 액세스

커스텀 UI는 원격에서 접근 가능하지만 Plex는 사설 LAN에서만 접근 가능한 경우, movies server 호스트는 Plex 백엔드에 직접 도달할 수 있어야 합니다.

### 같은 호스트

```json
"plex": {
  "base_url": "http://127.0.0.1:32400"
}
```

### 다른 LAN 장비의 Plex

Plex에 도달할 수 있는 Tailscale 노드에서 경로를 광고합니다:

```bash
sudo tailscale up --advertise-routes=192.168.50.0/24
```

그다음 movies server 호스트에서 연결 가능 여부를 확인합니다:

```bash
curl http://192.168.50.10:32400/identity
```

📌 참고:

- 브라우저가 Plex에 직접 네트워크로 접근할 필요는 없습니다
- movies server 프로세스는 `plex.base_url`에 도달할 수 있어야 합니다
- UI의 리버스 프록시나 MagicDNS 이름만으로 Plex가 자동으로 접근 가능해지지는 않습니다

---

## 💾 캐싱 전략

### 이미지 캐싱

썸네일, 미리보기 프레임, Plex 포스터 이미지는 장기 immutable cache header와 함께 제공됩니다.

### 메타데이터 캐싱

갤러리 메타데이터 스냅샷은 제한된 저장 공간으로 IndexedDB에 캐시됩니다:

- 1일 TTL
- 최대 8개 스냅샷 레코드
- 총 추정 크기 약 18MB까지
- 한도를 넘으면 오래된 항목부터 제거

각 캐시 스냅샷에는 다음이 저장됩니다:

- 서버 `catalogStatus`
- 폴더 목록 캐시
- 로드된 `videos`
- `serverTotal`, `serverOffset`, `serverExhausted` 같은 페이지네이션 카운터

제거는 주기적 작업이 아니라 기회가 있을 때 수행됩니다:

- 만료된 항목은 읽을 때 또는 이후 정리 시 제거됩니다
- 새 스냅샷 저장 후 정리가 실행됩니다
- 브라우저 저장 공간 압박이나 사이트 데이터 수동 삭제로 IndexedDB 데이터가 제거될 수도 있습니다

---

## 🔍 스캔 동작

카탈로그 스캔은 여전히 각 루트를 순회하지만 비용은 점진적으로 유지되도록 설계되었습니다.

현재 동작:

- 변경되지 않은 파일은 캐시된 `mtime + size` 시그니처를 재사용합니다
- 주기적 스캔은 처리 전에 전체 경로 목록을 더 이상 정렬하지 않습니다
- 삭제된 파일은 메모리 카탈로그와 영속 인덱스에서 제거됩니다
- 삭제된 파일은 생성된 썸네일과 미리보기 산출물 정리도 유발합니다
- 인덱스 저장은 각 파일에 다시 `stat`를 호출하지 않고 캐시된 파일 시그니처 데이터를 재사용합니다

스캔이 여전히 하는 일:

- 구성된 미디어 루트를 순회해 추가, 변경, 삭제된 파일을 감지합니다
- 미리보기 이미지가 없으면 미리보기 생성을 큐에 넣습니다

스캔이 하지 않는 일:

- 주기적 스캔 중 큰 미디어 파일의 체크섬을 계산하지 않습니다
- 캐시된 산출물이 존재하는 한 변경되지 않은 파일의 썸네일이나 메타데이터를 다시 생성하지 않습니다

### → 재스캔 실행

일반 증분 재스캔:

```bash
curl -s http://localhost:9245/rescan | python3 -m json.tool
```

강제 전체 재스캔:

```bash
curl -s "http://localhost:9245/rescan?full=1" | python3 -m json.tool
```

### → 재스캔 화면

`Rescan` 버튼은 즉시 증분 스캔을 시작하지 않고, 먼저 작업 대화상자를 엽니다.

사용 가능한 작업:

- `Rescan`: 새 파일 또는 변경된 파일에 대한 증분 스캔
- `Full Scan`: 저장된 스캔 상태를 지우고 전체 메타데이터 재검증을 강제
- `Refresh Database`: 브라우저 IndexedDB 스냅샷을 지우고 새 카탈로그 데이터를 다시 로드

### ⛓️‍💥 누락된 마운트 복구

이 기능은 일부 NAS가 자동 절전 모드로 설정되어 있어 일부 운영체제에서 SMB 마운트가 자동 해제되는 경우를 위한 것입니다.

`mount_script`가 설정되어 있고 미디어 요청이 누락된 폴더를 만났다면 서버는:

1. 상위 폴더가 존재하지 않음을 감지합니다
2. 설정된 마운트 스크립트를 한 번 호출합니다
3. 대상 경로를 다시 확인합니다
4. 폴더가 여전히 없을 때만 `Media folder is not mounted`와 함께 HTTP 404를 반환합니다

프런트엔드는 재생 중 404를 해당 시도의 최종 실패로 취급하고, 서버를 반복적으로 두드리는 대신 재시도 메시지를 표시합니다.

---

## 📄 생성되는 파일

이 파일들은 런타임에 생성되며 커밋하면 안 됩니다.

- `movies_config.json`
- `movies_state.json`
- `movies_auth_state.json`
- `movies_catalog_index.json`
- `cache/`

---

## 🛠️ 문제 해결


### → 디버그 오버레이

`movies_config.json`에서 `debug_enabled`를 켜면 오른쪽 아래에 상시 디버그 오버레이를 표시할 수 있습니다.

패널에는 다음이 표시됩니다:

- 서버가 직접 재생과 Plex 중 무엇을 선호하는지
- 구성된 direct-play 오디오 화이트리스트
- 현재 재생 후보와 비디오 ID
- 최근 스캔 진행 메트릭

현재 활성 설정 값 확인:

```bash
curl -s http://localhost:9245/api/config | python3 -m json.tool
```

### → 화면 변경이 보이지 않음

- 현재 앱은 `index.html`에서 `movies.js`를 직접 로드하므로 프런트엔드 변경은 `movies.min.js`를 다시 빌드하지 않아도 적용됩니다.
- 먼저 일반 새로고침을 해보세요
- JS 번들이 변경되었다면 `index.html`이 예상한 번들 버전을 참조하는지 확인하세요

### → 비공개 직접 재생이 실패함

- 비공개 모드를 다시 잠금 해제해 `movies_device_id` 쿠키를 새로 고치세요

### → Plex 재생은 실패하지만 직접 재생은 됨

- movies server 호스트가 `plex.base_url`에 도달할 수 있는지 확인하세요
- 설정에서 Plex가 활성화되어 있는지 확인하세요
- 구성한 토큰이 유효한지 확인하세요

### → 직접 재생은 실패하지만 Plex는 됨

- 해당 기기에서는 컨테이너나 코덱이 브라우저 네이티브 재생에 안전하지 않을 가능성이 큽니다
- 그런 파일은 Plex를 계속 사용하거나, 로컬 트랜스코딩 / Plex를 통해 호환 경로를 강제하세요

### → 로컬 트랜스코딩이 동작하지 않음

- `ffmpeg`와 `ffprobe`가 설치되어 있는지 확인하세요
- `on_demand_transcode`가 활성화되어 있는지 확인하세요
- 소스 파일이 현재 지원되는 컨테이너 `.mkv` 또는 `.ts`인지 확인하세요

---

## 📦 릴리스 버전 규칙

패키지 버전은 Git 태그에서 파생됩니다.

- TestPyPI / testing: `2026.3.26.dev1` 같은 개발 버전 사용
- PyPI 프리릴리스: `2026.3.26rc1` 같은 릴리스 후보 사용
- PyPI 안정판: `2026.3.26` 같은 안정 버전 사용
- Git 태그는 `v2026.3.26.dev1`, `v2026.3.26rc1`, `v2026.3.26` 형식이어야 합니다
  
---

## ©️ 라이선스

이 프로젝트는 MIT License로 배포됩니다. 공개하거나 재배포할 때는 MIT 텍스트가 포함된 `LICENSE` 파일을 추가하세요.
