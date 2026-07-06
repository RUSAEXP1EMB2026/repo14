import time

from config import LOOP_INTERVAL_SECONDS
from controllers import aircon_controller, audio_controller, light_controller, plant_mode_controller, presence_controller
from modules import nature_remo, spreadsheet, weather
from services import command_handler


def run_once():
    settings = spreadsheet.get_settings()

    command_handler.process_line_commands()

    sensor_data = nature_remo.get_sensor_data()
    spreadsheet.save_sensor_log(sensor_data)

    weather_data = weather.get_weather()
    spreadsheet.save_weather_log(weather_data)

    presence = presence_controller.judge(sensor_data, settings)

    aircon_action = aircon_controller.judge(settings, sensor_data, weather_data)
    if aircon_action:
        result = nature_remo.control_aircon(aircon_action)
        spreadsheet.save_control_log("aircon", aircon_action, result)

    plant_mode_action = plant_mode_controller.judge(settings, sensor_data, weather_data, presence)
    if plant_mode_action:
        result = nature_remo.control_light(plant_mode_action)
        spreadsheet.save_control_log("plant_mode", plant_mode_action, result)

    light_action = light_controller.judge(settings, sensor_data, weather_data, presence)
    if light_action and not plant_mode_action:
        result = nature_remo.control_light(light_action)
        spreadsheet.save_control_log("light", light_action, result)

    audio_action = audio_controller.judge(settings, sensor_data, weather_data, aircon_action)
    if audio_action:
        result = audio_controller.play(audio_action)
        spreadsheet.save_control_log("audio", audio_action, result)


def main():
    while True:
        try:
            run_once()
        except Exception as exc:
            spreadsheet.save_control_log("system", "error", str(exc))
        time.sleep(LOOP_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
