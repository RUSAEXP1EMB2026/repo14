from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials

from config import GOOGLE_SERVICE_ACCOUNT_FILE, GOOGLE_SPREADSHEET_ID


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def _now():
    return datetime.now().isoformat(timespec="seconds")


def _spreadsheet():
    if not GOOGLE_SPREADSHEET_ID or not GOOGLE_SERVICE_ACCOUNT_FILE:
        raise RuntimeError("Google Spreadsheet settings are missing.")
    credentials = Credentials.from_service_account_file(
        GOOGLE_SERVICE_ACCOUNT_FILE,
        scopes=SCOPES,
    )
    client = gspread.authorize(credentials)
    return client.open_by_key(GOOGLE_SPREADSHEET_ID)


def _worksheet(name):
    return _spreadsheet().worksheet(name)


def get_settings():
    rows = _worksheet("Settings").get_all_records()
    return {row["key"]: row["value"] for row in rows if row.get("key")}


def save_sensor_log(sensor_data):
    sheet = _worksheet("SensorLog")
    sheet.append_row([
        _now(),
        sensor_data.get("temperature"),
        sensor_data.get("humidity"),
        sensor_data.get("illuminance"),
        sensor_data.get("motion"),
        sensor_data.get("motion_time"),
    ])


def save_weather_log(weather_data):
    sheet = _worksheet("WeatherLog")
    sheet.append_row([
        _now(),
        weather_data.get("weather"),
        weather_data.get("description"),
        weather_data.get("outside_temp"),
        weather_data.get("rain_probability"),
    ])


def save_control_log(target, action, result=""):
    sheet = _worksheet("ControlLog")
    reason = action.get("reason", "") if isinstance(action, dict) else ""
    value = action.get("value", action) if isinstance(action, dict) else action
    sheet.append_row([_now(), target, value, reason, str(result)])


def get_pending_commands():
    sheet = _worksheet("CommandQueue")
    rows = sheet.get_all_records()
    commands = []

    for index, row in enumerate(rows, start=2):
        status = str(row.get("status", "")).upper()
        if status == "PENDING":
            row["_row_number"] = index
            commands.append(row)

    return commands


def mark_command_done(row_number):
    sheet = _worksheet("CommandQueue")
    sheet.update_cell(row_number, 5, "DONE")
