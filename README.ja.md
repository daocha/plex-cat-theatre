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
  <p><strong>超軽量、プライベートモード 🔐、マルチデバイス、スマートストリーミング</strong></p>
  <p>アプリ不要。サーバー導入は簡単。モバイル向けにも使いやすい画面で、どこからでも NAS に接続でき、必要に応じて Plex と連携できます</p>
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



> 重い依存関係なし、すべてが透明。Flask、Waitress、`ffmpeg` で構築された軽量なセルフホスト型の映画ブラウザ兼ストリーミングサーバーで、互換性重視の再生のために _`Plex`_ 統合を任意で利用できます。

---

![Screenshot 2026-03-22 at 9 39 12 PM](https://github.com/user-attachments/assets/124f21b7-71b0-46fc-9d76-c73f700c25f3)

---

## ✨ 使う理由

Cat Theatre は意図的に軽量です。

- 🩷 _リモートアクセス_ のために Plex のサブスクリプション 💰 は不要
- ✅ Python 依存関係が少ない
- ✅ データベースが不要
- ✅ ファイルシステム中心のカタログ化
- ✅ 🖥️ デスクトップ、📱 モバイル、タブレットに対応
- ✅ OS 固有のウォッチャー依存ではなく、移植性のあるポーリング型スキャンフロー
- 🔶 Plex 統合はコア再生に必須ではなく、任意で重ねられる追加レイヤー

## ✴️ 機能

- 🎬 複数フォルダにまたがるローカル / NAS メディアライブラリ
- 🌄 サムネイル / ポスターとプレビューフレームの生成
- 🔐 デバイス単位で解除するプライベートフォルダ
- 🔗 `http://192.168.1.100/movie/` のようなパスプレフィックス配下でのリバースプロキシ運用
- 📽️ 混在する再生戦略: 直接再生、`.mkv` / `.ts` 向けの内蔵ローカルトランスコード、または Plex ベース HLS プロキシ。メディアごとに簡単に切り替え可能
- 🌐 ブラウザ画像キャッシュと IndexedDB メタデータキャッシュ

---
→ ワンライナーでセットアップ:
```
curl -fsSL https://raw.githubusercontent.com/daocha/plex-cat-theatre/main/install.sh | bash
```
---

## 🟢 動作要件

### Python 3.9 以上

現在の Python パッケージ:

- `Flask`
- `waitress`

### メタデータ解析、プレビュー、サムネイル生成、ローカルトランスコードに必要なシステムバイナリ:

- `ffmpeg`
- `ffprobe`

利用可能か確認:

```bash
which ffmpeg
which ffprobe
```

---

## 🚀 クイックスタート


### → オプション A: ワンライナーでセットアップ:
```
curl -fsSL https://raw.githubusercontent.com/daocha/plex-cat-theatre/main/install.sh | bash
```

### → オプション B: pip で PyPI からインストール

```bash
pip install plex-cat-theatre
plex-cat-theatre-init
plex-cat-theatre --config ~/movies_config.json
```

### → オプション C: 推奨の起動方法

```bash
git clone https://github.com/daocha/plex-cat-theatre
cd plex-cat-theatre
./startup.sh
```

このブートストラップスクリプトでは次のことができます。

- 初回起動時にサンプル設定から `movies_config.json` を作成
- ローカル `.venv` を作成
- Python 依存関係をそのローカル仮想環境にインストール
- 必要に応じて設定ファイル基準の `cache/thumbnails` と `logs` フォルダを作成
- `ffmpeg` と `ffprobe` を確認
- 必要に応じてプライベートモード用パスコードのハッシュ生成を支援
- ローカル設定でサーバーを起動

以下の手動フローも利用できます。

1. サンプル設定をコピー:

```bash
cp movies_config.sample.json movies_config.json
```

2. 環境に合わせて `movies_config.json` を編集します。

### 🌐 サーバーを起動:

```bash
# オプション A またはオプション B を使う場合
plex-cat-theatre --config ~/movies_config.json

# オプション C を使う場合
python3 movies_server.py --config movies_config.json
```

画面を開く:

```text
http://localhost:9245
```
### 🔑 パスコードを変更
```bash
# オプション A またはオプション B を使う場合
plex-cat-theatre-passcode newpasscode

# オプション C を使う場合
python3 passcode.py newpasscode
```
- プライベートフォルダはデバイスが承認されるまで非表示
- 解除状態はデバイス ID に紐づく
- 承認済みデバイスはサーバー側に保存される
- このスクリプトでプライベートモードのパスコードをローテーションし、承認をクリアできる

---

## 🗂️ プロジェクト構成

- `movies_server.py`: Flask エントリーポイントとルーティング接続
- `movies_server_core.py`: 認証、設定、Cookie、マウントパス処理の共通サーバーヘルパー
- `movies_catalog.py`: カタログスキャン、サムネイル生成、字幕抽出、ローカルトランスコード補助
- `movies_server_plex.py`: Plex アダプタ、ポスター / 字幕の対応付け、Plex HLS プロキシ
- `movies.js`: フロントエンドソース
- `movies.min.js`: 圧縮済みフロントエンドバンドル
- `movies.css`: ギャラリーとプレイヤーのスタイル
- `passcode.py`: プライベートモードのパスコードをローテーションする補助スクリプト

---

## ⚙️ 設定

サンプル設定は意図的にサニタイズされており、以下は含まれていません。

- 実際のファイルシステムパス
- 実際の Plex トークン
- 実際のハッシュ化済みパスコード
- デバイス固有の値

### 📍 重要な項目

<table>
  <tr>
    <td width="200"><code>root</code></td>
    <td>スキャン対象のメディアルート（複数フォルダ対応）</td>
  </tr>
  <tr>
    <td><code>thumbs_dir</code></td>
    <td>サムネイルとプレビューフレーム用ディレクトリ。既定値: <code>./cache/thumbnails</code></td>
  </tr>
  <tr>
    <td><code>private_folder</code></td>
    <td>プライベートとして扱うフォルダ接頭辞。例: <code>Personal</code>。<code>Personal</code> フォルダ配下の内容は画面で解除するまでロックされます。</td>
  </tr>
  <tr>
    <td><code>private_passcode</code></td>
    <td>プライベートモード用パスコードハッシュです。平文で直接更新しないでください。更新したい場合は <code>パスコードを変更</code> セクションを参照してください。</td>
  </tr>
  <tr>
    <td><code>mount_script</code></td>
    <td>[任意] 再生時にメディアフォルダがアンマウントされていることを検出した場合に実行するコマンド。</td>
  </tr>
  <tr>
    <td><code>transcode</code></td>
    <td>`.mkv` や `.ts` などのソースコンテナ向けに、カタログ側のバックグラウンドトランスコードワーカーを有効化します。元ライブラリの横に別のトランスコード済みサイドカーファイルを生成する場合があるため、特に Plex 統合を有効にしているときは通常 <code>false</code> のままが推奨です。既定値: <code>false</code></td>
  </tr>
  <tr>
    <td><code>auto_scan_on_start</code></td>
    <td>起動時にメディアを再スキャンします。既定値: <code>false</code></td>
  </tr>
  <tr>
    <td><code>on_demand_transcode</code></td>
    <td>ソースコンテナに対する実行時プレイヤートランスコードを有効化します。利用可能ならハードウェアエンコードを優先し、必要時にはソフトウェアエンコードへフォールバックします。既定値: <code>true</code></td>
  </tr>
  <tr>
    <td><code>on_demand_hls</code></td>
    <td>ソースコンテナ向けに内蔵 HLS プレイリストを有効化します。既定値: <code>true</code></td>
  </tr>
  <tr>
  <td><code>enable_plex_server</code></td>
  <td>📍 [任意] Plex 統合を有効化します。既定値: <code>false</code>。有効にする前に、Plex Server が正しくインストールされ設定済みであることを確認してください。<br> このサーバーはネイティブ字幕を扱えますが、自動で字幕を取得したい場合は Plex を使う方が適しています。
  <br> オンデマンドトランスコード体験をより良くしたい場合は、シームレスなメディア配信のために Plex server の導入を強く推奨します。<br>
  Plex server がなくてもこのサーバーは十分使えますが、次の点に注意してください。
  <br>→ デバイスが直接再生できるメディアでは、シーク機能は問題なく動作します。
  <br>→ デバイスが直接再生できないメディア、たとえば <code>DTS 音声付き h.265</code>（AAC または MP3 の h.265 は影響なし）、<code>.mkv</code>、<code>.ts</code>、<code>.wmv</code> ではオンザフライ変換は可能ですが、シークが使えないことがあります。
  </td>
  </tr>
  <tr>
    <td><code>plex.base_url</code></td>
    <td>Plex サーバーのベース URL。</td>
  </tr>
  <tr>
    <td><code>plex.token</code></td>
    <td>Plex トークン</td>
  </tr>
  <tr>
    <td><code>debug_enabled</code></td>
    <td>内蔵デバッグオーバーレイを表示</td>
  </tr>
  <tr>
    <td><code>direct_playback</code></td>
    <td><code>enabled</code> と <code>audio_whitelist</code> を持つオブジェクトです。<code>enabled=true</code> のとき、トランスコードせずにネイティブプレイヤーで再生できます（高速）。既定設定のまま使うのがおすすめです。</td>
  </tr>
</table>

### 最小のローカル専用例

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

### Plex 統合例

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

### 🅿️ Plex スキャン時の挙動

- Plex ポスターが利用可能な場合、ローカルのポスターサムネイル生成はスキップされる
- 既存のローカルキャッシュ済みサムネイルは引き続き再利用できる
- プレビューフレーム生成は有効のまま
- Plex 統合は任意であり、ローカル専用モードも引き続き使える

### → Plex トークンの取得方法

#### 方法 1: 既存の Plex Web セッション

1. Plex Web を開いてサインインします。
2. ブラウザの開発者ツールを開きます。
3. ネットワークタブに移動します。
4. ページを再読み込みします。
5. Plex サーバーに送られているリクエストを確認します。
6. URL またはヘッダー内の `X-Plex-Token` を探します。

#### 方法 2: ブラウザストレージ

確認する項目:

- ローカルストレージ (`Local Storage`)
- セッションストレージ (`Session Storage`)
- DevTools 上のリクエスト URL とヘッダー

#### 方法 3: ローカルへの直接リクエスト

同じマシンで Plex Web にログイン済みであれば、DevTools で Plex リクエストを確認し、次を探します。

```text
X-Plex-Token=...
```

‼️ セキュリティ上の注意:

- Plex トークンはパスワード同様に扱う
- git にコミットしない
- `movies_config.json` にのみ保存する

---

## 🎥 再生モード

### 1. ネイティブ直接再生

`.mp4`、`.m4v`、`.webm` のようなブラウザセーフなファイルに使われます。

挙動:

- `/video/<id>` からローカルファイルを直接配信
- HTTP range request をサポート
- ブラウザがネイティブ再生できる場合、トランスコードのオーバーヘッドを回避

向いているケース:

- MP4 / H.264 系のファイル
- ブラウザがそのまま再生できるファイル
- 音声コーデックが direct-play ホワイトリストに合致するファイル

### 2. Plex を使わない内蔵ローカルトランスコード

Plex が無効な場合、または完全ローカルで運用したい場合のフォールバック経路です。

現在の実装:

- `.mkv` と `.ts` は `/hls/<id>/index.m3u8` でローカル HLS として配信可能
- 同じファイルを `/video/<id>?fmp4=1` で fragmented MP4 として配信することも可能
- HLS セグメントは `ffmpeg` でオンデマンド生成
- まずハードウェアエンコードを試し、必要に応じて `libx264` にフォールバック
- fMP4 出力は `libx264` と AAC で生成

### 3. Plex バックエンド再生

Plex 統合が有効な場合:

- フロントエンドは互換性重視の再生で `plex_stream_url` を使用可能
- Plex が上流の HLS プレイリストを生成
- このサーバーがプレイリストを書き換え、ネストされたプレイリストやセグメント要求をプロキシ
- ブラウザは Plex ではなく、このアプリと通信し続ける

向いているケース:

- コーデックやコンテナのサポートが弱いデバイスでの MKV / TS コンテンツ
- 字幕選択やストリーム正規化を Plex に任せたいケース

### 再生方式の選択ポリシー

- ブラウザセーフで音声コーデックが `direct_playback.audio_whitelist` に合うファイルは直接再生を優先
- `.mkv`、`.ts`、HLS、fMP4、または非対応音声コーデックでは Plex を優先
- iOS ネイティブ HLS のフォールバック待機は長めで、Plex ストリームのウォームアップ時間を確保

### 既定の再生ロジック

- 直接 URL が実ファイルパスで、音声コーデックがホワイトリスト安全なら `.mp4`、`.m4v`、`.webm`、`.avi` は `Direct` を優先
- これらの拡張子で音声コーデック情報が欠けていても、アプリは `Direct` を優先
- `.mkv`、`.ts`、HLS / fMP4 の直接 URL、および既知の音声コーデックがホワイトリスト外のファイルでは `Plex` を優先
- Plex に一致がなければ `Direct` にフォールバック

---

## 認証モデル

このアプリはリクエスト種別ごとに異なる伝送方法を使います。

- API リクエストは `X-Device-Id` ヘッダーを使う
- HLS と Plex プロキシリクエストも `X-Device-Id` ヘッダーを使う
- ネイティブ直接メディアリクエストは `movies_device_id` Cookie のフォールバックを使う

この分割が必要なのは、ネイティブの `<video src="...">` リクエストでは任意のカスタムヘッダーを付けられないためです。

---

## リバースプロキシとコンテキストパス対応

このアプリは次のようなサブパス配下での運用をサポートします。

- `https://example.com/movie/`
- `https://example.com/cinema/`

ルーティングは次の項目で現在のマウントプレフィックスを維持します。

- 直接メディア
- ローカル HLS
- Plex HLS プロキシリクエスト
- ポスターと字幕アセット

---

## Tailscale を使ったリモート Plex アクセス

カスタム画面にはリモートから到達できても、Plex はプライベート LAN でしか到達できない場合、movies server ホストから Plex バックエンドに直接到達できる必要があります。

### 同一ホスト

```json
"plex": {
  "base_url": "http://127.0.0.1:32400"
}
```

### 別の LAN マシン上の Plex

Plex に到達できる Tailscale ノードからルートを広告します。

```bash
sudo tailscale up --advertise-routes=192.168.50.0/24
```

次に movies server ホストから到達性を確認します。

```bash
curl http://192.168.50.10:32400/identity
```

📌 メモ:

- ブラウザが Plex に直接アクセスできる必要はない
- movies server プロセスは `plex.base_url` に到達できる必要がある
- 画面側のリバースプロキシ名や MagicDNS 名だけでは Plex は到達可能にならない

---

## 💾 キャッシュ戦略

### 画像キャッシュ

サムネイル、プレビューフレーム、Plex ポスター画像は長寿命の immutable cache header 付きで配信されます。

### メタデータキャッシュ

ギャラリーのメタデータスナップショットは、容量制限付きで IndexedDB にキャッシュされます。

- TTL は 1 日
- 最大 8 件のスナップショット
- 推定合計サイズは約 18 MB まで
- 制限を超えた古い項目は削除

各キャッシュ済みスナップショットには次が保存されます。

- サーバーの `catalogStatus`
- フォルダ一覧キャッシュ
- 読み込み済み `videos`
- `serverTotal`、`serverOffset`、`serverExhausted` などのページネーションカウンタ

削除は定期実行ではなく、機会があるときに行われます。

- 期限切れ項目は読み込み時または後続の整理時に削除
- 新しいスナップショット保存後に整理が走る
- ブラウザのストレージ圧迫や手動でのサイトデータ削除でも IndexedDB データは消えることがある

---

## 🔍 スキャンの挙動

カタログスキャンは、各ルートを走査し続けながらもコストを増分的に保つよう設計されています。

現在の挙動:

- 変更のないファイルは `mtime + size` のキャッシュ済みシグネチャを再利用
- 定期スキャンでは処理前にフルパス一覧をソートしなくなった
- 削除されたファイルはメモリ上のカタログと永続インデックスから削除
- 削除されたファイルに対しては生成済みサムネイルやプレビューのクリーンアップも実行
- インデックス保存では各ファイルを再度 `stat` せず、キャッシュ済みシグネチャデータを再利用

スキャンが引き続き行うこと:

- 設定済みメディアルートを走査し、追加・変更・削除されたファイルを検出
- プレビュー画像がない場合はプレビュー生成をキューに積む

スキャンが行わないこと:

- 定期スキャン時に大きなメディアファイルのチェックサムは取らない
- キャッシュ済みアーティファクトが存在する限り、未変更ファイルのサムネイルやメタデータは再生成しない

### → 再スキャンを実行

通常の増分再スキャン:

```bash
curl -s http://localhost:9245/rescan | python3 -m json.tool
```

完全再スキャンを強制:

```bash
curl -s "http://localhost:9245/rescan?full=1" | python3 -m json.tool
```

### → 再スキャン画面

`Rescan` ボタンは即時に増分スキャンを開始せず、まずアクションダイアログを開きます。

利用可能な操作:

- `Rescan`: 新規または変更ファイルに対する増分スキャン
- `Full Scan`: 保存済みスキャン状態を消去し、メタデータを全面的に再検証
- `Refresh Database`: ブラウザの IndexedDB スナップショットを削除し、新しいカタログデータを再読み込み

### ⛓️‍💥 マウント消失時の復旧

この機能は、NAS が自動スリープ設定になっていて、一部 OS で SMB マウントが自動的に外れてしまうケースを想定しています。

`mount_script` が設定されており、メディア要求が存在しないフォルダに当たった場合、サーバーは次のように動作します。

1. 親フォルダが存在しないことを検出
2. 設定済みのマウントスクリプトを 1 回実行
3. 対象パスを再確認
4. それでもフォルダが利用できない場合にのみ `Media folder is not mounted` を HTTP 404 で返す

フロントエンドは再生時の 404 をその試行の最終失敗として扱い、サーバーを繰り返し叩く代わりに再試行メッセージを表示します。

---

## 📄 生成されるファイル

以下のファイルは実行時に生成されるため、コミットしないでください。

- `movies_config.json`
- `movies_state.json`
- `movies_auth_state.json`
- `movies_catalog_index.json`
- `cache/`

---

## 🛠️ トラブルシューティング


### → デバッグオーバーレイ

`movies_config.json` で `debug_enabled` を有効にすると、右下に常時表示されるデバッグオーバーレイを出せます。

パネルに表示される内容:

- サーバーが直接再生と Plex のどちらを優先しているか
- 設定済み direct-play 音声ホワイトリスト
- 現在の再生候補と動画 ID
- 直近のスキャン進捗メトリクス

現在有効な設定値の確認:

```bash
curl -s http://localhost:9245/api/config | python3 -m json.tool
```

### → 画面の変更が反映されない

- 現在アプリは `index.html` から `movies.js` を直接読み込んでいるため、フロントエンド変更は `movies.min.js` を再ビルドしなくても反映されます。
- まず通常のリロードを試す
- JS バンドルが変わった場合は、`index.html` が期待するバージョンを参照しているか確認する

### → プライベート動画の直接再生が失敗する

- プライベートモードを再度解除し、`movies_device_id` Cookie を更新する

### → Plex 再生は失敗するが直接再生は動く

- movies server ホストから `plex.base_url` に到達できるか確認
- 設定で Plex が有効か確認
- 設定したトークンが有効か確認

### → 直接再生は失敗するが Plex は動く

- そのデバイスではコンテナまたはコーデックがブラウザネイティブ再生に向いていない可能性が高い
- そのファイルでは Plex を使い続けるか、ローカルトランスコード / Plex で互換経路を強制する

### → ローカルトランスコードが動かない

- `ffmpeg` と `ffprobe` がインストールされているか確認
- `on_demand_transcode` が有効か確認
- 元ファイルが現在対応しているコンテナ `.mkv` または `.ts` か確認

---

## 📦 リリース版のバージョニング

パッケージバージョンは Git タグから決まります。

- TestPyPI / testing: `2026.3.26.dev1` のような開発版を使う
- PyPI プレリリース: `2026.3.26rc1` のような RC を使う
- PyPI 安定版: `2026.3.26` のような安定版を使う
- Git タグは `v2026.3.26.dev1`、`v2026.3.26rc1`、`v2026.3.26` にする
  
---

## ©️ ライセンス

このプロジェクトは MIT License で公開されています。公開または再配布する際は、MIT テキストを含む `LICENSE` ファイルを添付してください。
