import requests

from config import NATURE_REMO_AIRCON_ID, NATURE_REMO_LIGHT_ID, NATURE_REMO_TOKEN


BASE_URL = "https://api.nature.global/1"


def _headers():
    if not NATURE_REMO_TOKEN:
        raise RuntimeError("Nature Remo token is missing.")
    return {"Authorization": f"Bearer {NATURE_REMO_TOKEN}"}


def _get(path):
    response = requests.get(f"{BASE_URL}{path}", headers=_headers(), timeout=10)
    response.raise_for_status()
    return response.json()


def _post(path, data=None):
    response = requests.post(
        f"{BASE_URL}{path}",
        headers=_headers(),
        data=data or {},
        timeout=10,
    )
    response.raise_for_status()
    return response.json() if response.text else {"status": "ok"}


def get_appliances():
    return _get("/appliances")


def get_sensor_data():
    devices = _get("/devices")
    if not devices:
        raise RuntimeError("Nature Remo device was not found.")

    newest_events = devices[0].get("newest_events", {})
    motion_event = newest_events.get("mo", {})
    return {
        "temperature": newest_events.get("te", {}).get("val"),
        "humidity": newest_events.get("hu", {}).get("val"),
        "illuminance": newest_events.get("il", {}).get("val"),
        "motion": motion_event.get("val"),
        "motion_time": motion_event.get("created_at"),
    }


def control_aircon(action):
    if not NATURE_REMO_AIRCON_ID:
        return {
            "status": "skipped",
            "message": "NATURE_REMO_AIRCON_ID is missing.",
            "action": action,
        }

    value = action.get("value") if isinstance(action, dict) else action
    data = _aircon_payload(value)
    result = _post(f"/appliances/{NATURE_REMO_AIRCON_ID}/aircon_settings", data)
    return {"status": "ok", "action": action, "result": result}


def _aircon_payload(value):
    if value in ("cooling", "wake_preheat", "return_preheat"):
        return {
            "operation_mode": "cool",
            "temperature": "25",
            "air_volume": "auto",
        }

    if value == "heating":
        return {
            "operation_mode": "warm",
            "temperature": "22",
            "air_volume": "auto",
        }

    if value == "sleep_mode":
        return {
            "operation_mode": "cool",
            "temperature": "27",
            "air_volume": "auto",
        }

    return {
        "operation_mode": "cool",
        "temperature": "25",
        "air_volume": "auto",
    }


def control_light(action):
    if not NATURE_REMO_LIGHT_ID:
        return {
            "status": "skipped",
            "message": "NATURE_REMO_LIGHT_ID is missing.",
            "action": action,
        }

    return {
        "status": "skipped",
        "message": "Light signal IDs are not configured yet.",
        "action": action,
    }
