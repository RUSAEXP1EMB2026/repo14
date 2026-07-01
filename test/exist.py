# exist.py

import csv
import os
from datetime import datetime, timezone

from remo import get_sensor_data

CSV_FILE_PATH = "plant_mode_log.csv"


def check_plant_mode():

    try:

        data = get_sensor_data()

        temperature = data["temp"]
        humidity = data["humidity"]
        motion = data["motion"]
        motion_time = data["motion_time"]

        # 最後に人感を検知した時間
        last_detected = datetime.fromisoformat(
            motion_time.replace("Z", "+00:00")
        )

        now = datetime.now(timezone.utc)

        hours = (
            now - last_detected
        ).total_seconds() / 3600

        # 植物モード判定
        if hours >= 3:

            plant_mode = True
            mode = "植物育成モード"

            if temperature < 15:
                action = "暖房推奨"

            elif temperature > 30:
                action = "冷房推奨"

            else:
                action = "植物育成ライトON"

        else:

            plant_mode = False
            mode = "通常モード"
            action = "なし"

        # CSV保存
        file_exists = os.path.exists(CSV_FILE_PATH)

        with open(
            CSV_FILE_PATH,
            mode="a",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.writer(f)

            if not file_exists:
                writer.writerow(
                    [
                        "日時",
                        "温度",
                        "湿度",
                        "人感",
                        "最終検知からの経過時間",
                        "モード",
                        "動作"
                    ]
                )

            writer.writerow(
                [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    temperature,
                    humidity,
                    motion,
                    round(hours, 2),
                    mode,
                    action
                ]
            )

        print("===== 植物モード判定 =====")
        print(f"温度: {temperature}℃")
        print(f"湿度: {humidity}%")
        print(f"人感: {motion}")
        print(f"最終検知から: {round(hours, 2)}時間")
        print(f"モード: {mode}")
        print(f"動作: {action}")
        print("========================")

        return plant_mode

    except Exception as e:
        print("エラー:", e)
        return False


if __name__ == "__main__":
    check_plant_mode()