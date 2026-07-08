import time

from config import ANNOUNCE_FILE, AUDIO_ENABLED


def judge(settings, sensor_data, weather_data, aircon_action):
    if aircon_action:
        return {
            "value": "announce_aircon",
            "text": "室温が変化したため空調を調整しました",
            "reason": aircon_action.get("reason", "aircon action was selected"),
        }

    weather = weather_data.get("weather")
    if weather == "Rain":
        return {
            "value": "announce_weather",
            "text": "本日は雨の予報です",
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
