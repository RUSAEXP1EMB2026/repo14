from modules.scheduler import is_time_in_daily_range


def judge(settings, sensor_data, weather_data, presence=None, now=None):
    if is_sleep_period(settings, now=now):
        return {
            "value": "off",
            "reason": "current time is between sleep time and wake time",
        }

    return {
        "value": "full_light",
        "reason": "current time is outside the sleep period",
    }


def is_sleep_period(settings, now=None):
    return is_time_in_daily_range(
        settings.get("sleep_time"),
        settings.get("wake_time"),
        now=now,
    )
