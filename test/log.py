#log.py
import csv
import os
from datetime import datetime

LOG_FILE = "system_log.csv"


def save_log(
    temp,
    humidity,
    weather,
    presence,
    plant_mode
):

    file_exists = os.path.exists(LOG_FILE)

    with open(
        LOG_FILE,
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
                    "天気",
                    "在室状況",
                    "植物モード"
                ]
            )

        writer.writerow(
            [
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                temp,
                humidity,
                weather,
                presence,
                plant_mode
            ]
        )