# remo_project 統合まとめ

`test` フォルダで使えそうだった処理を、`remo_project` の構成に合わせて統合するためのファイル一式です。

## 統合した要素

- Nature Remoのセンサ取得に `motion_time` を追加
- Nature Remoのエアコン操作を `control_aircon()` に追加
- OpenWeatherMapの天気説明 `description` を追加
- gTTS + pygame による音声読み上げを `audio_controller.py` に追加
- 人感センサの在室判定を `motion == 1` ベースに調整
- 最終人感検知時刻と `absence_threshold` による植物育成モード判定を追加
- `CommandQueue` の `PENDING` 読み取りと `DONE` 更新を追加
- Nature Remoの家電IDを確認する `tools/print_appliances.py` を追加
- `main.py` に植物育成モード判定の呼び出しを追加
- `.env.example` にNature Remo家電ID、音声設定を追加

## 反映先

同名ファイルを `C:/Users/kenth/work/exp1/remo_project/` に反映してください。

```text
config.py
.env.example
requirements.txt
main.py
modules/nature_remo.py
modules/spreadsheet.py
modules/weather.py
controllers/audio_controller.py
controllers/presence_controller.py
controllers/plant_mode_controller.py
services/command_handler.py
tools/print_appliances.py
```

## 追加で.envに必要な値

```env
NATURE_REMO_TOKEN=
NATURE_REMO_AIRCON_ID=
NATURE_REMO_LIGHT_ID=
OPENWEATHERMAP_API_KEY=
OPENWEATHERMAP_CITY=Osaka,jp
AUDIO_ENABLED=false
ANNOUNCE_FILE=announce.mp3
```

`AUDIO_ENABLED=true` にすると、PCから音声読み上げを行います。

## スプレッドシートに必要なシート

Settings

| key | value | updated_at |
| --- | --- | --- |
| wake_time | 07:30 | |
| return_time | 18:30 | |
| sleep_time | 24:00 | |
| absence_threshold | 180 | |
| comfort_temp_min | 20 | |
| comfort_temp_max | 26 | |
| comfort_humidity_min | 40 | |
| comfort_humidity_max | 60 | |

SensorLog

| timestamp | temperature | humidity | illuminance | motion | motion_time |
| --- | --- | --- | --- | --- | --- |

WeatherLog

| timestamp | weather | description | outside_temp | rain_probability |
| --- | --- | --- | --- | --- |

ControlLog

| timestamp | target | action | reason | result |
| --- | --- | --- | --- | --- |

CommandQueue

| timestamp | user_id | command | value | status |
| --- | --- | --- | --- | --- |

## まだ追加が必要なもの

- 照明のNature Remo信号IDを取得して、昼光色・暖色・植物育成ライトの実操作に対応する
- OpenWeatherMapのforecast APIで数時間先予報と降水確率を取得する
- Google Nest Miniでの音声出力を行う場合は別途連携方式を決める
- BGM再生をSpotify等で行う場合はAPI認証とプレイリストIDが必要
- APIエラー時でも動作継続できるよう、前回成功値のキャッシュを追加する
