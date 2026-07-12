from datetime import datetime, timedelta


def is_within_minutes(time_text, minutes, now=None):
    now = now or datetime.now()
    targets = _target_candidates(time_text, now)
    return any(abs(now - target) <= timedelta(minutes=minutes) for target in targets)


def is_before_time_within_minutes(time_text, minutes, now=None):
    now = now or datetime.now()
    targets = _target_candidates(time_text, now)
    return any(
        timedelta(0) <= target - now <= timedelta(minutes=minutes)
        for target in targets
    )


def _target_candidates(time_text, now):
    parsed = _parse_time(time_text)
    if parsed is None:
        return []

    hour, minute = parsed
    today = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    return [today - timedelta(days=1), today, today + timedelta(days=1)]


def _parse_time(time_text):
    if not time_text:
        return None

    try:
        hour_text, minute_text = str(time_text).strip().split(":", 1)
        hour = int(hour_text)
        minute = int(minute_text)
    except (TypeError, ValueError):
        return None

    if hour == 24 and minute == 0:
        return 0, 0
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return None

    return hour, minute
