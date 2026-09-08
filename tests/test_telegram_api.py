import telegram_api

class _Resp:
    def raise_for_status(self): pass
    def json(self): return {"ok": True}

def test_send_message_posts_html(monkeypatch):
    seen = {}
    def fake_post(url, json=None, timeout=None):
        seen.update(url=url, json=json); return _Resp()
    monkeypatch.setattr(telegram_api.httpx, "post", fake_post)
    telegram_api.send_message("TOK", 7, "<b>hi</b>")
    assert seen["url"] == "https://api.telegram.org/botTOK/sendMessage"
    assert seen["json"]["chat_id"] == 7
    assert seen["json"]["parse_mode"] == "HTML"
    assert seen["json"]["disable_web_page_preview"] is True

def test_set_webhook_sends_secret(monkeypatch):
    seen = {}
    def fake_post(url, json=None, timeout=None):
        seen.update(url=url, json=json); return _Resp()
    monkeypatch.setattr(telegram_api.httpx, "post", fake_post)
    telegram_api.set_webhook("TOK", "https://app/telegram/webhook", "sec")
    assert seen["url"].endswith("/botTOK/setWebhook")
    assert seen["json"]["url"] == "https://app/telegram/webhook"
    assert seen["json"]["secret_token"] == "sec"

def test_error_raises_telegramerror_with_status(monkeypatch):
    import pytest
    class _Bad:
        status_code = 403
        def raise_for_status(self): raise RuntimeError("http 403")
        def json(self): return {"ok": False, "error_code": 403, "description": "bot was blocked by the user"}
    monkeypatch.setattr(telegram_api.httpx, "post", lambda *a, **k: _Bad())
    with pytest.raises(telegram_api.TelegramError) as ei:
        telegram_api.send_message("TOK", 7, "hi")
    assert ei.value.status_code == 403
    assert isinstance(ei.value, RuntimeError)   # existing callers that catch Exception still work

def test_error_parses_retry_after_on_429(monkeypatch):
    import pytest
    class _Bad:
        status_code = 429
        def raise_for_status(self): raise RuntimeError("http 429")
        def json(self): return {"ok": False, "error_code": 429, "parameters": {"retry_after": 5}}
    monkeypatch.setattr(telegram_api.httpx, "post", lambda *a, **k: _Bad())
    with pytest.raises(telegram_api.TelegramError) as ei:
        telegram_api.send_message("TOK", 7, "hi")
    assert ei.value.status_code == 429
    assert ei.value.retry_after == 5

def test_send_message_error_does_not_leak_token(monkeypatch):
    import httpx as _httpx, pytest
    class _Bad:
        status_code = 401
        def raise_for_status(self):
            raise _httpx.HTTPStatusError(
                "401 Unauthorized",
                request=_httpx.Request("POST", "https://api.telegram.org/botSECRET123/sendMessage"),
                response=_httpx.Response(401))
        def json(self): return {}
    monkeypatch.setattr(telegram_api.httpx, "post", lambda *a, **k: _Bad())
    with pytest.raises(RuntimeError) as ei:
        telegram_api.send_message("SECRET123", 7, "hi")
    assert "SECRET123" not in str(ei.value)
