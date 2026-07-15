# remo_line_bot

LINE -> ngrok -> Python Flask -> Googleスプレッドシート の受付用プロジェクトです。

このフォルダはGASを使わず、Python FlaskがLINEのWebhookを直接受け取ります。受け取った設定はGoogleスプレッドシートの `Settings` と `CommandQueue` に保存します。

## ファイル

- `app.py`: LINE Webhook受付、署名検証、Spreadsheet保存、LINE返信
- `.env.example`: 環境変数の記入例
- `requirements.txt`: 必要ライブラリ
- `.gitignore`: 秘密情報をGitに入れないための除外設定

## セットアップ

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

`.env.example` を `.env` にコピーして、LINEとGoogle Sheetsの値を入れます。

```env
LINE_CHANNEL_SECRET=ここにChannel secret
LINE_CHANNEL_ACCESS_TOKEN=ここにChannel access token
SPREADSHEET_ID=ここにスプレッドシートID
GOOGLE_SERVICE_ACCOUNT_JSON=service_account.json
PORT=5000
```

`.env` と `service_account.json` は公開しないでください。

## Google Sheets

最低限、以下の2シートを使います。存在しない場合は `app.py` が自動作成します。

`Settings`

| key | value | updated_at |
| --- | --- | --- |
| wake_time | 07:30 | 2026-xx-xx xx:xx |
| return_time | 18:30 | 2026-xx-xx xx:xx |
| sleep_time | 24:00 | 2026-xx-xx xx:xx |
| absence_threshold | 180 | 2026-xx-xx xx:xx |

`CommandQueue`

| timestamp | user_id | command | value | status |
| --- | --- | --- | --- | --- |

新しい命令は `PENDING` として追加されます。Pythonメイン処理側で読み取ったあと `DONE` にする想定です。

## 起動

```powershell
.\.venv\Scripts\activate
python app.py
```

ブラウザで確認します。

```text
http://127.0.0.1:5000/health
```

`OK` が表示されればFlask側は起動しています。

## ngrok

別のPowerShellで実行します。

```powershell
ngrok http 5000
```

LINE Developersに登録するWebhook URLは、ngrokのHTTPS URLに `/callback` を付けたものです。

```text
https://xxxx.ngrok-free.app/callback
```

## LINEで試す文言

```text
起床 07:30
帰宅 18:30
就寝 24:00
不在 180
```

期待する動作は、LINEに設定完了メッセージが返り、`Settings` に設定値、`CommandQueue` に `PENDING` の行が追加されることです。

## よくある確認点

- `/callback` は署名検証があるため、ブラウザ確認には使いません。確認は `/health` を使います。
- LINE DevelopersのWebhook URLには必ず `/callback` を付けます。
- ngrokを再起動するとURLが変わることがあります。
- Googleスプレッドシートは、`service_account.json` 内の `client_email` に編集者として共有してください。
- LINE Official Account Managerでは、Webhookをオン、応答メッセージをオフにします。

使用しているスプレッドシートのリンクは以下になります。
https://docs.google.com/spreadsheets/d/1YA5_eNiOeVL7PNGDX3NNqP7eb9whQGqhdd3NHhZjMQ4/edit?usp=sharing


あああ