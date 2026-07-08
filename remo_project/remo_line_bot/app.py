import os
import re
import hmac
import base64
import hashlib
from datetime import datetime

import gspread
import requests
from dotenv import load_dotenv
from flask import Flask, abort, request
from gspread.exceptions import WorksheetNotFound


load_dotenv()

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv(
    "GOOGLE_SERVICE_ACCOUNT_JSON",
    "service_account.json",
)
PORT = int(os.getenv("PORT", "5000"))

app = Flask(__name__)


def verify_signature(body: bytes, signature: str) -> bool:
    """LINEから届いたWebhookかどうかを確認する。"""
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
        raise RuntimeError("SPREADSHEET_ID is not set")

    gc = gspread.service_account(filename=GOOGLE_SERVICE_ACCOUNT_JSON)
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

    for i, row in enumerate(rows[1:], start=2):
        if row and row[0] == key:
            ws.update(f"B{i}:C{i}", [[value, now]])
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
    """
    LINEから届いた文章を設定コマンドとして解析する。

    例:
    起床 07:30
    帰宅 18:30
    就寝 24:00
    不在 180
    """
    time_pattern = r"((?:[01]?\d|2[0-3]):[0-5]\d|24:00)"

    wake_match = re.match(rf"^起床\s+{time_pattern}$", text)
    if wake_match:
        value = wake_match.group(1)
        return {
            "ok": True,
            "key": "wake_time",
            "value": value,
            "message": f"起床時刻を{value}に設定しました。",
        }

    return_match = re.match(rf"^帰宅\s+{time_pattern}$", text)
    if return_match:
        value = return_match.group(1)
        return {
            "ok": True,
            "key": "return_time",
            "value": value,
            "message": f"帰宅時刻を{value}に設定しました。",
        }

    sleep_match = re.match(rf"^就寝\s+{time_pattern}$", text)
    if sleep_match:
        value = sleep_match.group(1)
        return {
            "ok": True,
            "key": "sleep_time",
            "value": value,
            "message": f"就寝時刻を{value}に設定しました。",
        }

    absence_match = re.match(r"^不在\s+(\d+)$", text)
    if absence_match:
        value = absence_match.group(1)
        return {
            "ok": True,
            "key": "absence_threshold",
            "value": value,
            "message": f"不在判定時間を{value}分に設定しました。",
        }

    return {
        "ok": False,
        "message": (
            "入力形式が正しくありません。\n\n"
            "例:\n"
            "起床 07:30\n"
            "帰宅 18:30\n"
            "就寝 24:00\n"
            "不在 180"
        ),
    }


def reply_message(reply_token: str, message: str):
    """LINEにテキストメッセージを返信する。"""
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


if __name__ == "__main__":
    app.run(port=PORT, debug=True)
