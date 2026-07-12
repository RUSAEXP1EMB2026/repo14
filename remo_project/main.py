import time
import threading

from config import LOOP_INTERVAL_SECONDS, WAKE_CHECK_INTERVAL_SECONDS
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
_last_wake_light_key = None


def run_once():
    settings = spreadsheet.get_settings()

    command_handler.process_line_commands()

    sensor_data = nature_remo.get_sensor_data()
    spreadsheet.save_sensor_log(sensor_data)

    weather_data = weather.get_weather()
    spreadsheet.save_weather_log(weather_data)

    _handle_wake_actions(settings, sensor_data, weather_data)

    presence = presence_controller.judge(sensor_data, settings)

    executed_aircon_action = None
    aircon_action = aircon_controller.judge(settings, sensor_data, weather_data, presence)
    if aircon_action:
        if not _is_duplicate_control("aircon", aircon_action):
            result = _execute_control("aircon", aircon_action, nature_remo.control_aircon)
            if result.get("status") == "ok":
                _remember_control("aircon", aircon_action)
                executed_aircon_action = aircon_action

    plant_mode_action = plant_mode_controller.judge(settings, sensor_data, weather_data, presence)
    if plant_mode_action:
        _execute_control("plant_mode", plant_mode_action, nature_remo.control_light)

    light_action = light_controller.judge(settings, sensor_data, weather_data, presence)
    if light_action and not plant_mode_action:
        _execute_control("light", light_action, nature_remo.control_light)

    _handle_bgm(settings, sensor_data, weather_data, presence, aircon_action)

    audio_action = audio_controller.judge_non_wake(weather_data, executed_aircon_action)
    if audio_action:
        result = audio_controller.play(audio_action)
        spreadsheet.save_control_log("audio", audio_action, result)


def _handle_wake_announcement(settings, sensor_data, weather_data):
    action = audio_controller.judge_wake(settings, sensor_data, weather_data)
    if not action:
        return

    result = audio_controller.play(action)
    spreadsheet.save_control_log("audio", action, result)


def _handle_wake_actions(settings, sensor_data, weather_data):
    wake_key = audio_controller.get_wake_event_key(settings)
    if wake_key:
        _handle_wake_light(wake_key)

    _handle_wake_announcement(settings, sensor_data, weather_data)


def _handle_wake_light(wake_key):
    global _last_wake_light_key

    if wake_key == _last_wake_light_key:
        return

    action = {
        "value": "on",
        "reason": "configured wake time was reached",
    }
    result = _execute_control("wake_light", action, nature_remo.control_light)
    if result.get("status") == "ok":
        _last_wake_light_key = wake_key


def _execute_control(target, action, control):
    try:
        result = control(action)
    except Exception as exc:
        result = {
            "status": "error",
            "message": str(exc),
        }

    spreadsheet.save_control_log(target, action, result)
    return result


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
    next_control_at = 0.0

    while True:
        now = time.monotonic()
        try:
            if now >= next_control_at:
                next_control_at = now + LOOP_INTERVAL_SECONDS
                run_once()
            else:
                check_wake_actions()
        except Exception as exc:
            spreadsheet.save_control_log("system", "error", str(exc))

        seconds_until_control = max(0, next_control_at - time.monotonic())
        sleep_seconds = min(WAKE_CHECK_INTERVAL_SECONDS, seconds_until_control)
        if sleep_seconds > 0:
            time.sleep(sleep_seconds)


def check_wake_actions():
    settings = spreadsheet.get_settings()
    wake_key = audio_controller.get_wake_event_key(settings)
    if not wake_key:
        return

    if wake_key != _last_wake_light_key:
        _handle_wake_light(wake_key)

    if audio_controller.is_wake_announcement_due(settings):
        sensor_data = nature_remo.get_sensor_data()
        weather_data = weather.get_weather()
        _handle_wake_announcement(settings, sensor_data, weather_data)


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
