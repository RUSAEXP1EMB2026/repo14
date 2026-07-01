import requests

TOKEN = "ory_at_bIkD-nnzTB8rhiqJ4cy6bPfXpCYlQGp-w_6I00Gf8-4.wGiTj2j39XAJDzhylR9e7b-8NRTh8N2Gg5IVYI55s2Q"

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

r = requests.get(
    "https://api.nature.global/1/devices",
    headers=headers
)

device = r.json()[0]

temp = device["newest_events"]["te"]["val"]
humidity = device["newest_events"]["hu"]["val"]
motion = device["newest_events"]["mo"]["val"]
light = device["newest_events"]["il"]["val"]

print(f"温度: {temp}℃")
print(f"湿度: {humidity}%")
print(f"人感: {motion}")
print(f"照度: {light}")

