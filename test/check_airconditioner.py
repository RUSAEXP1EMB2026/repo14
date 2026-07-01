#airconditioner.py
#エアコンのトークンを取得するためのコード
#完成系の実装の時は使わない


import requests

TOKEN = "ory_at_bIkD-nnzTB8rhiqJ4cy6bPfXpCYlQGp-w_6I00Gf8-4.wGiTj2j39XAJDzhylR9e7b-8NRTh8N2Gg5IVYI55s2Q"

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

r = requests.get(
    "https://api.nature.global/1/appliances",
    headers=headers
)

print(r.json())