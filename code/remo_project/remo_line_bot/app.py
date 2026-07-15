import base64
import hashlib
import hmac
import os
import re
from datetime import datetime
from pathlib import Path

import gspread
import requests
from dotenv import load_dotenv
from flask import Flask, abort, jsonify, request
from gspread.exceptions import WorksheetNotFound


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(SCRIPT_DIR / ".env", override=True)

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID") or os.getenv("GOOGLE_SPREADSHEET_ID")
GOOGLE_SERVICE_ACCOUNT_JSON = (
    os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    or os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
    or "service_account.json"
)
PORT = int(os.getenv("PORT", "5000"))

WAKE = "\u8d77\u5e8a"
RETURN_HOME = "\u5e30\u5b85"
SLEEP = "\u5c31\u5bdd"
ABSENCE = "\u4e0d\u5728"

TIME_PATTERN = r"((?:[01]?\d|2[0-3]):[0-5]\d|24:00)"

app = Flask(__name__)


def _resolve_path(path_text):
    path = Path(path_text)
    if path.is_absolute():
        return path

    for base_dir in (SCRIPT_DIR, PROJECT_ROOT):
        candidate = base_dir / path
        if candidate.exists():
            return candidate

    return SCRIPT_DIR / path


def verify_signature(body: bytes, signature: str) -> bool:
    if not LINE_CHANNEL_SECRET:
        raise RuntimeError("LINE_CHANNEL_SECRET is not set")

    hash_value = hmac.new(
        LINE_CHANNEL_SECRET.encode("utf-8"),
        body,
        hashlib.sha256,
    ).digest()
    expected_signature = base64.b64encode(hash_value).decode("utf-8")

    return hmac.compare_digest(expected_signature, signature or "")


def get_spreadsheet():
    if not SPREADSHEET_ID:
        raise RuntimeError("SPREADSHEET_ID or GOOGLE_SPREADSHEET_ID is not set")

    service_account_path = _resolve_path(GOOGLE_SERVICE_ACCOUNT_JSON)
    gc = gspread.service_account(filename=str(service_account_path))
    return gc.open_by_key(SPREADSHEET_ID)


def get_or_create_worksheet(ss, name, headers):
    try:
        ws = ss.worksheet(name)
    except WorksheetNotFound:
        ws = ss.add_worksheet(title=name, rows=1000, cols=len(headers))
        ws.append_row(headers)
        return ws

    values = ws.get_all_values()
    if not values:
        ws.append_row(headers)

    return ws


def save_setting(key: str, value: str):
    ss = get_spreadsheet()
    ws = get_or_create_worksheet(
        ss,
        "Settings",
        ["key", "value", "updated_at"],
    )

    rows = ws.get_all_values()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for row_number, row in enumerate(rows[1:], start=2):
        if row and row[0] == key:
            ws.update(f"B{row_number}:C{row_number}", [[value, now]])
            return

    ws.append_row([key, value, now])


def add_command_queue(user_id: str, command: str, value: str):
    ss = get_spreadsheet()
    ws = get_or_create_worksheet(
        ss,
        "CommandQueue",
        ["timestamp", "user_id", "command", "value", "status"],
    )

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ws.append_row([now, user_id, command, value, "PENDING"])


def parse_command(text: str) -> dict:
    command_map = [
        (WAKE, "wake_time"),
        (RETURN_HOME, "return_time"),
        (SLEEP, "sleep_time"),
    ]

    for label, key in command_map:
        match = re.match(rf"^{re.escape(label)}\s+{TIME_PATTERN}$", text)
        if match:
            value = match.group(1)
            return {
                "ok": True,
                "key": key,
                "value": value,
                "message": f"{label}\u6642\u523b\u3092{value}\u306b\u8a2d\u5b9a\u3057\u307e\u3057\u305f\u3002",
            }

    absence_match = re.match(rf"^{re.escape(ABSENCE)}\s+(\d+)$", text)
    if absence_match:
        value = absence_match.group(1)
        return {
            "ok": True,
            "key": "absence_threshold",
            "value": value,
            "message": f"{ABSENCE}\u5224\u5b9a\u6642\u9593\u3092{value}\u5206\u306b\u8a2d\u5b9a\u3057\u307e\u3057\u305f\u3002",
        }

    return {
        "ok": False,
        "message": (
            "\u5165\u529b\u5f62\u5f0f\u304c\u6b63\u3057\u304f\u3042\u308a\u307e\u305b\u3093\u3002\n\n"
            "\u4f8b:\n"
            f"{WAKE} 07:30\n"
            f"{RETURN_HOME} 18:30\n"
            f"{SLEEP} 23:59\n"
            f"{ABSENCE} 180"
        ),
    }


def reply_message(reply_token: str, message: str):
    if not LINE_CHANNEL_ACCESS_TOKEN:
        raise RuntimeError("LINE_CHANNEL_ACCESS_TOKEN is not set")

    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
    }
    payload = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": message}],
    }

    response = requests.post(url, headers=headers, json=payload, timeout=10)
    print("LINE reply status:", response.status_code)
    print("LINE reply body:", response.text)


def handle_text_message(event):
    message = event.get("message", {})
    if message.get("type") != "text":
        return

    user_id = event.get("source", {}).get("userId", "")
    reply_token = event.get("replyToken")
    text = message.get("text", "").strip()
    result = parse_command(text)

    if result["ok"]:
        save_setting(result["key"], result["value"])
        add_command_queue(user_id, result["key"], result["value"])

    if reply_token:
        reply_message(reply_token, result["message"])


@app.get("/health")
def health():
    return "OK", 200


@app.get("/debug/config")
def debug_config():
    service_account_path = _resolve_path(GOOGLE_SERVICE_ACCOUNT_JSON)
    return jsonify(
        {
            "line_channel_secret": bool(LINE_CHANNEL_SECRET),
            "line_channel_access_token": bool(LINE_CHANNEL_ACCESS_TOKEN),
            "spreadsheet_id": bool(SPREADSHEET_ID),
            "service_account_file": str(service_account_path),
            "service_account_exists": service_account_path.exists(),
            "port": PORT,
        }
    )


@app.post("/callback")
def callback():
    body = request.get_data()
    signature = request.headers.get("X-Line-Signature", "")

    if not verify_signature(body, signature):
        print("Invalid signature")
        abort(403)

    try:
        data = request.get_json(force=True)
        events = data.get("events", [])

        if not events:
            return "OK", 200

        for event in events:
            if event.get("type") == "message":
                handle_text_message(event)

        return "OK", 200

    except Exception as exc:
        print("callback error:", exc)
        return "OK", 200


def run_server():
    app.run(port=PORT, debug=False, use_reloader=False)


if __name__ == "__main__":
    run_server()
