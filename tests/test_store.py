import store

class _Resp:
    def __init__(self, data=None, code=200): self._d = data or []; self.status_code = code
    def raise_for_status(self): pass
    def json(self): return self._d

def _env(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://proj.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_KEY", "svc-key")

def test_add_subscriber_upserts(monkeypatch):
    _env(monkeypatch); seen = {}
    def fake_post(url, headers=None, json=None, params=None, timeout=None):
        seen.update(url=url, headers=headers, json=json); return _Resp()
    monkeypatch.setattr(store.httpx, "post", fake_post)
    store.add_subscriber({"id": 7, "first_name": "Yash", "username": "yc"})
    assert seen["url"].endswith("/rest/v1/telegram_subscribers")
    assert seen["json"]["chat_id"] == 7 and seen["json"]["active"] is True
    assert seen["headers"]["Authorization"] == "Bearer svc-key"
    assert "merge-duplicates" in seen["headers"].get("Prefer", "")

def test_deactivate_patches_active_false(monkeypatch):
    _env(monkeypatch); seen = {}
    def fake_patch(url, headers=None, json=None, params=None, timeout=None):
        seen.update(url=url, json=json, params=params); return _Resp()
    monkeypatch.setattr(store.httpx, "patch", fake_patch)
    store.deactivate_subscriber(7)
    assert seen["json"] == {"active": False}
    assert seen["params"]["chat_id"] == "eq.7"

def test_active_subscribers_returns_rows(monkeypatch):
    _env(monkeypatch)
    def fake_get(url, headers=None, params=None, timeout=None):
        return _Resp([{"chat_id": 7}, {"chat_id": 9}])
    monkeypatch.setattr(store.httpx, "get", fake_get)
    assert [r["chat_id"] for r in store.active_subscribers()] == [7, 9]
