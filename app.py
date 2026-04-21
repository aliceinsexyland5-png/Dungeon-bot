import os
from flask import Flask, request
import requests
from openai import OpenAI

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = open("system_prompt.txt").read()

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

def send_message(chat_id, text):
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

def get_reply(user_text):
    response = client.responses.create(
        model="gpt-5",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ]
    )
    return response.output_text.strip()

@app.route("/", methods=["GET"])
def home():
    return "Bot is alive."

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" not in data:
        return "ok"

    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if text == "/start":
        send_message(chat_id, "Well... you found me.")
        return "ok"

    if not text:
        return "ok"

    reply = get_reply(text)
    send_message(chat_id, reply)

    return "ok"
