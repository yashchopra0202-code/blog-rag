from types import SimpleNamespace
import fastapi
import pytest
from fastapi.testclient import TestClient
import api

class _FakeDoc:
    def __init__(self, text, meta): self.page_content = text; self.metadata = meta

def test_answer_question_returns_answer_and_dedup_sources(monkeypatch):
    docs = [
        _FakeDoc("ctx one", {"source": "https://x/a", "title": "A", "site": "s"}),
        _FakeDoc("ctx two", {"source": "https://x/a", "title": "A", "site": "s"}),
        _FakeDoc("ctx three", {"source": "https://x/b", "title": "B", "site": "s"}),
    ]
    monkeypatch.setattr(api.os.path, "isdir", lambda p: True)
    monkeypatch.setattr(api.rag_core, "load_index", lambda p: object())
    monkeypatch.setattr(api.rag_core, "get_retriever",
                        lambda store, k=4: SimpleNamespace(invoke=lambda q: docs))
    monkeypatch.setattr(api, "_llm",
                        lambda: SimpleNamespace(invoke=lambda prompt: SimpleNamespace(content="ANSWER")))
    out = api.answer_question("q?")
    assert out["answer"] == "ANSWER"
    assert out["sources"] == [
        {"title": "A", "url": "https://x/a", "site": "s"},
        {"title": "B", "url": "https://x/b", "site": "s"},
    ]

def test_ask_endpoint(monkeypatch):
    monkeypatch.setattr(api, "answer_question", lambda q: {"answer": "OK", "sources": []})
    monkeypatch.setattr(api.store, "rate_limit_ok", lambda bucket, limit: True)
    client = TestClient(api.app)
    r = client.post("/ask", json={"question": "hi"})
    assert r.status_code == 200
    assert r.json()["answer"] == "OK"


def test_ask_rate_limited_per_ip_returns_429(monkeypatch):
    called = {"llm": False}
    monkeypatch.setattr(api, "answer_question",
                        lambda q: called.__setitem__("llm", True) or {"answer": "X", "sources": []})
    monkeypatch.setattr(api.store, "rate_limit_ok", lambda bucket, limit: False)  # per-IP blocks
    client = TestClient(api.app)
    r = client.post("/ask", json={"question": "hi"})
    assert r.status_code == 429
    assert called["llm"] is False  # blocked before the expensive LLM call


def test_ask_global_cap_returns_graceful_and_skips_llm(monkeypatch):
    called = {"llm": False}

    def fake_answer(q):
        called["llm"] = True
        return {"answer": "X", "sources": []}

    monkeypatch.setattr(api, "answer_question", fake_answer)
    # per-IP ok, but the global daily cap is exceeded
    monkeypatch.setattr(api.store, "rate_limit_ok",
                        lambda bucket, limit: not bucket.startswith("ask:global"))
    client = TestClient(api.app)
    r = client.post("/ask", json={"question": "hi"})
    assert r.status_code == 200
    assert r.json().get("capped") is True
    assert called["llm"] is False  # global cap skips the LLM -> no spend


def test_ask_fails_open_when_limiter_errors(monkeypatch):
    def boom(bucket, limit):
        raise RuntimeError("supabase down")

    monkeypatch.setattr(api.store, "rate_limit_ok", boom)
    monkeypatch.setattr(api, "answer_question", lambda q: {"answer": "OK", "sources": []})
    client = TestClient(api.app)
    r = client.post("/ask", json={"question": "hi"})
    assert r.status_code == 200
    assert r.json()["answer"] == "OK"  # limiter outage must not block legit users

def test_ask_endpoint_rejects_empty():
    client = TestClient(api.app)
    r = client.post("/ask", json={"question": "  "})
    assert r.status_code == 400

def test_answer_question_no_index_503(monkeypatch):
    monkeypatch.setattr(api.os.path, "isdir", lambda p: False)
    with pytest.raises(fastapi.HTTPException) as ei:
        api.answer_question("q?")
    assert ei.value.status_code == 503

