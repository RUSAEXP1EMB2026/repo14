from datetime import datetime, timezone


def judge(settings, sensor_data, weather_data, presence):
    if presence:
        return None

    motion_time = sensor_data.get("motion_time")
    threshold_minutes = int(settings.get("absence_threshold", 180))

    if not motion_time:
        return {
            "value": "plant_mode",
            "reason": "room is vacant and motion time is unknown",
        }

    last_detected = datetime.fromisoformat(motion_time.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    elapsed_minutes = (now - last_detected).total_seconds() / 60

    if elapsed_minutes >= threshold_minutes:
        return {
            "value": "plant_mode",
            "reason": f"no motion for {elapsed_minutes:.1f} minutes",
        }

    return None
