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

def test_add_email_subscriber_inserts_pending_with_tokens(monkeypatch):
    _env(monkeypatch); posted = {}
    def fake_post(url, headers=None, json=None, params=None, timeout=None):
        posted.update(url=url, headers=headers, json=json); return _Resp()
    def fake_get(url, headers=None, params=None, timeout=None):
        return _Resp([{"email": "a@b.com", "status": "pending",
                       "confirm_token": json_tok(posted), "unsub_token": "u"}])
    def json_tok(p): return p["json"]["confirm_token"]
    monkeypatch.setattr(store.httpx, "post", fake_post)
    monkeypatch.setattr(store.httpx, "get", fake_get)
    row = store.add_email_subscriber("A@b.com")
    assert posted["url"].endswith("/rest/v1/email_subscribers")
    assert posted["json"]["email"] == "a@b.com"           # normalized lower
    assert posted["json"]["status"] == "pending"
    assert posted["json"]["confirm_token"] and posted["json"]["unsub_token"]
    assert "ignore-duplicates" in posted["headers"].get("Prefer", "")
    assert row["status"] == "pending"

def test_confirm_email_patches_pending_to_confirmed(monkeypatch):
    _env(monkeypatch); seen = {}
    def fake_patch(url, headers=None, json=None, params=None, timeout=None):
        seen.update(url=url, json=json, params=params, headers=headers)
        return _Resp([{"email": "a@b.com"}])   # representation => matched
    monkeypatch.setattr(store.httpx, "patch", fake_patch)
    assert store.confirm_email("tok") is True
    assert seen["json"]["status"] == "confirmed"
    assert seen["params"]["confirm_token"] == "eq.tok"
    assert seen["params"]["status"] == "eq.pending"

def test_confirm_email_returns_false_when_no_match(monkeypatch):
    _env(monkeypatch)
    monkeypatch.setattr(store.httpx, "patch",
                        lambda *a, **k: _Resp([]))   # nothing matched
    assert store.confirm_email("bad") is False

def test_unsubscribe_email_patches_unsubscribed(monkeypatch):
    _env(monkeypatch); seen = {}
    monkeypatch.setattr(store.httpx, "patch",
                        lambda url, headers=None, json=None, params=None, timeout=None:
                        (seen.update(json=json, params=params), _Resp([{"email": "a@b.com"}]))[1])
    assert store.unsubscribe_email("u") is True
    assert seen["json"] == {"status": "unsubscribed"}
    assert seen["params"]["unsub_token"] == "eq.u"

def test_confirmed_email_subscribers_lists_rows(monkeypatch):
    _env(monkeypatch); seen = {}
    def fake_get(url, headers=None, params=None, timeout=None):
        seen.update(params=params); return _Resp([{"email": "a@b.com", "unsub_token": "u"}])
    monkeypatch.setattr(store.httpx, "get", fake_get)
    rows = store.confirmed_email_subscribers()
    assert rows == [{"email": "a@b.com", "unsub_token": "u"}]
    assert seen["params"]["status"] == "eq.confirmed"

def test_rate_limit_ok_allows_under_and_blocks_over(monkeypatch):
    _env(monkeypatch); state = {"n": 0}
    monkeypatch.setattr(store.httpx, "get",
                        lambda url, headers=None, params=None, timeout=None: _Resp([{"count": state["n"]}] if state["n"] else []))
    def fake_post(url, headers=None, json=None, params=None, timeout=None):
        state["n"] = json["count"]; return _Resp()
    monkeypatch.setattr(store.httpx, "post", fake_post)
    assert store.rate_limit_ok("subscribe:1.2.3.4:2026090812", 2) is True   # 1st -> count 1
    assert store.rate_limit_ok("subscribe:1.2.3.4:2026090812", 2) is True   # 2nd -> count 2
    assert store.rate_limit_ok("subscribe:1.2.3.4:2026090812", 2) is False  # 3rd -> count 3 > 2

def test_digest_guard_get_and_set(monkeypatch):
    _env(monkeypatch); posted = {}
    monkeypatch.setattr(store.httpx, "get",
                        lambda url, headers=None, params=None, timeout=None: _Resp([]))
    monkeypatch.setattr(store.httpx, "post",
                        lambda url, headers=None, json=None, params=None, timeout=None: (posted.update(json=json), _Resp())[1])
    assert store.digest_already_sent("2026-09-08") is False
    store.mark_digest_sent("2026-09-08")
    assert posted["json"]["digest_key"] == "2026-09-08"
