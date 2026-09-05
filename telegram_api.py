"""Thin Telegram Bot API client over httpx."""
import httpx

def _call(method, token, payload):
    """POST to the Telegram Bot API; on failure raise an error that does NOT
    contain the token (Telegram puts the token in the URL, and httpx's
    HTTPStatusError would otherwise expose it)."""
    r = httpx.post(f"https://api.telegram.org/bot{token}/{method}", json=payload, timeout=20)
    try:
        r.raise_for_status()
    except Exception:
        raise RuntimeError(f"Telegram {method} failed (HTTP {getattr(r, 'status_code', '?')})") from None
    return r.json()

def send_message(token, chat_id, html):
    return _call("sendMessage", token, {"chat_id": chat_id, "text": html,
                                        "parse_mode": "HTML", "disable_web_page_preview": True})

def set_webhook(token, url, secret):
    return _call("setWebhook", token, {"url": url, "secret_token": secret})
