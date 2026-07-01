import requests

from config import OPENWEATHERMAP_API_KEY, OPENWEATHERMAP_CITY


def get_weather():
    if not OPENWEATHERMAP_API_KEY:
        return {
            "weather": "unknown",
            "outside_temp": None,
            "rain_probability": None,
        }

    response = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
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

    return {
        "weather": data["weather"][0]["main"],
        "outside_temp": data["main"]["temp"],
        "rain_probability": None,
    }
