import requests

from config import NATURE_REMO_TOKEN


BASE_URL = "https://api.nature.global/1"


def _headers():
    if not NATURE_REMO_TOKEN:
        raise RuntimeError("Nature Remo token is missing.")
    return {"Authorization": f"Bearer {NATURE_REMO_TOKEN}"}


def _get(path):
    response = requests.get(f"{BASE_URL}{path}", headers=_headers(), timeout=10)
    response.raise_for_status()
    return response.json()


def _post(path, data):
    response = requests.post(f"{BASE_URL}{path}", headers=_headers(), data=data, timeout=10)
    response.raise_for_status()
    return response.json() if response.text else "ok"


def get_sensor_data():
    devices = _get("/devices")
    if not devices:
        raise RuntimeError("Nature Remo device was not found.")

    newest_events = devices[0].get("newest_events", {})
    return {
        "temperature": newest_events.get("te", {}).get("val"),
        "humidity": newest_events.get("hu", {}).get("val"),
        "illuminance": newest_events.get("il", {}).get("val"),
        "motion": newest_events.get("mo", {}).get("val"),
    }


def control_aircon(action):
    return {
        "status": "skipped",
        "message": "Set appliance ID before enabling aircon control.",
        "action": action,
    }


def control_light(action):
    return {
        "status": "skipped",
        "message": "Set appliance ID before enabling light control.",
        "action": action,
    }
