#kumitate14_exist.py
import csv
from datetime import datetime
import os
import requests

# 【実験当日に書き換える場所】
REMO_ACCESS_TOKEN = "ここにトークンを入れる"
AIRCON_APPLIANCE_ID = "ここにエアコンのIDを入れる"  # 実験当日に調べて入れる

# 記録用のCSVファイル名（スプレッドシートの代わりにパソコン内に自動で作られます）
CSV_FILE_PATH = "plant_mode_log.csv"


def check_plant_mode():
    headers = {
        "Authorization": f"Bearer {REMO_ACCESS_TOKEN}",
        "accept": "application/json",
    }

    try:
        # 1. Nature Remoからセンサーデータの取得
        response = requests.get(
            "https://api.nature.global/1/devices", headers=headers
        )
        response.raise_for_status()
        devices = response.json()
        remo3 = devices[0]

        # 人感センサーの最終検知時刻の計算
        last_detected_str = remo3["newest_events"]["mo"]["val"]
        last_detected = datetime.fromisoformat(
            last_detected_str.replace("Z", "+00:00")
        )
        now = datetime.now(last_detected.tzinfo)

        minutes = (now - last_detected).total_seconds() / 60
        temperature = remo3["newest_events"]["te"]["val"]  # 現在の室温

        presence = ""
        action = ""
        mode = ""

        # 2. 在室判定とエアコン動作のロジック
        if minutes >= 30:
            presence = "不在（30分以上検知なし）"

            if temperature <= 15:
                action = "暖房ON"
                mode = "warm"
            elif temperature >= 23:
                action = "冷房ON"
                mode = "cool"
            else:
                action = "適温のため何もしない"
        else:
            presence = "在室中"
            action = "操作なし（人がいるため）"

        # 3. 【エアコンを実際に動かす命令】
        # ※ 実験当日に本当にエアコンを動かしたい場合は、下の「"""」を2箇所消してください。
        """
        if mode in ["cool", "warm"]:
            aircon_url = f"https://api.nature.global/1/appliances/{AIRCON_APPLIANCE_ID}/aircon_settings"
            aircon_payload = {
                "operation_mode": mode,  # 冷房 or 暖房
                "temperature": "24" if mode == "cool" else "20",  # 冷房24度、暖房20度
                "button": ""  # 空っぽにすると「電源ON」になります
            }
            # 実際にNature Remoに信号を送る
            aircon_response = requests.post(aircon_url, headers=headers, data=aircon_payload)
            aircon_response.raise_for_status()
            print(f"実際のエアコンに【{action}】の電波を送信しました。")
        """

        # 4. CSVファイルへの記録 (GASのスプレッドシート代わり)
        file_exists = os.path.exists(CSV_FILE_PATH)
        with open(CSV_FILE_PATH, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["日時", "室温", "在室判定", "エアコンの動作"])

            now_local_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([now_local_str, temperature, presence, action])

        print(f"ファイルに正常に記録されました：{action}")

    except Exception as e:
        print(f"エラーが発生しました: {e}")


# 実行ボタンの代わり（プログラムを動かすトリガー）
if __name__ == "__main__":
    check_plant_mode()