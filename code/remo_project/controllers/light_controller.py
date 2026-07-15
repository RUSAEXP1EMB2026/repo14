from controllers import plant_mode_controller
from modules.scheduler import is_time_in_daily_range


def judge(settings, sensor_data, weather_data, presence, now=None):
    if is_sleep_period(settings, now=now):
        return {
            "value": "off",
            "reason": "current time is between sleep time and wake time",
        }

    if presence:
        return {
            "value": "full_light",
            "reason": "presence was detected",
        }

    plant_action = plant_mode_controller.judge(
        settings,
        sensor_data,
        weather_data,
        presence,
    )
    if plant_action:
        return plant_action

    return {
        "value": "off",
        "reason": "presence was not detected",
    }


def is_sleep_period(settings, now=None):
    return is_time_in_daily_range(
        settings.get("sleep_time"),
        settings.get("wake_time"),
        now=now,
    )
