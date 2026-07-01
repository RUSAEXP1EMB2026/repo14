from datetime import datetime, timedelta


def is_within_minutes(time_text, minutes):
    if not time_text:
        return False

    now = datetime.now()
    target = datetime.strptime(time_text, "%H:%M").replace(
        year=now.year,
        month=now.month,
        day=now.day,
    )
    return abs(now - target) <= timedelta(minutes=minutes)
