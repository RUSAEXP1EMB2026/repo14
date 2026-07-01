def judge(settings, sensor_data, weather_data, aircon_action):
    if aircon_action:
        return {
            "value": "announce_aircon",
            "reason": aircon_action.get("reason", "aircon action was selected"),
        }
    return None


def play(action):
    return {
        "status": "skipped",
        "message": "Connect speaker or TTS before enabling audio playback.",
        "action": action,
    }
