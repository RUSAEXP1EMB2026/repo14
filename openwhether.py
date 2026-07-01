import requests

API_KEY = "4a2eb14da94e0a763006e5bcf9839d3e"

url = (
    f"https://api.openweathermap.org/data/2.5/weather"
    f"?q=Osaka,jp"
    f"&appid={API_KEY}"
    f"&units=metric"
    f"&lang=ja"
)

r = requests.get(url)

print("status:", r.status_code)
print("text:", r.text)