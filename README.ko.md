# Cat Theatre 영화 서버

> Flask, Waitress, `ffmpeg` 기반의 경량 셀프호스팅 영화 브라우저 및 스트리밍 서버.

[English](./README.md)

---

## 핵심 기능

- 멀티 루트 라이브러리 스캔
- 썸네일 및 프리뷰 프레임 생성
- 장치 기반 비공개 폴더 잠금 해제
- 직접 재생, 로컬 트랜스코드, Plex 재생 경로
- `/movie/` 같은 리버스 프록시 경로 접두사 지원

---

## 빠른 시작

```bash
cp movies_config.sample.json movies_config.json
python3 movies_server.py --config movies_config.json
```

접속:

```text
http://localhost:9245
```

---

## 주요 설정

- `root`
- `thumbs_dir`
- `private_folder`
- `private_passcode`
- `mount_script`
- `enable_plex_server`
- `direct_playback`
- `plex.base_url`
- `plex.token`

---

## 재생 모드

### 직접 재생

- `.mp4`, `.m4v`, `.webm`에 적합
- 경로: `/video/<id>`

### 로컬 트랜스코드

- HLS: `/hls/<id>/index.m3u8`
- fMP4: `/video/<id>?fmp4=1`

### Plex

- Plex HLS
- Plex 포스터
- Plex 자막

---

## 확인 명령

```bash
python3 -m py_compile movies_server.py movies_server_core.py movies_server_plex.py movies_catalog.py
node --check movies.js
```
