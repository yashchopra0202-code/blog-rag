"""One-time: register the Telegram webhook. Run after the app is deployed.
Env: TELEGRAM_BOT_TOKEN, TELEGRAM_WEBHOOK_SECRET, APP_URL (e.g. https://blog-rag.onrender.com)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import telegram_api
from dotenv import load_dotenv

def main():
    load_dotenv()
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    secret = os.environ["TELEGRAM_WEBHOOK_SECRET"]
    base = os.environ.get("APP_URL", os.environ.get("FEED_URL", "")).rstrip("/")
    if not base:
        raise SystemExit("Set APP_URL to your deployed base URL.")
    print(telegram_api.set_webhook(token, f"{base}/telegram/webhook", secret))

if __name__ == "__main__":
    main()
