from datetime import datetime, timezone


def judge(sensor_data, settings):
    motion = sensor_data.get("motion")
    if motion is None:
        return False

    if not (motion == 1 or motion is True):
        return False

    motion_time = _parse_datetime(sensor_data.get("motion_time"))
    if motion_time is None:
        return True

    presence_timeout = _to_float(settings.get("presence_timeout"), 5)
    elapsed_minutes = (datetime.now(timezone.utc) - motion_time).total_seconds() / 60
    return elapsed_minutes <= presence_timeout


def _parse_datetime(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def _to_float(value, default):
    try:
        if value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default
