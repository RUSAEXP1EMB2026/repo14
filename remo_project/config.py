import os

from dotenv import load_dotenv


load_dotenv()

LOOP_INTERVAL_SECONDS = int(os.getenv("LOOP_INTERVAL_SECONDS", "300"))

GOOGLE_SPREADSHEET_ID = os.getenv("GOOGLE_SPREADSHEET_ID", "")
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "")

NATURE_REMO_TOKEN = os.getenv("NATURE_REMO_TOKEN", "")
NATURE_REMO_AIRCON_ID = os.getenv("NATURE_REMO_AIRCON_ID", "")
NATURE_REMO_LIGHT_ID = os.getenv("NATURE_REMO_LIGHT_ID", "")

OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY", "")
OPENWEATHERMAP_CITY = os.getenv("OPENWEATHERMAP_CITY", "Osaka,jp")

AUDIO_ENABLED = os.getenv("AUDIO_ENABLED", "false").lower() == "true"
ANNOUNCE_FILE = os.getenv("ANNOUNCE_FILE", "announce.mp3")
