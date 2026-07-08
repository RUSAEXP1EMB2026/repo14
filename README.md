# remo_project

LINEで生活リズムを受け付け、Python本体がNature Remo、天気API、Google Spreadsheetを使って空調・照明・音声・ログ保存を行うプロジェクトです。

## 構成

```text
remo_project/
├─ main.py
├─ config.py
├─ modules/
│  ├─ nature_remo.py
│  ├─ spreadsheet.py
│  ├─ weather.py
│  └─ scheduler.py
├─ controllers/
│  ├─ aircon_controller.py
│  ├─ light_controller.py
│  ├─ audio_controller.py
│  ├─ presence_controller.py
│  └─ plant_mode_controller.py
├─ services/
│  └─ command_handler.py
├─ tools/
│  └─ print_appliances.py
└─ remo_line_bot/
   └─ app.py
```

`remo_line_bot/` はLINE Webhook受付用です。`main.py` は制御本体です。

## .env

`.env.example` をコピーして `.env` を作成します。`.env` はGitHubに上げないでください。

```env
LOOP_INTERVAL_SECONDS=300

GOOGLE_SPREADSHEET_ID=
GOOGLE_SERVICE_ACCOUNT_FILE=remo_line_bot/service_account.json

NATURE_REMO_TOKEN=
NATURE_REMO_AIRCON_ID=
NATURE_REMO_LIGHT_ID=

NATURE_REMO_LIGHT_CONTROL_METHOD=button
NATURE_REMO_LIGHT_DAYLIGHT_BUTTON=colortemp-up
NATURE_REMO_LIGHT_WARM_BUTTON=colortemp-down
NATURE_REMO_LIGHT_PLANT_BUTTON=on-100
NATURE_REMO_LIGHT_OFF_BUTTON=off
NATURE_REMO_LIGHT_DAYLIGHT_SIGNAL_ID=
NATURE_REMO_LIGHT_WARM_SIGNAL_ID=
NATURE_REMO_LIGHT_PLANT_SIGNAL_ID=
NATURE_REMO_LIGHT_OFF_SIGNAL_ID=

OPENWEATHERMAP_API_KEY=
OPENWEATHERMAP_CITY=Osaka,jp

AUDIO_ENABLED=false
ANNOUNCE_FILE=announce.mp3
```

## 照明制御方式

照明制御は3方式から選べます。

```env
NATURE_REMO_LIGHT_CONTROL_METHOD=button
```

`button` はNature Remoの照明プリセットボタンを送る方式です。今回のPanasonic照明は `signals` が空で `light.buttons` があるため、この方式を使います。

```env
NATURE_REMO_LIGHT_CONTROL_METHOD=signal
```

`signal` は学習リモコンのsignal IDを送る方式です。`NATURE_REMO_LIGHT_DAYLIGHT_SIGNAL_ID` などにsignal IDを入れて使います。

```env
NATURE_REMO_LIGHT_CONTROL_METHOD=auto
```

`auto` はbutton方式を優先し、足りなければsignal方式を試します。

## 現在の照明ボタン対応

| action | button |
| --- | --- |
| daylight | colortemp-up |
| warm_light | colortemp-down |
| plant_mode | on-100 |
| off | off |

`light_controller.py` が返す `value` に応じて、`modules/nature_remo.py` の `control_light()` が送信方式を選びます。

## 家電ID確認

```powershell
python -m tools.print_appliances
```

出力されたエアコンIDと照明IDを `.env` に入れます。

```env
NATURE_REMO_AIRCON_ID=
NATURE_REMO_LIGHT_ID=
```

## 単体テスト

Remoセンサ取得:

```powershell
python -c "from modules import nature_remo; print(nature_remo.get_sensor_data())"
```

天気取得:

```powershell
python -c "from modules import weather; print(weather.get_weather())"
```

Spreadsheet設定取得:

```powershell
python -c "from modules import spreadsheet; print(spreadsheet.get_settings())"
```

照明button方式テスト:

```powershell
python -c "from modules import nature_remo; print(nature_remo.control_light({'value':'daylight','reason':'manual test'}))"
python -c "from modules import nature_remo; print(nature_remo.control_light({'value':'warm_light','reason':'manual test'}))"
python -c "from modules import nature_remo; print(nature_remo.control_light({'value':'plant_mode','reason':'manual test'}))"
```

エアコンテスト:

```powershell
python -c "from modules import nature_remo; print(nature_remo.control_aircon({'value':'cooling','reason':'manual test'}))"
```

## 本体の1回実行

無限ループではなく1回だけ動かす場合:

```powershell
python -c "from main import run_once; run_once()"
```

`SensorLog`、`WeatherLog`、`ControlLog` に行が追加されれば成功です。

## Spreadsheet

必要なシートは以下です。

```text
Settings
SensorLog
WeatherLog
ControlLog
CommandQueue
```

`Settings` の例:

```text
key,value,updated_at
wake_time,07:30,
return_time,19:00,
sleep_time,23:59,
absence_threshold,180,
comfort_temp_min,0,
comfort_temp_max,40,
comfort_humidity_min,0,
comfort_humidity_max,100,
```

`24:00` はPythonの時刻変換で扱えないため、`23:59` または `00:00` を使ってください。

## 安全メモ

`.env`、`service_account.json`、`.venv/`、`__pycache__/` はGitHubに上げないでください。

エアコン操作テスト後は、`comfort_temp_max` を安全側に戻してください。

1. remo_project/.env を作成
2. remo_project/remo_line_bot/.env を作成
3. service account json を remo_line_bot に配置
4. /debug/config で true 確認
5. main.py の接続確認

```text
comfort_temp_min = 0
comfort_temp_max = 40
```
使用しているスプレッドシートのリンクは以下です
https://docs.google.com/spreadsheets/d/1YA5_eNiOeVL7PNGDX3NNqP7eb9whQGqhdd3NHhZjMQ4/edit?usp=sharing