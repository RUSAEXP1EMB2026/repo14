# main.py

import time

from remo import get_sensor_data
from presence import check_presence
from aircon import cool_on
from weather import get_weather
from exist import check_plant_mode
from audio import speak
from log import save_log

# 前回の天気を記録
last_weather = ""

while True:

    try:

        # -------------------------
        # センサ・天気取得
        # -------------------------
        sensor = get_sensor_data()
        weather = get_weather()

        temp = sensor["temp"]
        humidity = sensor["humidity"]
        motion = sensor["motion"]

        current_weather = weather["weather"]

        print("\n===== システム実行 =====")
        print(f"室温: {temp}℃")
        print(f"湿度: {humidity}%")
        print(f"天気: {weather['description']}")

        # -------------------------
        # 天気アナウンス
        # -------------------------
        global_weather_changed = (
            current_weather != last_weather
        )

        if global_weather_changed:

            if current_weather == "Rain":

                print("本日は雨の予報です")
                speak("本日は雨の予報です")

            elif current_weather == "Clear":

                print("本日は晴れです")
                speak("本日は晴れです")

            elif current_weather == "Clouds":

                print("本日は曇りです")
                speak("本日は曇りです")

            last_weather = current_weather

        # -------------------------
        # エアコン制御
        # -------------------------
        if temp >= 28:

            cool_on()

            print("冷房を起動しました")

            speak(
                "室温が上昇したため冷房を起動しました"
            )

        # -------------------------
        # 在室判定
        # -------------------------
        if check_presence(motion):

            presence = "在室"
            print("在室中")

        else:

            presence = "不在"
            print("不在")

        # -------------------------
        # 植物育成モード判定
        # -------------------------
        plant_mode = check_plant_mode()

        if plant_mode:

            print("植物育成ライトON")

        # -------------------------
        # ログ保存
        # -------------------------
        save_log(
            temp=temp,
            humidity=humidity,
            weather=weather["description"],
            presence=presence,
            plant_mode=plant_mode
        )

        print("========================")

    except Exception as e:

        print("エラー:", e)

    # 5分ごと
    time.sleep(300)