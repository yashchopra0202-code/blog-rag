"""Thin Telegram Bot API client over httpx."""
import httpx

def _base(token):
    return f"https://api.telegram.org/bot{token}"

def send_message(token, chat_id, html):
    r = httpx.post(f"{_base(token)}/sendMessage",
                   json={"chat_id": chat_id, "text": html, "parse_mode": "HTML",
                         "disable_web_page_preview": True}, timeout=20)
    r.raise_for_status()
    return r.json()

def set_webhook(token, url, secret):
    r = httpx.post(f"{_base(token)}/setWebhook",
                   json={"url": url, "secret_token": secret}, timeout=20)
    r.raise_for_status()
    return r.json()
