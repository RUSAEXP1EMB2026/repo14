from modules.scheduler import is_within_minutes


def judge(settings, sensor_data, weather_data):
    temperature = sensor_data.get("temperature")
    if temperature is None:
        return None

    comfort_min = float(settings.get("comfort_temp_min", 20))
    comfort_max = float(settings.get("comfort_temp_max", 26))

    if is_within_minutes(settings.get("wake_time"), 30):
        return {"value": "wake_preheat", "reason": "wake time is near"}

    if is_within_minutes(settings.get("return_time"), 30):
        return {"value": "return_preheat", "reason": "return time is near"}

    if is_within_minutes(settings.get("sleep_time"), 10):
        return {"value": "sleep_mode", "reason": "sleep time is near"}

    if temperature < comfort_min:
        return {"value": "heating", "reason": "room temperature is low"}

    if temperature > comfort_max:
        return {"value": "cooling", "reason": "room temperature is high"}

    return None
