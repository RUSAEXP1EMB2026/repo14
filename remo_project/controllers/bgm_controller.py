import os
import random
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
BGM_BASE_DIR = BASE_DIR / "bgm"
BGM_FOLDERS = {
    "clear": "clear",
    "rain": "rain",
    "cloudy": "cloudy",
    "wake": "wake",
}

_current_category = None


def is_enabled(settings):
    flag = str(settings.get("bgm_flag", "ON")).strip().upper()
    return flag in ("ON", "TRUE", "1", "YES")


def judge(settings, sensor_data, weather_data, aircon_action):
    if not is_enabled(settings):
        return None

    if aircon_action and aircon_action.get("value") == "wake_preheat":
        return "wake"

    weather = weather_data.get("weather")
    if weather == "Clear":
        return "clear"
    if weather in ("Rain", "Drizzle", "Thunderstorm"):
        return "rain"
    if weather == "Clouds":
        return "cloudy"

    return None


def play(category):
    global _current_category

    if category not in BGM_FOLDERS:
        return {
            "status": "skipped",
            "message": f"Unknown BGM category: {category}",
            "category": category,
        }

    pygame = _pygame()
    if not pygame.mixer.get_init():
        pygame.mixer.init()

    if _current_category == category and pygame.mixer.music.get_busy():
        return {
            "status": "already_playing",
            "category": category,
        }

    bgm_file = get_random_bgm(category)
    if not bgm_file:
        return {
            "status": "skipped",
            "message": f"BGM file was not found for category: {category}",
            "category": category,
            "folder": str(BGM_BASE_DIR / BGM_FOLDERS[category]),
        }

    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(str(bgm_file))
        pygame.mixer.music.play(-1)
        _current_category = category
        return {
            "status": "ok",
            "category": category,
            "file": str(bgm_file),
        }
    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc),
            "category": category,
            "file": str(bgm_file),
        }


def stop():
    global _current_category

    pygame = _pygame()
    if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
        stopped_category = _current_category
        _current_category = None
        return {
            "status": "stopped",
            "category": stopped_category,
        }

    _current_category = None
    return {
        "status": "idle",
    }


def get_random_bgm(category):
    folder_name = BGM_FOLDERS.get(category)
    if not folder_name:
        return None

    folder_path = BGM_BASE_DIR / folder_name
    if not folder_path.exists():
        return None

    files = [
        path
        for path in folder_path.iterdir()
        if path.is_file() and path.suffix.lower() == ".mp3"
    ]
    return random.choice(files) if files else None


def _pygame():
    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
    import pygame

    return pygame
