import time
import threading

from config import LOOP_INTERVAL_SECONDS
from controllers import (
    aircon_controller,
    audio_controller,
    bgm_controller,
    light_controller,
    plant_mode_controller,
    presence_controller,
)
from modules import nature_remo, spreadsheet, weather
from services import command_handler


_LAST_CONTROL_SIGNATURES = {}


def run_once():
    settings = spreadsheet.get_settings()

    command_handler.process_line_commands()

    sensor_data = nature_remo.get_sensor_data()
    spreadsheet.save_sensor_log(sensor_data)

    weather_data = weather.get_weather()
    spreadsheet.save_weather_log(weather_data)

    presence = presence_controller.judge(sensor_data, settings)

    executed_aircon_action = None
    aircon_action = aircon_controller.judge(settings, sensor_data, weather_data, presence)
    if aircon_action:
        if not _is_duplicate_control("aircon", aircon_action):
            result = nature_remo.control_aircon(aircon_action)
            if result.get("status") == "ok":
                _remember_control("aircon", aircon_action)
                executed_aircon_action = aircon_action
            spreadsheet.save_control_log("aircon", aircon_action, result)

    plant_mode_action = plant_mode_controller.judge(settings, sensor_data, weather_data, presence)
    if plant_mode_action:
        result = nature_remo.control_light(plant_mode_action)
        spreadsheet.save_control_log("plant_mode", plant_mode_action, result)

    light_action = light_controller.judge(settings, sensor_data, weather_data, presence)
    if light_action and not plant_mode_action:
        result = nature_remo.control_light(light_action)
        spreadsheet.save_control_log("light", light_action, result)

    _handle_bgm(settings, sensor_data, weather_data, presence, aircon_action)

    audio_action = audio_controller.judge(settings, sensor_data, weather_data, executed_aircon_action)
    if audio_action:
        result = audio_controller.play(audio_action)
        spreadsheet.save_control_log("audio", audio_action, result)


def _handle_bgm(settings, sensor_data, weather_data, presence, aircon_action):
    if presence and bgm_controller.is_enabled(settings):
        category = bgm_controller.judge(settings, sensor_data, weather_data, aircon_action)
        if category:
            result = bgm_controller.play(category)
            if result.get("status") != "already_playing":
                spreadsheet.save_control_log(
                    "bgm",
                    {"value": category, "reason": "bgm category selected"},
                    result,
                )
            return

        result = bgm_controller.stop()
        if result.get("status") == "stopped":
            spreadsheet.save_control_log(
                "bgm",
                {"value": "stop", "reason": "bgm category was not selected"},
                result,
            )
        return

    result = bgm_controller.stop()
    if result.get("status") == "stopped":
        reason = "room is vacant" if not presence else "bgm flag is off"
        spreadsheet.save_control_log("bgm", {"value": "stop", "reason": reason}, result)


def main():
    start_line_bot()

    while True:
        try:
            run_once()
        except Exception as exc:
            spreadsheet.save_control_log("system", "error", str(exc))
        time.sleep(LOOP_INTERVAL_SECONDS)


def start_line_bot():
    from remo_line_bot.app import run_server

    thread = threading.Thread(
        target=run_server,
        name="line-bot-server",
        daemon=True,
    )
    thread.start()
    return thread


def _is_duplicate_control(target, action):
    return _LAST_CONTROL_SIGNATURES.get(target) == _control_signature(action)


def _remember_control(target, action):
    _LAST_CONTROL_SIGNATURES[target] = _control_signature(action)


def _control_signature(action):
    if isinstance(action, dict):
        return (
            action.get("value"),
            action.get("operation_mode"),
            action.get("temperature"),
            action.get("air_volume"),
            action.get("button"),
        )

    return action


if __name__ == "__main__":
    main()