def test_rag_answer_returns_error_dict_when_no_index(monkeypatch):
    monkeypatch.setattr(api.os.path, "isdir", lambda p: False)
    out = api.rag_answer("anything")
    assert out.get("status") == 503 and "error" in out

def test_feed_groups_filters_and_clamps(monkeypatch, tmp_path):
    import json as _json
    from datetime import datetime, timezone, timedelta
    today = datetime.now(timezone.utc).date().isoformat()
    old = (datetime.now(timezone.utc).date() - timedelta(days=40)).isoformat()
    manifest = {
        "https://x/a": {"title": "A", "site": "anthropic-news",
                        "nugget": "na", "scraped_at": today + "T10:00:00+00:00"},
        "https://x/b": {"title": "B", "site": "openai-index",
                        "scraped_at": today + "T09:00:00+00:00"},  # no nugget -> excluded
        "https://x/c": {"title": "C", "site": "cohere",
                        "nugget": "nc", "scraped_at": old + "T09:00:00+00:00"},  # too old
    }
    mf = tmp_path / "manifest.json"
    mf.write_text(_json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(api, "MANIFEST_PATH", str(mf))
    out = api.feed_data(days=1000)  # clamps to FEED_MAX_DAYS
    assert out["days"] == 30
    assert len(out["groups"]) == 1
    g = out["groups"][0]
    assert g["date"] == today
    assert [i["url"] for i in g["items"]] == ["https://x/a"]
    assert g["items"][0]["label"] == "Anthropic · News"

def test_subscribe_valid_sends_confirmation(monkeypatch):
    sent = {}
    monkeypatch.setattr(api.store, "rate_limit_ok", lambda bucket, limit: True)
    monkeypatch.setattr(api.store, "add_email_subscriber",
                        lambda e: {"email": e, "status": "pending",
                                   "confirm_token": "CT", "unsub_token": "UT"})
    monkeypatch.setattr(api.emailer, "send_email",
                        lambda to, subject, html, **k: sent.update(to=to, html=html))
    client = TestClient(api.app)
    r = client.post("/subscribe", json={"email": "a@b.com"})
    assert r.status_code == 200 and r.json()["ok"] is True
    assert sent["to"] == "a@b.com" and "token=CT" in sent["html"]

def test_subscribe_rejects_bad_email(monkeypatch):
    monkeypatch.setattr(api.store, "rate_limit_ok", lambda bucket, limit: True)
    client = TestClient(api.app)
    r = client.post("/subscribe", json={"email": "not-an-email"})
    assert r.status_code == 400

def test_subscribe_rate_limited(monkeypatch):
    calls = {"sent": 0}
    monkeypatch.setattr(api.store, "rate_limit_ok", lambda bucket, limit: False)
    monkeypatch.setattr(api.emailer, "send_email",
                        lambda *a, **k: calls.__setitem__("sent", calls["sent"] + 1))
    client = TestClient(api.app)
    r = client.post("/subscribe", json={"email": "a@b.com"})
    assert r.status_code == 429 and calls["sent"] == 0

def test_subscribe_no_enumeration_for_existing(monkeypatch):
    sent = {"n": 0}
    monkeypatch.setattr(api.store, "rate_limit_ok", lambda bucket, limit: True)
    monkeypatch.setattr(api.store, "add_email_subscriber",
                        lambda e: {"email": e, "status": "confirmed",
                                   "confirm_token": "CT", "unsub_token": "UT"})
    monkeypatch.setattr(api.emailer, "send_email",
                        lambda *a, **k: sent.__setitem__("n", sent["n"] + 1))
    client = TestClient(api.app)
    r = client.post("/subscribe", json={"email": "a@b.com"})
    assert r.status_code == 200 and r.json()["ok"] is True   # same body as a new sub
    assert sent["n"] == 0   # already confirmed -> no confirmation email re-sent

def test_confirm_endpoint(monkeypatch):
    monkeypatch.setattr(api.store, "confirm_email", lambda t: True)
    client = TestClient(api.app)
    r = client.get("/confirm", params={"token": "CT"})
    assert r.status_code == 200 and "confirmed" in r.text.lower()

def test_unsubscribe_endpoint(monkeypatch):
    monkeypatch.setattr(api.store, "unsubscribe_email", lambda t: True)
    client = TestClient(api.app)
    r = client.get("/unsubscribe", params={"token": "UT"})
    assert r.status_code == 200 and "unsubscribed" in r.text.lower()

def _svix_headers(secret_b64key, body: str):
    import base64, hmac, hashlib
    key = base64.b64decode(secret_b64key)
    sid, ts = "msg_1", "1700000000"
    sig = base64.b64encode(hmac.new(key, f"{sid}.{ts}.{body}".encode(), hashlib.sha256).digest()).decode()
    return {"svix-id": sid, "svix-timestamp": ts, "svix-signature": f"v1,{sig}"}

def test_resend_webhook_marks_bounced(monkeypatch):
    import base64, json as _json
    b64key = base64.b64encode(b"secretkey").decode()
    monkeypatch.setenv("RESEND_WEBHOOK_SECRET", "whsec_" + b64key)
    marked = {}
    monkeypatch.setattr(api.store, "mark_email_status",
                        lambda email, status: marked.update(email=email, status=status))
    body = _json.dumps({"type": "email.bounced", "data": {"to": ["x@y.com"]}})
    client = TestClient(api.app)
    r = client.post("/resend/webhook", content=body, headers=_svix_headers(b64key, body))
    assert r.status_code == 200
    assert marked == {"email": "x@y.com", "status": "bounced"}

def test_resend_webhook_rejects_bad_signature(monkeypatch):
    import base64
    monkeypatch.setenv("RESEND_WEBHOOK_SECRET", "whsec_" + base64.b64encode(b"secretkey").decode())
    client = TestClient(api.app)
    r = client.post("/resend/webhook", content='{"type":"email.bounced"}',
                    headers={"svix-id": "m", "svix-timestamp": "1", "svix-signature": "v1,deadbeef"})
    assert r.status_code == 401

def test_resend_webhook_fails_closed_without_secret(monkeypatch):
    monkeypatch.delenv("RESEND_WEBHOOK_SECRET", raising=False)
    client = TestClient(api.app)
    r = client.post("/resend/webhook", content="{}",
                    headers={"svix-id": "m", "svix-timestamp": "1", "svix-signature": "v1,x"})
    assert r.status_code == 401

def test_index_html_has_subscribe_form():
    with open("static/index.html", encoding="utf-8") as f:
        html = f.read()
    assert 'id="subscribe-form"' in html
    assert "/subscribe" in html

def test_corpus_stats_counts_from_manifest(monkeypatch, tmp_path):
    import json as _json
    manifest = {
        "https://x/a": {"site": "anthropic-news", "scraped_at": "2026-09-07T10:00:00+00:00"},
        "https://x/b": {"site": "anthropic-news", "scraped_at": "2026-09-06T10:00:00+00:00"},
        "https://x/c": {"site": "openai-index", "scraped_at": "2026-09-08T09:00:00+00:00"},
    }
    mf = tmp_path / "manifest.json"
    mf.write_text(_json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(api, "MANIFEST_PATH", str(mf))
    out = api.corpus_stats()
    assert out["articles"] == 3
    counts = {s["name"]: s["count"] for s in out["sites"]}
    assert counts == {"anthropic-news": 2, "openai-index": 1}
    assert out["updated"] == "2026-09-08"
    assert {s["label"] for s in out["sites"]} >= {"Anthropic · News", "OpenAI · Index"}
