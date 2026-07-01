#remo.py
import requests

TOKEN = "ory_at_bIkD-nnzTB8rhiqJ4cy6bPfXpCYlQGp-w_6I00Gf8-4.wGiTj2j39XAJDzhylR9e7b-8NRTh8N2Gg5IVYI55s2Q"

def get_sensor_data():
    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }

    r = requests.get(
        "https://api.nature.global/1/devices",
        headers=headers
    )

    device = r.json()[0]

    return {
    "temp": device["newest_events"]["te"]["val"],
    "humidity": device["newest_events"]["hu"]["val"],
    "motion": device["newest_events"]["mo"]["val"],
    "light": device["newest_events"]["il"]["val"],
    "motion_time": device["newest_events"]["mo"]["created_at"]
}