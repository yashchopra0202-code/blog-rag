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

def _one_nugget_setup(monkeypatch):
    monkeypatch.setattr(telegram_digest.config, "load_config", lambda: {"cadence": "daily", "enabled_labs": None})
    monkeypatch.setattr(telegram_digest, "load_manifest", lambda p: {
        "u1": {"nugget": "n", "title": "T", "site": "s", "signal": 5, "topic": "Models",
               "scraped_at": "2026-09-06T10:00:00+00:00"}})
    monkeypatch.setattr(telegram_digest.digest, "load_state", lambda p: {})
    monkeypatch.setattr(telegram_digest.digest, "save_state", lambda s, p: None)
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "TOK")

def test_broadcast_deactivates_subscriber_on_403(monkeypatch):
    _one_nugget_setup(monkeypatch)
    monkeypatch.setattr(telegram_digest.store, "active_subscribers", lambda: [{"chat_id": 1}, {"chat_id": 2}])
    deactivated = []
    monkeypatch.setattr(telegram_digest.store, "deactivate_subscriber", lambda cid: deactivated.append(cid))
    def fake_send(tok, cid, html):
        if cid == 2:
            raise telegram_digest.telegram_api.TelegramError("sendMessage", 403)
    monkeypatch.setattr(telegram_digest.telegram_api, "send_message", fake_send)
    out = telegram_digest.broadcast(now=datetime(2026, 9, 6, tzinfo=timezone.utc), sleep=lambda _s: None)
    assert deactivated == [2]
    assert out["sent"] == 1 and out["dropped"] == 1 and out["failed"] == 0

def test_broadcast_retries_once_on_429(monkeypatch):
    _one_nugget_setup(monkeypatch)
    monkeypatch.setattr(telegram_digest.store, "active_subscribers", lambda: [{"chat_id": 1}])
    slept = []
    attempts = {"n": 0}
    def fake_send(tok, cid, html):
        attempts["n"] += 1
        if attempts["n"] == 1:
            raise telegram_digest.telegram_api.TelegramError("sendMessage", 429, retry_after=0)
        # second attempt succeeds
    monkeypatch.setattr(telegram_digest.telegram_api, "send_message", fake_send)
    out = telegram_digest.broadcast(now=datetime(2026, 9, 6, tzinfo=timezone.utc), sleep=lambda s: slept.append(s))
    assert attempts["n"] == 2 and out["sent"] == 1 and out["failed"] == 0
    assert 0 in slept   # honored retry_after

def test_broadcast_paces_between_sends(monkeypatch):
    _one_nugget_setup(monkeypatch)
    monkeypatch.setattr(telegram_digest.store, "active_subscribers", lambda: [{"chat_id": 1}, {"chat_id": 2}, {"chat_id": 3}])
    monkeypatch.setattr(telegram_digest.telegram_api, "send_message", lambda tok, cid, html: None)
    slept = []
    out = telegram_digest.broadcast(now=datetime(2026, 9, 6, tzinfo=timezone.utc),
                                    sleep=lambda s: slept.append(s), delay=0.04)
    assert out["sent"] == 3
    assert slept == [0.04, 0.04]   # paced between the 3 sends (N-1 gaps)

def test_broadcast_no_entries(monkeypatch):
    monkeypatch.setattr(telegram_digest.config, "load_config", lambda: {"cadence": "daily", "enabled_labs": None})
    monkeypatch.setattr(telegram_digest, "load_manifest", lambda p: {})
    monkeypatch.setattr(telegram_digest.digest, "load_state", lambda p: {})
    out = telegram_digest.broadcast(now=datetime(2026, 9, 6, tzinfo=timezone.utc))
    assert out["sent"] == 0 and out["skipped"] is False


def _image_nugget_setup(monkeypatch):
    # Two nuggets; the lower-signal one carries an image (so "first with image" != first entry).
    monkeypatch.setattr(telegram_digest.config, "load_config", lambda: {"cadence": "daily", "enabled_labs": None})
    monkeypatch.setattr(telegram_digest, "load_manifest", lambda p: {
        "u1": {"nugget": "n1", "title": "NoImg", "site": "s", "signal": 5, "topic": "Models",
               "scraped_at": "2026-09-06T10:00:00+00:00"},
        "u2": {"nugget": "n2", "title": "HasImg", "site": "s", "signal": 4, "topic": "Models",
               "scraped_at": "2026-09-06T09:00:00+00:00", "image": "https://img/x.jpg"}})
    monkeypatch.setattr(telegram_digest.digest, "load_state", lambda p: {})
    monkeypatch.setattr(telegram_digest.digest, "save_state", lambda s, p: None)
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "TOK")


def test_broadcast_sends_lead_photo_before_text_when_image_present(monkeypatch):
    _image_nugget_setup(monkeypatch)
    monkeypatch.setattr(telegram_digest.store, "active_subscribers", lambda: [{"chat_id": 1}])
    photos, msgs = [], []
    monkeypatch.setattr(telegram_digest.telegram_api, "send_photo",
                        lambda tok, cid, photo, caption: photos.append((cid, photo)))
    monkeypatch.setattr(telegram_digest.telegram_api, "send_message",
                        lambda tok, cid, html: msgs.append(cid))
    telegram_digest.broadcast(now=datetime(2026, 9, 6, tzinfo=timezone.utc), sleep=lambda _s: None)
    assert photos == [(1, "https://img/x.jpg")]   # the highest-ranked image is sent as a lead photo
    assert msgs == [1]                            # the text digest is still sent


def test_broadcast_no_photo_when_no_image(monkeypatch):
    _one_nugget_setup(monkeypatch)   # u1 has no image
    monkeypatch.setattr(telegram_digest.store, "active_subscribers", lambda: [{"chat_id": 1}])
    photos = []
    monkeypatch.setattr(telegram_digest.telegram_api, "send_photo", lambda *a, **k: photos.append(a))
    monkeypatch.setattr(telegram_digest.telegram_api, "send_message", lambda tok, cid, html: None)
    telegram_digest.broadcast(now=datetime(2026, 9, 6, tzinfo=timezone.utc), sleep=lambda _s: None)
    assert photos == []   # no image anywhere -> no photo call


def test_broadcast_photo_failure_does_not_block_text(monkeypatch):
    _image_nugget_setup(monkeypatch)
    monkeypatch.setattr(telegram_digest.store, "active_subscribers", lambda: [{"chat_id": 1}])
    msgs = []

    def boom(*a, **k):
        raise RuntimeError("photo fetch failed")

    monkeypatch.setattr(telegram_digest.telegram_api, "send_photo", boom)
    monkeypatch.setattr(telegram_digest.telegram_api, "send_message",
                        lambda tok, cid, html: msgs.append(cid))
    out = telegram_digest.broadcast(now=datetime(2026, 9, 6, tzinfo=timezone.utc), sleep=lambda _s: None)
    assert msgs == [1]          # best-effort: photo failure must not block the text digest
    assert out["sent"] == 1
