def judge(settings, sensor_data, weather_data, presence):
    weather = weather_data.get("weather")

    if not presence:
        return {"value": "plant_mode", "reason": "room is vacant"}

    if weather in ("Rain", "Clouds"):
        return {"value": "warm_light", "reason": "weather is cloudy or rainy"}

    if weather == "Clear":
        return {"value": "daylight", "reason": "weather is clear"}

    return None
