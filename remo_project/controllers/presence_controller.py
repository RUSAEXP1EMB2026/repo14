def judge(sensor_data, settings):
    motion = sensor_data.get("motion")
    if motion is None:
        return False
    return bool(motion)
