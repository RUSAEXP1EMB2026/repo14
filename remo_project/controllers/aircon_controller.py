from modules.scheduler import is_within_minutes


RAINY_WEATHER = {"Rain", "Drizzle", "Thunderstorm", "Snow"}
CLOUDY_WEATHER = {"Clouds", "Mist", "Fog", "Haze"}


def judge(settings, sensor_data, weather_data):
    temperature = _to_float(sensor_data.get("temperature"))
    if temperature is None:
        return None

    comfort_min = _to_float(settings.get("comfort_temp_min"), 20)
    comfort_max = _to_float(settings.get("comfort_temp_max"), 26)
    humidity_max = _to_float(settings.get("comfort_humidity_max"), 65)

    if is_within_minutes(settings.get("wake_time"), 30):
        return _rhythm_action(
            "wake_preheat",
            "wake time is near",
            temperature,
            humidity_max,
            sensor_data,
            weather_data,
            comfort_min,
            comfort_max,
        )

    if is_within_minutes(settings.get("return_time"), 30):
        return _rhythm_action(
            "return_preheat",
            "return time is near",
            temperature,
            humidity_max,
            sensor_data,
            weather_data,
            comfort_min,
            comfort_max,
        )

    if is_within_minutes(settings.get("sleep_time"), 10):
        return _sleep_action(sensor_data, weather_data)

    humidity = _to_float(sensor_data.get("humidity"))
    if humidity is not None and humidity > humidity_max and temperature >= comfort_max - 1:
        return _cooling_action(
            "humidity_cooling",
            "humidity is high",
            sensor_data,
            weather_data,
        )

    if temperature < comfort_min:
        return _heating_action(
            "heating",
            "room temperature is low",
            sensor_data,
            weather_data,
        )

    if temperature > comfort_max:
        return _cooling_action(
            "cooling",
            "room temperature is high",
            sensor_data,
            weather_data,
        )

    return None


def _rhythm_action(
    value,
    reason,
    temperature,
    humidity_max,
    sensor_data,
    weather_data,
    comfort_min,
    comfort_max,
):
    outside_temp = _to_float(weather_data.get("outside_temp"))
    weather = weather_data.get("weather")
    humidity = _to_float(sensor_data.get("humidity"))

    if temperature <= comfort_min or (outside_temp is not None and outside_temp <= 15):
        return _heating_action(value, reason, sensor_data, weather_data)

    if temperature >= comfort_max or (outside_temp is not None and outside_temp >= 28):
        return _cooling_action(value, reason, sensor_data, weather_data)

    if weather in RAINY_WEATHER and humidity is not None and humidity > humidity_max:
        return _cooling_action(
            value,
            f"{reason}; rainy weather and humidity are high",
            sensor_data,
            weather_data,
        )

    return None


def _sleep_action(sensor_data, weather_data):
    temperature = _to_float(sensor_data.get("temperature"))
    outside_temp = _to_float(weather_data.get("outside_temp"))

    if temperature is not None and temperature <= 18:
        return _heating_action(
            "sleep_mode",
            "sleep time is near and room is cold",
            sensor_data,
            weather_data,
            sleep=True,
        )

    if outside_temp is not None and outside_temp <= 10:
        return _heating_action(
            "sleep_mode",
            "sleep time is near and outside temperature is low",
            sensor_data,
            weather_data,
            sleep=True,
        )

    return _cooling_action(
        "sleep_mode",
        "sleep time is near",
        sensor_data,
        weather_data,
        sleep=True,
    )


def _cooling_action(value, reason, sensor_data, weather_data, sleep=False):
    temperature = _cooling_temperature(sensor_data, weather_data, sleep=sleep)
    return _action(
        value=value,
        reason=reason,
        operation_mode="cool",
        temperature=temperature,
        sensor_data=sensor_data,
        weather_data=weather_data,
    )


def _heating_action(value, reason, sensor_data, weather_data, sleep=False):
    temperature = _heating_temperature(weather_data, sleep=sleep)
    return _action(
        value=value,
        reason=reason,
        operation_mode="warm",
        temperature=temperature,
        sensor_data=sensor_data,
        weather_data=weather_data,
    )


def _cooling_temperature(sensor_data, weather_data, sleep=False):
    outside_temp = _to_float(weather_data.get("outside_temp"))
    humidity = _to_float(sensor_data.get("humidity"))
    weather = weather_data.get("weather")
    target = 27 if sleep else 25

    if outside_temp is not None:
        if outside_temp >= 32:
            target -= 1
        elif outside_temp <= 26:
            target += 1

    if weather in RAINY_WEATHER or (humidity is not None and humidity >= 70):
        target -= 1
    elif weather in CLOUDY_WEATHER and outside_temp is not None and outside_temp < 30:
        target += 1

    return _clamp(target, 24, 28)


def _heating_temperature(weather_data, sleep=False):
    outside_temp = _to_float(weather_data.get("outside_temp"))
    weather = weather_data.get("weather")
    target = 21 if sleep else 22

    if outside_temp is not None:
        if outside_temp <= 5:
            target += 1
        elif outside_temp >= 15:
            target -= 1

    if weather in RAINY_WEATHER:
        target += 1

    return _clamp(target, 20, 24)


def _action(value, reason, operation_mode, temperature, sensor_data, weather_data):
    weather = weather_data.get("weather")
    outside_temp = _to_float(weather_data.get("outside_temp"))
    humidity = _to_float(sensor_data.get("humidity"))

    return {
        "value": value,
        "reason": _reason_with_weather(reason, weather, outside_temp, humidity),
        "operation_mode": operation_mode,
        "temperature": str(temperature),
        "air_volume": "auto",
        "weather": weather,
        "outside_temp": outside_temp,
        "humidity": humidity,
    }


def _reason_with_weather(reason, weather, outside_temp, humidity):
    details = []
    if weather:
        details.append(f"weather={weather}")
    if outside_temp is not None:
        details.append(f"outside_temp={outside_temp}")
    if humidity is not None:
        details.append(f"humidity={humidity}")

    if not details:
        return reason

    return f"{reason}; " + ", ".join(details)


def _to_float(value, default=None):
    try:
        if value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))
