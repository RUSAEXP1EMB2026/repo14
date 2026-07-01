def judge(settings, sensor_data, weather_data, presence):
    if presence:
        return None
    return {"value": "plant_mode", "reason": "room is vacant"}
