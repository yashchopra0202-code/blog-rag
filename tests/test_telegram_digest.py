from datetime import datetime, timezone
import telegram_digest

def test_broadcast_skips_when_not_send_day(monkeypatch):
    monkeypatch.setattr(telegram_digest.config, "load_config", lambda: {"cadence": "weekly", "weekly_day": "mon"})
    tue = datetime(2026, 9, 8, tzinfo=timezone.utc)
    out = telegram_digest.broadcast(now=tue)
    assert out["skipped"] is True and out["sent"] == 0

def test_broadcast_sends_to_each_subscriber_best_effort(monkeypatch):
    monkeypatch.setattr(telegram_digest.config, "load_config", lambda: {"cadence": "daily", "enabled_labs": None})
    monkeypatch.setattr(telegram_digest, "load_manifest", lambda p: {
        "u1": {"nugget": "n", "title": "T", "site": "s", "signal": 5, "topic": "Models",
               "scraped_at": "2026-09-06T10:00:00+00:00"}})
    monkeypatch.setattr(telegram_digest.digest, "load_state", lambda p: {})
    monkeypatch.setattr(telegram_digest.digest, "save_state", lambda s, p: None)
    monkeypatch.setattr(telegram_digest.store, "active_subscribers", lambda: [{"chat_id": 1}, {"chat_id": 2}, {"chat_id": 3}])
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "TOK")
    calls = []
    def fake_send(tok, cid, html):
        if cid == 2: raise RuntimeError("blocked")   # one recipient fails
        calls.append(cid)
    monkeypatch.setattr(telegram_digest.telegram_api, "send_message", fake_send)
    out = telegram_digest.broadcast(now=datetime(2026, 9, 6, tzinfo=timezone.utc))
    assert out["sent"] == 2 and out["failed"] == 1   # 1 and 3 sent, 2 failed but didn't abort

def test_broadcast_no_entries(monkeypatch):
    monkeypatch.setattr(telegram_digest.config, "load_config", lambda: {"cadence": "daily", "enabled_labs": None})
    monkeypatch.setattr(telegram_digest, "load_manifest", lambda p: {})
    monkeypatch.setattr(telegram_digest.digest, "load_state", lambda p: {})
    out = telegram_digest.broadcast(now=datetime(2026, 9, 6, tzinfo=timezone.utc))
    assert out["sent"] == 0 and out["skipped"] is False
