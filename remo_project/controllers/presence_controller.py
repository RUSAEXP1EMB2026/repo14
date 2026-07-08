def judge(sensor_data, settings):
    motion = sensor_data.get("motion")
    if motion is None:
        return False
    return motion == 1 or motion is True
