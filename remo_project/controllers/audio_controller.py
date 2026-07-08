import time
import os

from config import ANNOUNCE_FILE, AUDIO_ENABLED


AIRCON_MESSAGE = "\u5ba4\u6e29\u304c\u5909\u5316\u3057\u305f\u305f\u3081\u3001\u7a7a\u8abf\u3092\u8abf\u6574\u3057\u307e\u3057\u305f\u3002"
RAIN_MESSAGE = "\u672c\u65e5\u306f\u96e8\u306e\u4e88\u5831\u3067\u3059\u3002"


def judge(settings, sensor_data, weather_data, aircon_action):
    if aircon_action:
        return {
            "value": "announce_aircon",
            "text": AIRCON_MESSAGE,
            "reason": aircon_action.get("reason", "aircon action was selected"),
        }

    weather = weather_data.get("weather")
    if weather == "Rain":
        return {
            "value": "announce_weather",
            "text": RAIN_MESSAGE,
            "reason": "weather is rainy",
        }

    return None


def play(action):
    text = action.get("text", action.get("value", "")) if isinstance(action, dict) else str(action)
    if not AUDIO_ENABLED:
        return {
            "status": "skipped",
            "message": "AUDIO_ENABLED is false.",
            "text": text,
        }

    try:
        os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
        import pygame
        from gtts import gTTS

        pygame.mixer.init()
        tts = gTTS(text=text, lang="ja")
        tts.save(ANNOUNCE_FILE)

        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

        pygame.mixer.music.load(ANNOUNCE_FILE)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.5)

        return {"status": "ok", "text": text}

    except Exception as exc:
        return {"status": "error", "message": str(exc), "text": text}
