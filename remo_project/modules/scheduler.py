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


def is_time_in_daily_range(start_time_text, end_time_text, now=None):
    now = now or datetime.now()
    start = _parse_time(start_time_text)
    end = _parse_time(end_time_text)
    if start is None or end is None:
        return False

    current_minutes = now.hour * 60 + now.minute
    start_minutes = start[0] * 60 + start[1]
    end_minutes = end[0] * 60 + end[1]

    if start_minutes == end_minutes:
        return False
    if start_minutes < end_minutes:
        return start_minutes <= current_minutes < end_minutes
    return current_minutes >= start_minutes or current_minutes < end_minutes


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
