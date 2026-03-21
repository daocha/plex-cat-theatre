# Cat Theatre Movies Server

> Flask, Waitress, `ffmpeg` 기반의 셀프호스팅 영화 브라우저 및 스트리밍 서버이며, 호환성 중심 재생을 위해 Plex 통합을 선택적으로 지원합니다.

**언어**

[English](./README.md) | `한국어`

---

## 개요

Cat Theatre는 가볍게 유지됩니다.

- 작은 Python 의존성
- 데이터베이스 불필요
- 파일 시스템 중심 카탈로그
- 플랫폼 종속 파일 감시 대신 폴링 기반 스캔
- Plex는 선택 사항

적합한 용도:

- 여러 폴더에 분산된 로컬 미디어 라이브러리
- 썸네일과 프리뷰 생성
- 기기 기반 비공개 폴더 제어
- `/movie/` 같은 경로 프리픽스 프록시 배포
- 직접 재생, 로컬 트랜스코딩, Plex HLS 혼합 재생

---

## 기능

- 멀티 루트 스캔
- 포스터 썸네일과 프리뷰 프레임
- 비공개 폴더
- 네이티브 직접 재생
- `.mkv`, `.ts` 로컬 트랜스코딩
- Plex 통합
- 리버스 프록시 하위 경로 지원
- 브라우저 이미지 캐시와 IndexedDB 메타데이터 캐시

---

## 프로젝트 구조

- `movies_server.py`
- `movies_server_core.py`
- `movies_catalog.py`
- `movies_server_plex.py`
- `movies.js`
- `movies.min.js`
- `movies.css`
- `passcode.py`

---

## 요구 사항

```bash
pip install -r requirements.txt
which ffmpeg
which ffprobe
```

---

## 빠른 시작

```bash
cp movies_config.sample.json movies_config.json
python3 movies_server.py --config movies_config.json
```

열기:

```text
http://localhost:9245
```

---

## 설정

중요한 필드:

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

## 재생 모드

- 직접 재생: `/video/<id>`
- 로컬 트랜스코딩: `/hls/<id>/index.m3u8` 또는 `/video/<id>?fmp4=1`
- Plex 재생: Plex가 HLS를 생성하고 이 앱이 프록시

### 기본 재생 로직

- `.mp4`, `.m4v`, `.webm`, `.avi` 는 direct URL 이 실제 파일 경로이고 오디오 코덱이 화이트리스트에 맞으면 `Direct` 를 우선 사용합니다
- 이런 브라우저 안전 확장자에서 오디오 메타데이터가 없더라도 앱은 여전히 `Direct` 를 우선합니다
- `.mkv`, `.ts`, HLS/fMP4 direct URL, 그리고 알려진 오디오 코덱이 화이트리스트 밖인 파일은 `Plex` 를 우선합니다
- Plex 매칭이 없으면 `Direct` 로 되돌아갑니다

---

## 캐시와 스캔

- 이미지 장기 캐시
- IndexedDB 스냅샷 TTL 1일
- 최대 8개 스냅샷
- 약 18MB 상한
- `/rescan?full=1` 로 강제 전체 재검증

---

## 비공개 모드와 디버그

- 비공개 폴더는 기본 숨김
- 잠금 해제 상태는 기기 기준
- `passcode.py` 로 비밀번호 회전 가능
- `debug_enabled` 로 디버그 오버레이 표시

---

## 문제 해결

- Plex 재생 실패 시 `plex.base_url` 과 토큰 확인
- 로컬 트랜스코딩 실패 시 `ffmpeg`, `ffprobe`, `on_demand_transcode` 확인
