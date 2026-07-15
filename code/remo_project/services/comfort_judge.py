def is_comfortable(settings, sensor_data):
    temperature = sensor_data.get("temperature")
    humidity = sensor_data.get("humidity")
    if temperature is None or humidity is None:
        return False

    return (
        float(settings.get("comfort_temp_min", 20)) <= temperature <= float(settings.get("comfort_temp_max", 26))
        and float(settings.get("comfort_humidity_min", 40)) <= humidity <= float(settings.get("comfort_humidity_max", 60))
    )
