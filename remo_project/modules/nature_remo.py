import requests

import time

from config import (
    NATURE_REMO_AIRCON_ID,
    NATURE_REMO_LIGHT_CONTROL_METHOD,
    NATURE_REMO_LIGHT_DAYLIGHT_BUTTON,
    NATURE_REMO_LIGHT_DAYLIGHT_SIGNAL_ID,
    NATURE_REMO_LIGHT_BRIGHT_DOWN_BUTTON,
    NATURE_REMO_LIGHT_BRIGHT_UP_BUTTON,
    NATURE_REMO_LIGHT_ID,
    NATURE_REMO_LIGHT_NIGHT_BUTTON,
    NATURE_REMO_LIGHT_OFF_BUTTON,
    NATURE_REMO_LIGHT_OFF_SIGNAL_ID,
    NATURE_REMO_LIGHT_ON_BUTTON,
    NATURE_REMO_LIGHT_PLANT_BUTTON,
    NATURE_REMO_LIGHT_PLANT_SIGNAL_ID,
    NATURE_REMO_LIGHT_WARM_BUTTON,
    NATURE_REMO_LIGHT_WARM_SIGNAL_ID,
    NATURE_REMO_TOKEN,
)


BASE_URL = "https://api.nature.global/1"
LIGHT_BUTTON_SEQUENCE_DELAY_SECONDS = 0.5


LIGHT_BUTTONS = {
    "on": NATURE_REMO_LIGHT_ON_BUTTON,
    "full_light": NATURE_REMO_LIGHT_PLANT_BUTTON,
    "night": NATURE_REMO_LIGHT_NIGHT_BUTTON,
    "daylight": NATURE_REMO_LIGHT_DAYLIGHT_BUTTON,
    "warm_light": NATURE_REMO_LIGHT_WARM_BUTTON,
    "plant_mode": NATURE_REMO_LIGHT_PLANT_BUTTON,
    "bright_up": NATURE_REMO_LIGHT_BRIGHT_UP_BUTTON,
    "bright_down": NATURE_REMO_LIGHT_BRIGHT_DOWN_BUTTON,
    "off": NATURE_REMO_LIGHT_OFF_BUTTON,
}

LIGHT_BUTTON_SEQUENCES = {
    "daylight": [NATURE_REMO_LIGHT_PLANT_BUTTON, NATURE_REMO_LIGHT_DAYLIGHT_BUTTON],
    "warm_light": [NATURE_REMO_LIGHT_PLANT_BUTTON, NATURE_REMO_LIGHT_WARM_BUTTON],
}

LIGHT_SIGNAL_IDS = {
    "daylight": NATURE_REMO_LIGHT_DAYLIGHT_SIGNAL_ID,
    "warm_light": NATURE_REMO_LIGHT_WARM_SIGNAL_ID,
    "plant_mode": NATURE_REMO_LIGHT_PLANT_SIGNAL_ID,
    "off": NATURE_REMO_LIGHT_OFF_SIGNAL_ID,
}


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

    data = _aircon_payload(action)
    result = _post(f"/appliances/{NATURE_REMO_AIRCON_ID}/aircon_settings", data)
    return {"status": "ok", "action": action, "payload": data, "result": result}


def _aircon_payload(action):
    value = _action_value(action)
    if isinstance(action, dict) and action.get("button"):
        return {"button": action.get("button")}

    if value in ("off", "power_off"):
        return {"button": "power-off"}

    if isinstance(action, dict) and action.get("operation_mode") and action.get("temperature"):
        return {
            "operation_mode": action.get("operation_mode"),
            "temperature": str(action.get("temperature")),
            "air_volume": action.get("air_volume", "auto"),
        }

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
    value = _action_value(action)
    method = NATURE_REMO_LIGHT_CONTROL_METHOD

    if method == "button":
        return _control_light_by_button(value, action)

    if method == "signal":
        return _control_light_by_signal(value, action)

    if method == "auto":
        button_result = _control_light_by_button(value, action)
        if button_result.get("status") != "skipped":
            return button_result
        return _control_light_by_signal(value, action)

    return {
        "status": "skipped",
        "message": f"Unknown light control method: {method}",
        "action": action,
    }


def _control_light_by_button(value, action):
    if not NATURE_REMO_LIGHT_ID:
        return {
            "status": "skipped",
            "message": "NATURE_REMO_LIGHT_ID is missing.",
            "action": action,
        }

    buttons = LIGHT_BUTTON_SEQUENCES.get(value) or [LIGHT_BUTTONS.get(value)]
    if not all(buttons):
        return {
            "status": "skipped",
            "message": f"Light button is missing for {value}.",
            "action": action,
        }

    results = []
    for index, button in enumerate(buttons):
        if index > 0:
            time.sleep(LIGHT_BUTTON_SEQUENCE_DELAY_SECONDS)
        results.append(_post(f"/appliances/{NATURE_REMO_LIGHT_ID}/light", {"button": button}))

    return {
        "status": "ok",
        "method": "button",
        "button": buttons[-1],
        "buttons": buttons,
        "action": action,
        "result": results[-1],
        "results": results,
    }


def _control_light_by_signal(value, action):
    signal_id = LIGHT_SIGNAL_IDS.get(value)
    if not signal_id:
        return {
            "status": "skipped",
            "message": f"Light signal ID is missing for {value}.",
            "action": action,
        }

    result = _post(f"/signals/{signal_id}/send")
    return {
        "status": "ok",
        "method": "signal",
        "signal_id": signal_id,
        "action": action,
        "result": result,
    }


def _action_value(action):
    return action.get("value") if isinstance(action, dict) else action
