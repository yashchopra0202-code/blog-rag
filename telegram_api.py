"""Thin Telegram Bot API client over httpx."""
import httpx


class TelegramError(RuntimeError):
    """A failed Telegram Bot API call. Carries the HTTP status_code (so callers
    can branch on 403 = blocked, 429 = rate-limited) and retry_after (from a 429
    body) — WITHOUT ever putting the bot token in the message (it's in the URL).
    Subclasses RuntimeError so existing `except Exception`/`except RuntimeError`
    callers keep working unchanged."""
    def __init__(self, method, status_code, retry_after=None):
        super().__init__(f"Telegram {method} failed (HTTP {status_code})")
        self.status_code = status_code
        self.retry_after = retry_after


def _call(method, token, payload):
    """POST to the Telegram Bot API; on failure raise a TelegramError that does
    NOT contain the token, carrying the status code and any 429 retry_after."""
    r = httpx.post(f"https://api.telegram.org/bot{token}/{method}", json=payload, timeout=20)
    try:
        r.raise_for_status()
    except Exception:
        status = getattr(r, "status_code", None)
        retry_after = None
        try:
            retry_after = (r.json().get("parameters") or {}).get("retry_after")
        except Exception:
            pass
        raise TelegramError(method, status, retry_after) from None
    return r.json()

def send_message(token, chat_id, html):
    return _call("sendMessage", token, {"chat_id": chat_id, "text": html,
                                        "parse_mode": "HTML", "disable_web_page_preview": True})

def set_webhook(token, url, secret):
    return _call("setWebhook", token, {"url": url, "secret_token": secret})
