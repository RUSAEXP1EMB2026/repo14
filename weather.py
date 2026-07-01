#weather.py
import requests

API_KEY = "4a2eb14da94e0a763006e5bcf9839d3e"

def get_weather():

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q=Osaka,jp"
        f"&appid={API_KEY}"
        f"&units=metric"
        f"&lang=ja"
    )

    r = requests.get(url)

    data = r.json()

    return {
        "weather": data["weather"][0]["main"],
        "description": data["weather"][0]["description"],
        "temp": data["main"]["temp"]
    }