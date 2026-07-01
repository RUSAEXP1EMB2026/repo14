from modules.scheduler import is_within_minutes


def is_wake_window(settings):
    return is_within_minutes(settings.get("wake_time"), 30)


def is_return_window(settings):
    return is_within_minutes(settings.get("return_time"), 30)


def is_sleep_window(settings):
    return is_within_minutes(settings.get("sleep_time"), 10)
