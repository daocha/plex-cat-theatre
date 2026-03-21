# Cat Theatre 映画サーバー

> Flask、Waitress、`ffmpeg` ベースの軽量セルフホスト映画ブラウザ兼ストリーミングサーバー。

[English](./README.md)

---

## 主な機能

- 複数ルートのライブラリスキャン
- サムネイルとプレビュー生成
- デバイス単位のプライベートフォルダ解除
- 直接再生、ローカル変換、Plex 再生
- `/movie/` のようなリバースプロキシ接頭辞に対応

---

## クイックスタート

```bash
cp movies_config.sample.json movies_config.json
python3 movies_server.py --config movies_config.json
```

開く:

```text
http://localhost:9245
```

---

## 重要な設定

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

## 再生モード

### 直接再生

- `.mp4`、`.m4v`、`.webm` 向け
- パス: `/video/<id>`

### ローカルトランスコード

- HLS: `/hls/<id>/index.m3u8`
- fMP4: `/video/<id>?fmp4=1`

### Plex

- Plex HLS
- Plex ポスター
- Plex 字幕

---

## 確認コマンド

```bash
python3 -m py_compile movies_server.py movies_server_core.py movies_server_plex.py movies_catalog.py
node --check movies.js
```
