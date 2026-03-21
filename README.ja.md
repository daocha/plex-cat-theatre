# Cat Theatre Movies Server

> Flask、Waitress、`ffmpeg` で構成されたセルフホスト型の映画ブラウザ兼ストリーミングサーバーで、互換性重視の再生のために Plex 統合を任意で利用できます。

**言語**

[English](./README.md) | `日本語`

---

## 概要

Cat Theatre は軽量さを重視しています。

- Python 依存が少ない
- データベース不要
- ファイルシステム中心のカタログ
- OS 依存の監視ではなくポーリング型スキャン
- Plex は任意機能

用途:

- 複数フォルダにまたがるローカルメディアライブラリ
- サムネイルとプレビュー生成
- デバイス単位のプライベートフォルダ制御
- `/movie/` のようなサブパス配下での公開
- 直接再生、ローカルトランスコード、Plex HLS の併用

---

## 主な機能

- マルチルートスキャン
- ポスターサムネイルとプレビューフレーム
- プライベートフォルダ
- ネイティブ直接再生
- `.mkv` と `.ts` のローカルトランスコード
- Plex 連携
- リバースプロキシのサブパス対応
- ブラウザ画像キャッシュと IndexedDB メタデータキャッシュ

---

## プロジェクト構成

- `movies_server.py`
- `movies_server_core.py`
- `movies_catalog.py`
- `movies_server_plex.py`
- `movies.js`
- `movies.min.js`
- `movies.css`
- `passcode.py`

---

## 必要条件

```bash
pip install -r requirements.txt
which ffmpeg
which ffprobe
```

---

## クイックスタート

```bash
cp movies_config.sample.json movies_config.json
python3 movies_server.py --config movies_config.json
```

アクセス:

```text
http://localhost:9245
```

---

## 設定

重要な項目:

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

## 再生モード

- 直接再生: `/video/<id>`
- ローカルトランスコード: `/hls/<id>/index.m3u8` または `/video/<id>?fmp4=1`
- Plex 再生: Plex が HLS を生成し、このアプリがプロキシ

### デフォルトの再生ロジック

- `.mp4`、`.m4v`、`.webm`、`.avi` は、直接 URL が実ファイルを指し、音声コーデックがホワイトリスト内なら `Direct` が優先されます
- これらのブラウザ向け拡張子で音声メタデータが欠けていても、アプリは引き続き `Direct` を優先します
- `.mkv`、`.ts`、HLS/fMP4 の直接 URL、または既知の音声コーデックがホワイトリスト外のファイルは `Plex` が優先されます
- Plex の対応付けが無い場合は `Direct` にフォールバックします

---

## キャッシュとスキャン

- 画像は長期キャッシュ
- IndexedDB スナップショットは 1 日 TTL
- 最大 8 件
- 合計約 18MB 上限
- `/rescan?full=1` で完全再検証

---

## プライベートモードとデバッグ

- プライベートフォルダは既定で非表示
- 解除状態はデバイス単位
- `passcode.py` でパスコード更新可能
- `debug_enabled` で右下のデバッグオーバーレイ表示

---

## トラブルシューティング

- Plex 再生失敗時は `plex.base_url` と token を確認
- ローカルトランスコード失敗時は `ffmpeg`、`ffprobe`、`on_demand_transcode` を確認
