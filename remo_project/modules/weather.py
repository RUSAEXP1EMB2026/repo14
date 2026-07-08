import requests

from config import OPENWEATHERMAP_API_KEY, OPENWEATHERMAP_CITY


def get_weather():
    if not OPENWEATHERMAP_API_KEY:
        return {
            "weather": "unknown",
            "description": "unknown",
            "outside_temp": None,
            "rain_probability": None,
            "future_weather": "unknown",
            "future_description": "unknown",
            "future_temp": None,
            "future_rain_probability": None,
        }

    response = requests.get(
        "https://api.openweathermap.org/data/2.5/forecast",
        params={
            "q": OPENWEATHERMAP_CITY,
            "appid": OPENWEATHERMAP_API_KEY,
            "units": "metric",
            "lang": "ja",
        },
        timeout=10,
    )

    response.raise_for_status()
    data = response.json()

    forecasts = data.get("list", [])
    if not forecasts:
        return {
            "weather": "unknown",
            "description": "unknown",
            "outside_temp": None,
            "rain_probability": None,
            "future_weather": "unknown",
            "future_description": "unknown",
            "future_temp": None,
            "future_rain_probability": None,
        }

    # 一番近い時間帯の予報
    current = forecasts[0]

    # 約3時間後の予報（なければ現在の予報を使う）
    future = forecasts[1] if len(forecasts) > 1 else current

    return {
        # 現在（直近）
        "weather": current["weather"][0]["main"],
        "description": current["weather"][0]["description"],
        "outside_temp": current["main"]["temp"],
        "rain_probability": int(current.get("pop", 0) * 100),

        # 約3時間後
        "future_weather": future["weather"][0]["main"],
        "future_description": future["weather"][0]["description"],
        "future_temp": future["main"]["temp"],
        "future_rain_probability": int(future.get("pop", 0) * 100),
    }
