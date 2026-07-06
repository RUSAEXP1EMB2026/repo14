# remo_project

GASをLINE受付、Pythonをメイン制御にするNature Remo連携プロジェクトです。

## Structure

- `gas/line_bot.gs`: LINE Bot受付とGoogle Spreadsheetへの設定保存
- `main.py`: Python側のメインループ
- `modules/`: Spreadsheet、Nature Remo、天気APIなどの外部連携
- `controllers/`: 空調、照明、音声、在室、植物育成モードの判定
- `services/`: 共通判定やLINEコマンド処理

## Spreadsheet Sheets

`Settings`

| key | value |
| --- | --- |
| wake_time | 07:00 |
| return_time | 18:30 |
| sleep_time | 23:00 |
| absence_threshold | 30 |
| comfort_temp_min | 20 |
| comfort_temp_max | 26 |
| comfort_humidity_min | 40 |
| comfort_humidity_max | 60 |

`SensorLog`

| timestamp | temperature | humidity | illuminance | motion |
| --- | --- | --- | --- | --- |

`WeatherLog`

| timestamp | weather | outside_temp | rain_probability |
| --- | --- | --- | --- |

`ControlLog`

| timestamp | target | action | reason | result |
| --- | --- | --- | --- | --- |

`CommandQueue`

| timestamp | source | command | value | status |
| --- | --- | --- | --- | --- |

## Setup

1. Copy `.env.example` to `.env`.
2. Fill in Google Spreadsheet, Nature Remo, and OpenWeatherMap settings.
3. Install dependencies.

```bash
pip install -r requirements.txt
```

4. Start the Python main loop.

```bash
python main.py
```

Nature Remoの家電操作は、家電IDと具体的な操作内容が決まってから `modules/nature_remo.py` に追加します。
