# Cat Theatre Movies Server

> Flask, Waitress, `ffmpeg`로 구성된 경량 자체 호스팅 영화 브라우저 및 스트리밍 서버이며, 호환성 중심 재생을 위해 선택적으로 _`Plex`_ 통합을 사용할 수 있습니다.

---

![Screenshot 2026-03-22 at 9 39 12 PM](https://github.com/user-attachments/assets/124f21b7-71b0-46fc-9d76-c73f700c25f3)

---

**언어**

[English](./README.md) | [简体中文](./README.zh-CN.md) | [繁體中文（香港）](./README.zh-HK.md) | [繁體中文（台灣）](./README.zh-TW.md) | [Français](./README.fr.md) | `한국어` | [日本語](./README.ja.md) | [Deutsch](./README.de.md) | [ไทย](./README.th.md) | [Tiếng Việt](./README.vi.md) | [Nederlands](./README.nl.md)

---

## 개요

Cat Theatre는 의도적으로 가볍게 설계되었습니다.

- Python 의존성이 작음
- 데이터베이스가 필요 없음
- 파일 시스템 중심 카탈로그 구성
- OS 전용 watcher에 의존하지 않고 이식 가능한 폴링 기반 스캔 흐름 사용
- 핵심 재생에 필수인 대신 Plex 통합을 선택적 계층으로 추가

다음과 같은 환경을 위해 설계되었습니다.

- 하나 이상의 폴더에 분산된 로컬 미디어 라이브러리
- 썸네일과 미리보기 프레임 생성
- 기기 기반 비공개 폴더 접근 제어
- `/movie/` 같은 경로 프리픽스로 리버스 프록시 뒤에 배포
- 혼합 재생 전략: 직접 파일 재생, 내장 로컬 트랜스코딩, Plex 기반 HLS

---

## 기능

- 다중 루트 미디어 스캔
- 포스터 썸네일 및 미리보기 프레임 생성
- 기기별 잠금 해제가 있는 비공개 폴더
- 브라우저 안전 형식에 대한 네이티브 직접 재생
- 활성화 시 `.mkv` 및 `.ts`에 대한 내장 로컬 트랜스코딩
- 재생, 포스터, 자막, HLS 프록시를 위한 Plex 통합
- 리버스 프록시를 위한 컨텍스트 경로 인식 라우팅
- 브라우저 이미지 캐시와 IndexedDB 메타데이터 캐시

### UX 및 재생 참고

- 내장 디버그 패널은 오른쪽 아래에 있으며 가장 가까운 가장자리로 이동할 수 있습니다
- 재생은 현재 파일과 기기에 더 안전한 경로를 자동으로 우선 선택합니다
- 수동 Direct/Plex 오버라이드는 비디오별로 IndexedDB에 저장됩니다
- 캐시된 썸네일과 메타데이터는 브라우저 저장소 한도 내에 유지됩니다

---

## 요구 사항

### Python

```bash
pip install -r requirements.txt
```

현재 Python 패키지:

- `Flask`
- `waitress`

### 시스템 바이너리

메타데이터 분석, 미리보기, 썸네일, 로컬 트랜스코딩에 필요합니다.

- `ffmpeg`
- `ffprobe`

사용 가능 여부 확인:

```bash
which ffmpeg
which ffprobe
```

---

## 빠른 시작

권장 시작 방법:

```bash
./startup.sh
```

이 부트스트랩 스크립트는 다음을 수행할 수 있습니다.

- 첫 실행 시 샘플 설정으로부터 `movies_config.json` 생성
- 로컬 `.venv` 생성
- Python 의존성을 해당 로컬 가상환경에 설치
- `ffmpeg` 및 `ffprobe` 확인
- 선택적으로 비공개 모드 비밀번호 해시 생성 지원
- 로컬 설정으로 서버 시작

아래의 수동 절차도 계속 사용할 수 있습니다.

1. 샘플 설정을 복사합니다.

```bash
cp movies_config.sample.json movies_config.json
```

2. 환경에 맞게 `movies_config.json`을 수정합니다.

3. 서버를 시작합니다.

```bash
python3 movies_server.py --config movies_config.json
```

4. UI를 엽니다.

```text
http://localhost:9245
```

앱을 `/movie/` 같은 프리픽스로 리버스 프록시 뒤에 배포했다면 프리픽스가 포함된 URL을 여십시오.

---

## 프로젝트 구조

- `movies_server.py`: Flask 진입점 및 라우팅 연결
- `movies_server_core.py`: 인증, 설정, 쿠키, 마운트 경로 처리를 위한 공용 서버 헬퍼
- `movies_catalog.py`: 카탈로그 스캔, 썸네일 생성, 자막 추출, 로컬 트랜스코딩 헬퍼
- `movies_server_plex.py`: Plex 어댑터, 포스터/자막 매핑, Plex HLS 프록시
- `movies.js`: 프론트엔드 소스
- `movies.min.js`: 압축된 프론트엔드 번들
- `movies.css`: 갤러리 및 플레이어 스타일
- `passcode.py`: 비공개 모드 비밀번호를 교체하는 헬퍼

---

## 설정

샘플 설정은 의도적으로 정리되어 있어 다음을 포함하지 않습니다.

- 실제 파일 시스템 경로
- 실제 Plex 토큰
- 실제 비밀번호
- 기기별 값

### 중요한 필드

- `root`: 스캔할 미디어 루트
- `thumbs_dir`: 썸네일 및 미리보기 프레임 디렉터리
- `private_folder`: 비공개로 취급할 폴더 프리픽스
- `private_passcode`: 비공개 모드 비밀번호 해시
- `mount_script`: 재생 중 누락된 미디어 폴더를 만났을 때 호출할 선택적 명령
- `transcode`: `.mkv`, `.ts` 같은 소스 컨테이너에 대해 카탈로그 측 백그라운드 트랜스코드 워커를 활성화하며, 이는 미디어 라이브러리 옆에 별도의 트랜스코드 산출 파일을 만들 수 있으므로 보통 `false`로 두는 것이 좋고 Plex 통합 시에는 특히 그렇습니다
- `auto_scan_on_start`: 시작 시 미디어 다시 스캔
- `on_demand_transcode`: 플레이어 런타임 중 소스 컨테이너에 대한 트랜스코딩을 활성화하며, 가능하면 하드웨어 인코딩을 우선 사용하고 필요 시 소프트웨어 인코딩으로 폴백합니다
- `on_demand_hls`: 소스 컨테이너에 대한 내장 HLS 플레이리스트 활성화
- `enable_plex_server`: Plex 통합 활성화
- `plex.base_url`: Plex 서버 기본 URL
- `plex.token`: Plex 토큰
- `debug_enabled`: 내장 디버그 오버레이 표시
- `direct_playback`: `enabled`와 `audio_whitelist`를 포함하는 객체

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

### Plex 스캔 동작

- Plex 포스터를 사용할 수 있으면 로컬 포스터 썸네일 생성을 건너뜁니다
- 기존의 로컬 캐시 썸네일은 계속 재사용할 수 있습니다
- 미리보기 프레임 생성은 계속 활성화됩니다
- Plex 통합은 선택 사항이며 로컬 전용 모드도 계속 동작합니다

### Plex 토큰 얻는 방법

#### 방법 1: 기존 Plex Web 세션 사용

1. Plex Web을 열고 로그인합니다.
2. 브라우저 개발자 도구를 엽니다.
3. Network 탭으로 이동합니다.
4. 페이지를 새로고침합니다.
5. Plex 서버로 전송된 요청 하나를 확인합니다.
6. URL 또는 헤더에서 `X-Plex-Token`을 찾습니다.

#### 방법 2: 브라우저 저장소

다음을 확인합니다.

- Local Storage
- Session Storage
- DevTools의 요청 URL 및 헤더

#### 방법 3: 직접 로컬 요청

같은 컴퓨터에서 이미 활성 Plex Web 세션이 있다면 DevTools에서 Plex 요청을 확인하고 다음을 찾습니다.

```text
X-Plex-Token=...
```

보안 참고:

- Plex 토큰은 비밀번호처럼 취급하십시오
- git에 커밋하지 마십시오
- `movies_config.json`에만 보관하십시오

---

## 재생 모드

### 1. 네이티브 직접 재생

`.mp4`, `.m4v`, `.webm` 같은 브라우저 안전 파일에 사용됩니다.

동작:

- 로컬 파일을 `/video/<id>`에서 직접 제공합니다
- HTTP Range 요청을 지원합니다
- 브라우저가 파일을 네이티브로 재생할 수 있으면 트랜스코딩 오버헤드를 피합니다

적합한 경우:

- MP4/H.264 계열 파일
- 브라우저가 이미 직접 지원하는 파일
- 오디오 코덱이 direct-play 화이트리스트와 일치하는 파일

### 2. Plex 없이 사용하는 내장 로컬 트랜스코딩

이것은 Plex가 활성화되지 않았거나 의도적으로 완전 로컬 상태를 유지하고 싶을 때의 대체 경로입니다.

현재 구현:

- `.mkv`와 `.ts`는 `/hls/<id>/index.m3u8`에서 로컬 HLS로 노출할 수 있습니다
- 같은 파일은 `/video/<id>?fmp4=1`을 통해 fragmented MP4로도 스트리밍할 수 있습니다
- HLS 세그먼트는 `ffmpeg`로 필요 시 생성됩니다
- 하드웨어 인코딩을 먼저 시도한 뒤 `libx264`로 폴백할 수 있습니다
- fMP4 출력은 `libx264`와 AAC로 생성됩니다

### 3. Plex 기반 재생

Plex 통합이 활성화되면:

- 프론트엔드는 호환성 중심 재생을 위해 `plex_stream_url`을 사용할 수 있습니다
- Plex가 상위 HLS 플레이리스트를 생성합니다
- 이 서버는 플레이리스트를 다시 작성하고 중첩 플레이리스트 및 세그먼트 요청을 프록시합니다
- 브라우저는 여전히 Plex가 아니라 이 앱과 통신합니다

적합한 경우:

- 코덱 또는 컨테이너 지원이 약한 기기에서 MKV 또는 TS 콘텐츠를 재생할 때
- Plex의 자막 선택 또는 스트림 정규화를 선호할 때

### 재생 선택 정책

- 오디오 코덱이 `direct_playback.audio_whitelist`와 일치하는 브라우저 안전 파일은 직접 재생이 우선입니다
- `.mkv`, `.ts`, HLS, fMP4, 또는 지원되지 않는 오디오 코덱에는 Plex가 계속 우선입니다
- iOS 네이티브 HLS 폴백 타이밍은 Plex 스트림이 준비될 시간을 주기 위해 더 깁니다

### 기본 재생 로직

- 직접 URL이 실제 파일 경로이고 오디오 코덱이 화이트리스트 안전이면 `.mp4`, `.m4v`, `.webm`, `.avi`는 `Direct`를 우선합니다
- 이러한 브라우저 안전 확장자에서 오디오 코덱 메타데이터가 없더라도 앱은 여전히 `Direct`를 우선합니다
- `.mkv`, `.ts`, HLS/fMP4 직접 URL, 그리고 알려진 오디오 코덱이 화이트리스트 밖인 파일은 `Plex`를 우선합니다
- Plex 매칭이 없으면 앱은 `Direct`로 폴백합니다

---

## 디버그 오버레이

`movies_config.json`에서 `debug_enabled`를 활성화하면 오른쪽 아래에 항상 표시되는 디버그 오버레이를 유지할 수 있습니다.

패널에는 다음이 표시됩니다.

- 서버가 direct playback 또는 Plex 중 어느 쪽을 선호하는지
- 설정된 direct-play 오디오 화이트리스트
- 현재 재생 후보와 비디오 ID
- 최근 스캔 진행 지표

현재 설정 값을 확인하려면:

```bash
curl -s http://localhost:9245/api/config | python3 -m json.tool
```

앱을 `/movie/` 아래에서 서비스한다면 프리픽스가 포함된 경로를 사용하십시오.

---

## 인증 모델

앱은 요청 유형에 따라 서로 다른 전송 방식을 사용합니다.

- API 요청은 `X-Device-Id` 헤더를 사용합니다
- HLS 및 Plex 프록시 요청은 `X-Device-Id` 헤더를 사용합니다
- 네이티브 직접 미디어 요청은 폴백으로 `movies_device_id` 쿠키를 사용합니다

이렇게 분리한 이유는 네이티브 `<video src="...">` 요청이 임의의 사용자 정의 헤더를 붙일 수 없기 때문입니다.

---

## 리버스 프록시 및 컨텍스트 경로 지원

앱은 다음과 같은 하위 경로 배포를 지원합니다.

- `https://example.com/movie/`
- `https://example.com/cinema/`

라우팅은 다음 항목에 대해 활성 마운트 프리픽스를 유지합니다.

- 직접 미디어
- 로컬 HLS
- Plex HLS 프록시 요청
- 포스터 및 자막 자산

---

## Tailscale을 통한 원격 Plex 접근

커스텀 UI는 원격으로 접근 가능하지만 Plex는 사설 LAN에서만 접근 가능하다면, movies server 호스트는 여전히 Plex 백엔드에 직접 접근할 수 있어야 합니다.

### 동일 호스트

```json
"plex": {
  "base_url": "http://127.0.0.1:32400"
}
```

### Plex가 다른 LAN 장비에 있는 경우

Plex에 도달할 수 있는 Tailscale 노드에서 경로를 광고합니다.

```bash
sudo tailscale up --advertise-routes=192.168.50.0/24
```

그런 다음 movies server 호스트에서 접근성을 확인합니다.

```bash
curl http://192.168.50.10:32400/identity
```

참고:

- 브라우저는 Plex에 직접 네트워크 접근이 필요하지 않습니다
- movies server 프로세스는 `plex.base_url`에 도달할 수 있어야 합니다
- UI용 리버스 프록시 또는 MagicDNS 이름만으로는 Plex가 접근 가능해지지 않습니다

---

## 캐싱 전략

### 이미지 캐싱

썸네일, 미리보기 프레임, Plex 포스터 이미지는 장기 immutable 캐시 헤더와 함께 제공됩니다.

### 메타데이터 캐싱

갤러리 메타데이터 스냅샷은 제한된 저장소와 함께 IndexedDB에 캐시됩니다.

- 1일 TTL
- 최대 8개의 스냅샷 레코드
- 총 추정 크기 약 18MB까지
- 한도를 넘으면 오래된 항목이 제거됨

각 캐시 스냅샷에는 다음이 저장됩니다.

- 서버 `catalogStatus`
- 폴더 목록 캐시
- 로드된 `videos`
- `serverTotal`, `serverOffset`, `serverExhausted` 같은 페이지네이션 카운터

제거는 스케줄 기반이 아니라 기회적입니다.

- 만료된 항목은 읽을 때 또는 이후 정리 시 제거됩니다
- 새 스냅샷 저장 후 정리가 실행됩니다
- 브라우저 저장소 압박 또는 수동 사이트 데이터 삭제로도 IndexedDB 데이터가 제거될 수 있습니다

---

## 스캔 동작

카탈로그 스캔은 여전히 각 설정 루트를 순회하지만 비용이 점진적으로 유지되도록 설계되었습니다.

현재 동작:

- 변경되지 않은 파일은 캐시된 `mtime + size` 서명을 재사용합니다
- 주기적 스캔은 처리 전에 전체 경로 목록을 더 이상 정렬하지 않습니다
- 삭제된 파일은 메모리 카탈로그와 저장된 인덱스에서 제거됩니다
- 삭제된 파일은 생성된 썸네일 및 미리보기 산출물 정리도 트리거합니다
- 인덱스 저장은 각 파일을 다시 stat하지 않고 캐시된 파일 서명 데이터를 재사용합니다

스캔이 여전히 하는 일:

- 설정된 미디어 루트를 순회하며 추가, 변경, 삭제된 파일을 감지합니다
- 미리보기 이미지가 없을 때 미리보기 생성을 큐에 넣습니다

하지 않는 일:

- 주기적 스캔 중 대용량 미디어 파일의 체크섬을 계산하지 않습니다
- 캐시 산출물이 누락되지 않는 한 변경되지 않은 파일의 썸네일이나 메타데이터를 재생성하지 않습니다

### 전체 재스캔 강제

사용:

```text
/rescan?full=1
```

다음 경우에 유용합니다.

- 누군가 썸네일 또는 미리보기 캐시 폴더를 수동으로 삭제했을 때
- 저장된 스캔 매니페스트가 오래되었다고 의심될 때
- 스캔 파생 상태 전체를 강제로 재검증하고 싶을 때

### 스캔 상태 확인

```bash
curl -s http://localhost:9245/api/status | python3 -m json.tool
```

앱을 `/movie/` 아래에서 서비스한다면 프리픽스가 포함된 경로를 사용하십시오.

### 재스캔 실행

일반 증분 재스캔:

```bash
curl -s http://localhost:9245/rescan | python3 -m json.tool
```

강제 전체 재스캔:

```bash
curl -s "http://localhost:9245/rescan?full=1" | python3 -m json.tool
```

### 재스캔 UI

`Rescan` 버튼은 즉시 증분 스캔을 시작하지 않고 작업 대화상자를 엽니다.

사용 가능한 작업:

- `Rescan`: 새 파일 또는 변경된 파일에 대한 증분 스캔
- `Full Scan`: 저장된 스캔 상태를 지우고 전체 메타데이터 재검증 강제
- `Refresh Database`: 브라우저 IndexedDB 스냅샷을 지우고 새 카탈로그 데이터를 다시 로드

### 누락된 마운트 복구

`mount_script`가 설정되어 있고 미디어 요청이 누락된 폴더를 만나면 서버는 다음을 수행합니다.

1. 상위 폴더가 존재하지 않음을 감지
2. 설정된 마운트 스크립트를 한 번 호출
3. 대상 경로를 다시 확인
4. 폴더가 여전히 사용할 수 없을 때만 HTTP 404와 함께 `Media folder is not mounted` 반환

프론트엔드는 재생 404를 해당 시도의 종료 상태로 취급하고 서버를 계속 두드리는 대신 재시도 메시지를 표시합니다.

---

## 프론트엔드 개발 참고

현재 앱은 `index.html`에서 `movies.js`를 직접 로드하므로 프론트엔드 변경은 `movies.min.js`를 다시 빌드하지 않아도 적용됩니다.

---

## 비공개 모드

- 비공개 폴더는 기기가 승인되기 전까지 숨겨집니다
- 잠금 해제 상태는 기기 ID에 연결됩니다
- 승인된 기기는 서버 측에 저장됩니다
- `passcode.py`는 비공개 모드 비밀번호를 교체하고 승인을 지울 수 있습니다

예시:

```bash
python3 passcode.py mynewpasscode
```

---

## 생성 파일

다음 파일은 런타임에 생성되며 커밋하면 안 됩니다.

- `movies_config.json`
- `movies_state.json`
- `movies_auth_state.json`
- `movies_catalog_index.json`
- `cache/`

---

## 문제 해결

### UI 변경이 보이지 않음

- 먼저 페이지를 일반적으로 새로고침합니다
- JS 번들이 변경되었다면 `index.html`이 예상된 번들 버전을 참조하는지 확인합니다

### 비공개 직접 재생 실패

- 비공개 모드를 다시 잠금 해제하여 `movies_device_id` 쿠키를 새로 고칩니다

### Plex 재생은 실패하지만 Direct 재생은 동작함

- movies server 호스트가 `plex.base_url`에 도달할 수 있는지 확인합니다
- 설정에서 Plex가 활성화되어 있는지 확인합니다
- 구성된 토큰이 유효한지 확인합니다

### Direct 재생은 실패하지만 Plex 재생은 동작함

- 해당 컨테이너나 코덱은 그 기기 브라우저의 네이티브 재생에 적합하지 않을 가능성이 큽니다
- 이런 파일은 Plex를 유지하거나 로컬 트랜스코딩 또는 Plex를 통한 호환 경로를 강제하십시오

### 로컬 트랜스코딩이 동작하지 않음

- `ffmpeg`와 `ffprobe`가 설치되어 있는지 확인합니다
- `on_demand_transcode`가 활성화되어 있는지 확인합니다
- 원본 파일이 현재 지원되는 컨테이너 `.mkv` 또는 `.ts`인지 확인합니다

---

## 라이선스

이 프로젝트는 MIT License로 배포됩니다. 공개하거나 재배포할 때는 MIT 전문이 포함된 `LICENSE` 파일을 추가하십시오.
