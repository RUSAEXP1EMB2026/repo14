#aircon.py

import requests

TOKEN = "ory_at_bIkD-nnzTB8rhiqJ4cy6bPfXpCYlQGp-w_6I00Gf8-4.wGiTj2j39XAJDzhylR9e7b-8NRTh8N2Gg5IVYI55s2Q"

APPLIANCE_ID = "824ea23c-f1e2-4a49-963c-8487c0054618"


def cool_on():

    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }

    r = requests.post(
        f"https://api.nature.global/1/appliances/{APPLIANCE_ID}/aircon_settings",
        headers=headers,
        data={
            "operation_mode": "cool",
            "temperature": "25",
            "air_volume": "auto"
        }
    )

    print("エアコンAPI結果:", r.status_code)

def power_off():

    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }

    requests.post(
        f"https://api.nature.global/1/signals/...",
        headers=headers
    )