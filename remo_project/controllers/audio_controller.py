import time
import os
from datetime import datetime

from config import ANNOUNCE_FILE, AUDIO_ENABLED


AIRCON_MESSAGE = "\u5ba4\u6e29\u304c\u5909\u5316\u3057\u305f\u305f\u3081\u3001\u7a7a\u8abf\u3092\u8abf\u6574\u3057\u307e\u3057\u305f\u3002"


def judge(settings, sensor_data, weather_data, aircon_action):
    # 1. 起床時の特別アナウンス（最優先）
    if aircon_action and aircon_action.get("value") == "wake_preheat":
        now = datetime.now()
        time_str = f"{now.hour}時{now.minute}分"
        
        temp = sensor_data.get("temperature", "不明な")
        humidity = sensor_data.get("humidity", "不明な")
        
        # 3時間後（未来）の天気を優先して取得。なければ現在の天気を使う
        weather_desc = weather_data.get("future_description") or weather_data.get("description", "不明")
        rain_prob = weather_data.get("future_rain_probability")
        if rain_prob is None:
            rain_prob = weather_data.get("rain_probability", 0)
        
        wake_text = (
            f"おはようございます。現在の時刻は、{time_str}です。"
            f"これからの天気は{weather_desc}、降水確率は{rain_prob}パーセントです。"
            f"現在の室温は{temp}度、湿度は{humidity}パーセントです。"
            "今日も一日頑張りましょう。"
        )
        
        return {
            "value": "announce_wake",
            "text": wake_text,
            "reason": "wake_preheat action was selected",
        }

    # 2. 通常の空調アナウンス
    if aircon_action:
        return {
            "value": "announce_aircon",
            "text": AIRCON_MESSAGE,
            "reason": aircon_action.get("reason", "aircon action was selected"),
        }

    # 3. 雨の日アナウンス（降水確率が50%以上の場合）
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

        # BGMなどが鳴っていれば一度止める
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

        pygame.mixer.music.load(ANNOUNCE_FILE)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.5)

        return {"status": "ok", "text": text}

    except Exception as exc:
        return {"status": "error", "message": str(exc), "text": text}