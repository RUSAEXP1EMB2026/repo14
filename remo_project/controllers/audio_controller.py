import time
import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from config import ANNOUNCE_FILE, AUDIO_ENABLED, LOOP_INTERVAL_SECONDS


AIRCON_MESSAGE = "\u5ba4\u6e29\u304c\u5909\u5316\u3057\u305f\u305f\u3081\u3001\u7a7a\u8abf\u3092\u8abf\u6574\u3057\u307e\u3057\u305f\u3002"
WAKE_ANNOUNCEMENT_WINDOW_MINUTES = max(5, LOOP_INTERVAL_SECONDS / 60 + 1)

_last_wake_announcement_key = None


def judge(settings, sensor_data, weather_data, aircon_action, now=None):
    wake_action = judge_wake(settings, sensor_data, weather_data, now=now)
    if wake_action:
        return wake_action

    return judge_non_wake(weather_data, aircon_action)


def judge_wake(settings, sensor_data, weather_data, now=None):
    # 設定された起床時刻のアナウンス（同一プロセス内で1日1回）
    now = now or datetime.now()
    wake_key = _wake_announcement_key(settings, now)
    if wake_key and wake_key != _last_wake_announcement_key:
        weather_desc = weather_data.get("description") or weather_data.get("weather") or "不明"
        temp = _display_value(sensor_data.get("temperature"))
        humidity = _display_value(sensor_data.get("humidity"))
        wake_text = (
            f"おはようございます、現在は{now:%H時%M分}"
            f"天気は{weather_desc}、室温{temp}度、湿度{humidity}パーです"
        )

        return {
            "value": "announce_wake",
            "text": wake_text,
            "reason": "configured wake time was reached",
            "wake_announcement_key": wake_key,
        }


def is_wake_announcement_due(settings, now=None):
    wake_key = get_wake_event_key(settings, now=now)
    return bool(wake_key and wake_key != _last_wake_announcement_key)


def get_wake_event_key(settings, now=None):
    return _wake_announcement_key(settings, now or datetime.now())


def judge_non_wake(weather_data, aircon_action):
    # 通常の空調アナウンス
    if aircon_action:
        return {
            "value": "announce_aircon",
            "text": AIRCON_MESSAGE,
            "reason": aircon_action.get("reason", "aircon action was selected"),
        }

    # 雨の日アナウンス（降水確率が50%以上の場合）
    rain_prob_current = weather_data.get("rain_probability", 0)
    if rain_prob_current >= 50:
        return {
            "value": "announce_weather",
            "text": f"本日は雨の予報です。降水確率は{rain_prob_current}パーセントです。傘をお持ちください。",
            "reason": "high rain probability",
        }

    return None


def play(action):
    text = action.get("text", action.get("value", "")) if isinstance(action, dict) else str(action)
    if not AUDIO_ENABLED:
        result = {
            "status": "skipped",
            "message": "AUDIO_ENABLED is false.",
            "text": text,
        }
        _mark_wake_announcement(action)
        return result

    announcement_file = None
    try:
        os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
        import pygame
        from gtts import gTTS

        pygame.mixer.init()
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        if hasattr(pygame.mixer.music, "unload"):
            pygame.mixer.music.unload()

        announce_path = Path(ANNOUNCE_FILE)
        suffix = announce_path.suffix or ".mp3"
        announcement_file = announce_path.with_name(
            f"{announce_path.stem}-{uuid4().hex}{suffix}"
        )

        tts = gTTS(text=text, lang="ja")
        tts.save(str(announcement_file))

        pygame.mixer.music.load(str(announcement_file))
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.5)

        result = {"status": "ok", "text": text}
        _mark_wake_announcement(action)
        return result

    except Exception as exc:
        return {"status": "error", "message": str(exc), "text": text}

    finally:
        if announcement_file is not None:
            try:
                if "pygame" in locals() and hasattr(pygame.mixer.music, "unload"):
                    pygame.mixer.music.unload()
            except Exception:
                pass
            try:
                announcement_file.unlink(missing_ok=True)
            except OSError:
                pass


def _wake_announcement_key(settings, now):
    time_text = str(settings.get("wake_time", "")).strip()
    try:
        hour_text, minute_text = time_text.split(":", 1)
        hour = int(hour_text)
        minute = int(minute_text)
    except (TypeError, ValueError):
        return None

    if hour == 24 and minute == 0:
        hour = 0
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return None

    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    elapsed_minutes = (now - target).total_seconds() / 60
    if not 0 <= elapsed_minutes <= WAKE_ANNOUNCEMENT_WINDOW_MINUTES:
        return None

    return f"{target.date().isoformat()}:{hour:02d}:{minute:02d}"


def _display_value(value):
    return "不明" if value is None or value == "" else value


def _mark_wake_announcement(action):
    global _last_wake_announcement_key

    if not isinstance(action, dict):
        return

    wake_key = action.get("wake_announcement_key")
    if wake_key:
        _last_wake_announcement_key = wake_key
