# Email Subscription (Phase 2) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the single-recipient email digest into a public double-opt-in subscription: a subscribe box, `/subscribe` `/confirm` `/unsubscribe` endpoints, a Resend bounce webhook, `email_subscribers`/`rate_limits`/`sent_digests` in Supabase, and a per-recipient digest send guarded against double-sends.

**Architecture:** Extend the existing FastAPI app + `store.py` PostgREST pattern. A new `emailer.py` isolates the Resend send (reused by the digest and the transactional confirmation email). `store.py` gains email-subscriber, rate-limit, and digest-guard helpers. `api.py` gains four endpoints. `digest.py` switches from one `DIGEST_TO` address to iterating confirmed subscribers, guarded by a durable `sent_digests[<utc-date>]` record. Everything is unit/integration-tested with monkeypatched `httpx`/`store`/`emailer`; real delivery is owner-only until a sending domain is verified (deferred).

**Tech Stack:** Python 3.12, FastAPI, httpx (Resend + Supabase PostgREST), stdlib `secrets`/`hmac`/`hashlib`/`base64`, pytest.

**Spec:** `docs/superpowers/specs/2026-09-08-blog-rag-email-subscription-design.md`

## Global Constraints

- **Python 3.12; NO new dependencies** — only `httpx`, `fastapi`, and stdlib.
- **Test gate command:** `.venv/bin/python -m pytest -q --ignore=tests/test_extraction.py` — must stay green (baseline 89 tests; this plan adds more).
- **Tests require no secrets** — all network (`httpx`) is monkeypatched; Supabase env is set via `monkeypatch.setenv` in tests.
- **Supabase access pattern (match `store.py`):** PostgREST over `httpx` with `SUPABASE_URL` + `SUPABASE_SERVICE_KEY`, headers `{"apikey": key, "Authorization": "Bearer "+key, "Content-Type":"application/json"}`. Never add `supabase-py`.
- **No enumeration:** `/subscribe` returns the same success body whether the address is new, pending, or already confirmed.
- **Fail-closed auth:** the Resend webhook rejects (401) when the signing secret is unset or the signature is invalid — same discipline as the Telegram webhook.
- **Tokens:** `secrets.token_urlsafe(32)`.
- **Public launch is deferred** — build against the sandbox sender; no verified-domain assumptions in code (sender comes from `DIGEST_FROM`, default `onboarding@resend.dev`).
- **Commit trailer** on every commit body:
  `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`
  `Claude-Session: https://claude.ai/code/session_01TQ1fNc6CoWAnrjCSMC2fNn`
- **Branch:** feature branch `feat/email-subscription`, not `main`.

## File structure

- **`emailer.py`** (new) — Resend send + transactional HTML builders. One responsibility: composing/sending email.
- **`store.py`** (extend) — the Supabase data-access layer; add email-subscriber, rate-limit, digest-guard helpers grouped by table.
- **`api.py`** (extend) — four thin HTTP endpoints delegating to `store`/`emailer`.
- **`digest.py`** (change) — per-recipient send + idempotency guard + unsubscribe footer; `send_digest` delegates its Resend call to `emailer`.
- **`static/index.html`** (extend) — a subscribe box + small POST handler.
- **`.env.example`** (extend) — document new env vars.

---

### Task 1: `emailer.py` — isolate the Resend send + transactional HTML

**Files:**
- Create: `emailer.py`
- Create: `tests/test_emailer.py`
- Modify: `digest.py` (`send_digest` delegates to `emailer.send_email`; move `RESEND_ENDPOINT`)

**Interfaces:**
- Produces:
  - `emailer.send_email(to: str, subject: str, html: str, attachments: list | None = None, api_key: str | None = None, sender: str | None = None) -> dict` — POSTs to Resend; `api_key` defaults to `os.getenv("RESEND_API_KEY")`, `sender` to `os.getenv("DIGEST_FROM", "onboarding@resend.dev")`; raises on HTTP error; returns `resp.json()`.
  - `emailer.confirmation_html(confirm_url: str) -> str`
  - `emailer.unsubscribe_footer(unsub_url: str) -> str`
  - `emailer.RESEND_ENDPOINT` constant.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_emailer.py`:

```python
import emailer

class _Resp:
    def raise_for_status(self): pass
    def json(self): return {"id": "e1"}

def test_send_email_posts_to_resend(monkeypatch):
    seen = {}
    def fake_post(url, headers=None, json=None, timeout=None):
        seen.update(url=url, headers=headers, json=json); return _Resp()
    monkeypatch.setattr(emailer.httpx, "post", fake_post)
    out = emailer.send_email("to@x.com", "Subj", "<b>hi</b>", api_key="k", sender="from@x.com")
    assert out == {"id": "e1"}
    assert seen["url"] == emailer.RESEND_ENDPOINT
    assert seen["headers"]["Authorization"] == "Bearer k"
    assert seen["json"]["from"] == "from@x.com"
    assert seen["json"]["to"] == ["to@x.com"]
    assert seen["json"]["subject"] == "Subj"

def test_send_email_defaults_sender_and_key(monkeypatch):
    monkeypatch.setenv("RESEND_API_KEY", "envkey")
    monkeypatch.delenv("DIGEST_FROM", raising=False)
    seen = {}
    monkeypatch.setattr(emailer.httpx, "post",
                        lambda url, headers=None, json=None, timeout=None: (seen.update(headers=headers, json=json), _Resp())[1])
    emailer.send_email("a@b.com", "S", "<p>x</p>")
    assert seen["headers"]["Authorization"] == "Bearer envkey"
    assert seen["json"]["from"] == "onboarding@resend.dev"

def test_confirmation_html_contains_and_escapes_url():
    html = emailer.confirmation_html("https://app/confirm?token=abc&x=1")
    assert "https://app/confirm?token=abc&amp;x=1" in html   # & escaped
    assert "Confirm" in html

def test_unsubscribe_footer_contains_link():
    foot = emailer.unsubscribe_footer("https://app/unsubscribe?token=zzz")
    assert "https://app/unsubscribe?token=zzz" in foot
    assert "unsubscribe" in foot.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_emailer.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'emailer'`.

- [ ] **Step 3: Create `emailer.py`**

```python
"""Send transactional + digest emails via Resend (HTTP, over httpx — no SDK).
Isolated so the digest and the subscribe-confirmation flow share one sender."""
import os
import httpx

RESEND_ENDPOINT = "https://api.resend.com/emails"


def _esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def send_email(to, subject, html, attachments=None, api_key=None, sender=None):
    api_key = api_key or os.getenv("RESEND_API_KEY")
    sender = sender or os.getenv("DIGEST_FROM", "onboarding@resend.dev")
    payload = {"from": sender, "to": [to], "subject": subject, "html": html}
    if attachments:
        payload["attachments"] = attachments
    resp = httpx.post(RESEND_ENDPOINT,
                      headers={"Authorization": f"Bearer {api_key}"},
                      json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def confirmation_html(confirm_url: str) -> str:
    u = _esc(confirm_url)
    return (
        '<div style="font-family:-apple-system,Segoe UI,sans-serif;max-width:520px;'
        'color:#15201A;font-size:15px;line-height:1.6">'
        '<h2 style="color:#0A5F4E">Confirm your subscription</h2>'
        '<p>Someone (hopefully you) subscribed this address to the daily AI-labs digest. '
        'Confirm to start receiving it:</p>'
        f'<p><a href="{u}" style="background:#0E7C66;color:#fff;text-decoration:none;'
        'padding:10px 18px;border-radius:10px;font-weight:600;display:inline-block">'
        'Confirm subscription</a></p>'
        '<p style="color:#7C867E;font-size:13px">If it wasn\'t you, just ignore this email — '
        'you won\'t be subscribed.</p></div>')


def unsubscribe_footer(unsub_url: str) -> str:
    u = _esc(unsub_url)
    return (
        '<div style="margin-top:22px;padding-top:14px;border-top:1px solid #E3E5DC;'
        'color:#7C867E;font-size:12px;line-height:1.5">'
        f'You\'re receiving this because you subscribed. <a href="{u}" '
        'style="color:#0A5F4E">Unsubscribe</a>.</div>')
```

- [ ] **Step 4: Point `digest.send_digest` at `emailer` (keep its signature)**

In `digest.py`, add `import emailer` at the top, and replace the body of `send_digest` with a delegation (keep the exact signature so existing callers/tests are unaffected):

```python
def send_digest(subject, html, api_key, sender, to, attachments=None):
    return emailer.send_email(to, subject, html, attachments=attachments,
                              api_key=api_key, sender=sender)
```

Leave `RESEND_ENDPOINT` in `digest.py` if other code references it; it is now also `emailer.RESEND_ENDPOINT`. (If nothing else uses `digest.RESEND_ENDPOINT`, you may remove it — grep first: `grep -rn "digest.RESEND_ENDPOINT\|RESEND_ENDPOINT" --include=*.py .`)

- [ ] **Step 5: Run the emailer tests + the digest suite**

Run: `.venv/bin/python -m pytest tests/test_emailer.py tests/test_digest.py -v`
Expected: PASS — new emailer tests green; existing digest tests still green (delegation preserves behavior).

- [ ] **Step 6: Commit**

```bash
git add emailer.py tests/test_emailer.py digest.py
git commit -m "$(cat <<'EOF'
feat(email): add emailer.py (Resend send + transactional HTML)

Extracts the Resend HTTP call out of digest.send_digest into a shared
emailer.send_email, plus confirmation_html and unsubscribe_footer builders
for the subscription flow. digest.send_digest now delegates to it.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01TQ1fNc6CoWAnrjCSMC2fNn
EOF
)"
```

---

### Task 2: `store.py` — email-subscriber, rate-limit, and digest-guard helpers

**Files:**
- Modify: `store.py`
- Modify: `tests/test_store.py`

**Interfaces:**
- Consumes: existing `store._conf()` returning `(url, headers)` (present in `store.py`).
- Produces:
  - `store.add_email_subscriber(email: str) -> dict` — returns the row `{"email","status","confirm_token","unsub_token"}`. Inserts a `pending` row with fresh tokens if the email is new (`Prefer: resolution=ignore-duplicates,return=representation`), then GETs the row so callers see the *current* status (an already-`confirmed` address is not downgraded).
  - `store.confirm_email(token: str) -> bool` — PATCH `status=confirmed, confirmed_at=now` where `confirm_token=eq.<token>` and `status=eq.pending`; returns whether a row matched.
  - `store.unsubscribe_email(token: str) -> bool` — PATCH `status=unsubscribed` where `unsub_token=eq.<token>`; returns whether a row matched.
  - `store.confirmed_email_subscribers() -> list[dict]` — GET `select=email,unsub_token` where `status=eq.confirmed`.
  - `store.mark_email_status(email: str, status: str) -> None` — PATCH `status` where `email=eq.<email>`.
  - `store.rate_limit_ok(bucket: str, limit: int) -> bool` — fixed-window counter; increments `count` for `bucket`, returns `True` while `count <= limit`, else `False`.
  - `store.digest_already_sent(key: str) -> bool` — GET `sent_digests` where `digest_key=eq.<key>`; truthy if any row.
  - `store.mark_digest_sent(key: str) -> None` — POST `{digest_key, sent_at}` (ignore-duplicates).
  - Constants `EMAIL_TABLE="email_subscribers"`, `RL_TABLE="rate_limits"`, `SENT_TABLE="sent_digests"`.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_store.py` (reuse the file's existing `_Resp` and `_env` helpers):

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_store.py -v`
Expected: FAIL — the new `store.add_email_subscriber` etc. don't exist (`AttributeError`).

- [ ] **Step 3: Add the helpers to `store.py`**

Append to `store.py` (after the existing telegram helpers):

```python
import secrets
from datetime import datetime, timezone

EMAIL_TABLE = "email_subscribers"
RL_TABLE = "rate_limits"
SENT_TABLE = "sent_digests"


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# --- email subscribers ------------------------------------------------------

def add_email_subscriber(email):
    """Insert a pending subscriber (ignore if already present), then return the
    current row so callers never downgrade an already-confirmed address."""
    email = email.strip().lower()
    url, headers = _conf()
    ins = {**headers, "Prefer": "resolution=ignore-duplicates,return=representation"}
    row = {"email": email, "status": "pending",
           "confirm_token": secrets.token_urlsafe(32),
           "unsub_token": secrets.token_urlsafe(32)}
    httpx.post(f"{url}/rest/v1/{EMAIL_TABLE}", headers=ins, json=row, timeout=15).raise_for_status()
    r = httpx.get(f"{url}/rest/v1/{EMAIL_TABLE}", headers=headers,
                  params={"email": f"eq.{email}",
                          "select": "email,status,confirm_token,unsub_token"}, timeout=15)
    r.raise_for_status()
    rows = r.json()
    return rows[0] if rows else row


def confirm_email(token):
    url, headers = _conf()
    h = {**headers, "Prefer": "return=representation"}
    r = httpx.patch(f"{url}/rest/v1/{EMAIL_TABLE}", headers=h,
                    json={"status": "confirmed", "confirmed_at": _now()},
                    params={"confirm_token": f"eq.{token}", "status": "eq.pending"}, timeout=15)
    r.raise_for_status()
    return bool(r.json())


def unsubscribe_email(token):
    url, headers = _conf()
    h = {**headers, "Prefer": "return=representation"}
    r = httpx.patch(f"{url}/rest/v1/{EMAIL_TABLE}", headers=h,
                    json={"status": "unsubscribed"},
                    params={"unsub_token": f"eq.{token}"}, timeout=15)
    r.raise_for_status()
    return bool(r.json())


def confirmed_email_subscribers():
    url, headers = _conf()
    r = httpx.get(f"{url}/rest/v1/{EMAIL_TABLE}", headers=headers,
                  params={"status": "eq.confirmed", "select": "email,unsub_token"}, timeout=15)
    r.raise_for_status()
    return r.json()


def mark_email_status(email, status):
    url, headers = _conf()
    httpx.patch(f"{url}/rest/v1/{EMAIL_TABLE}", headers=headers,
                json={"status": status},
                params={"email": f"eq.{email.strip().lower()}"}, timeout=15).raise_for_status()


# --- rate limit (fixed window) ----------------------------------------------

def rate_limit_ok(bucket, limit):
    """Increment the counter for `bucket` and return True while count <= limit.
    Read-then-upsert; racy under heavy concurrency but fine at this scale."""
    url, headers = _conf()
    r = httpx.get(f"{url}/rest/v1/{RL_TABLE}", headers=headers,
                  params={"bucket": f"eq.{bucket}", "select": "count"}, timeout=15)
    r.raise_for_status()
    rows = r.json()
    count = (rows[0]["count"] if rows else 0) + 1
    up = {**headers, "Prefer": "resolution=merge-duplicates"}
    httpx.post(f"{url}/rest/v1/{RL_TABLE}", headers=up,
               json={"bucket": bucket, "count": count, "window_start": _now()},
               timeout=15).raise_for_status()
    return count <= limit


# --- digest idempotency guard -----------------------------------------------

def digest_already_sent(key):
    url, headers = _conf()
    r = httpx.get(f"{url}/rest/v1/{SENT_TABLE}", headers=headers,
                  params={"digest_key": f"eq.{key}", "select": "digest_key"}, timeout=15)
    r.raise_for_status()
    return bool(r.json())


def mark_digest_sent(key):
    url, headers = _conf()
    h = {**headers, "Prefer": "resolution=ignore-duplicates"}
    httpx.post(f"{url}/rest/v1/{SENT_TABLE}", headers=h,
               json={"digest_key": key, "sent_at": _now()}, timeout=15).raise_for_status()
```

- [ ] **Step 4: Run the store tests**

Run: `.venv/bin/python -m pytest tests/test_store.py -v`
Expected: PASS — all new store tests green, existing telegram-subscriber tests unchanged.

- [ ] **Step 5: Commit**

```bash
git add store.py tests/test_store.py
git commit -m "$(cat <<'EOF'
feat(store): email-subscriber, rate-limit, and digest-guard helpers

Adds Supabase (PostgREST/httpx) helpers for email_subscribers (add/confirm/
unsubscribe/list/mark), a fixed-window rate_limit_ok, and the sent_digests
idempotency guard. No new dependency.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01TQ1fNc6CoWAnrjCSMC2fNn
EOF
)"
```

---

### Task 3: `api.py` — `/subscribe`, `/confirm`, `/unsubscribe`

**Files:**
- Modify: `api.py`
- Modify: `tests/test_api.py`

**Interfaces:**
- Consumes: `store.add_email_subscriber`, `store.confirm_email`, `store.unsubscribe_email`, `store.rate_limit_ok` (Task 2); `emailer.send_email`, `emailer.confirmation_html` (Task 1).
- Produces: routes `POST /subscribe`, `GET /confirm`, `GET /unsubscribe`; module-level `SUBSCRIBE_LIMIT = 5`; helper `_valid_email(s) -> bool`; `_base_url(request) -> str`.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_api.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_api.py -k "subscribe or confirm or unsubscribe" -v`
Expected: FAIL — routes 404 / `api.emailer` attribute missing.

- [ ] **Step 3: Implement the endpoints in `api.py`**

Add near the other imports: `import re`, `import emailer`. Add `from fastapi.responses import HTMLResponse` to the existing `fastapi.responses` import line.

Add after the `Ask` model / near the other routes:

```python
SUBSCRIBE_LIMIT = 5   # confirmation-email attempts per IP per hour
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Subscribe(BaseModel):
    email: str


def _valid_email(s: str) -> bool:
    return bool(_EMAIL_RE.match((s or "").strip()))


def _base_url(request: Request) -> str:
    # PUBLIC_BASE_URL (or FEED_URL) in prod; fall back to the request's own base.
    return (os.getenv("PUBLIC_BASE_URL") or os.getenv("FEED_URL")
            or str(request.base_url)).rstrip("/")


def _page(title: str, body: str) -> HTMLResponse:
    return HTMLResponse(
        '<!doctype html><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<div style="font-family:-apple-system,Segoe UI,sans-serif;max-width:520px;'
        'margin:12vh auto;padding:0 20px;color:#15201A;text-align:center">'
        f'<h1 style="color:#0A5F4E">{title}</h1><p>{body}</p>'
        '<p><a href="/" style="color:#0A5F4E">← Back to blog-rag</a></p></div>')


@app.post("/subscribe")
def subscribe(payload: Subscribe, request: Request):
    email = (payload.email or "").strip().lower()
    if not _valid_email(email):
        raise HTTPException(status_code=400, detail="Enter a valid email address.")
    ip = request.client.host if request.client else "unknown"
    bucket = f"subscribe:{ip}:{datetime.now(timezone.utc):%Y%m%d%H}"
    try:
        allowed = store.rate_limit_ok(bucket, SUBSCRIBE_LIMIT)
    except Exception:
        allowed = True   # never let a limiter outage block a legit signup
    if not allowed:
        raise HTTPException(status_code=429, detail="Too many attempts. Try again later.")
    try:
        row = store.add_email_subscriber(email)
        if row.get("status") == "pending":
            url = f'{_base_url(request)}/confirm?token={row["confirm_token"]}'
            emailer.send_email(email, "Confirm your blog-rag subscription",
                               emailer.confirmation_html(url))
    except Exception:
        print("subscribe: store/email failed")   # generic success regardless (no enumeration)
    return {"ok": True, "message": "Check your inbox to confirm your subscription."}


@app.get("/confirm")
def confirm(token: str):
    try:
        ok = store.confirm_email(token)
    except Exception:
        ok = False
    if ok:
        return _page("Subscription confirmed", "You'll get the daily AI-labs digest. 🎉")
    return _page("Link expired or already confirmed",
                 "This confirmation link is no longer valid. If you already confirmed, you're all set.")


@app.get("/unsubscribe")
def unsubscribe(token: str):
    try:
        store.unsubscribe_email(token)
    except Exception:
        pass
    return _page("Unsubscribed", "You won't receive the digest anymore. You can re-subscribe any time.")
```

- [ ] **Step 4: Run the endpoint tests + full gate**

Run: `.venv/bin/python -m pytest tests/test_api.py -v && .venv/bin/python -m pytest -q --ignore=tests/test_extraction.py`
Expected: PASS — new subscribe/confirm/unsubscribe tests green; whole suite green.

- [ ] **Step 5: Commit**

```bash
git add api.py tests/test_api.py
git commit -m "$(cat <<'EOF'
feat(api): public subscribe / confirm / unsubscribe endpoints

POST /subscribe (email-validated, per-IP rate-limited, generic response to
avoid enumeration) sends a double-opt-in confirmation; GET /confirm and
GET /unsubscribe flip status and return small styled pages.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01TQ1fNc6CoWAnrjCSMC2fNn
EOF
)"
```

---

### Task 4: `api.py` — Resend bounce/complaint webhook (`POST /resend/webhook`)

**Files:**
- Modify: `api.py`
- Modify: `tests/test_api.py`

**Interfaces:**
- Consumes: `store.mark_email_status(email, status)` (Task 2).
- Produces: route `POST /resend/webhook`; helper `_verify_svix(secret, svix_id, svix_ts, svix_sig, body) -> bool`.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_api.py` (top-level imports `import base64, hmac, hashlib, json` as needed — add any missing):

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_api.py -k resend -v`
Expected: FAIL — route 404.

- [ ] **Step 3: Implement the webhook in `api.py`**

Add `import base64` and `import hashlib` to the imports (`hmac` and `json` are already imported). Add:

```python
def _verify_svix(secret, svix_id, svix_ts, svix_sig, body):
    """Verify a Resend (Svix) webhook signature. Fail-closed on any gap."""
    if not (secret and svix_id and svix_ts and svix_sig):
        return False
    try:
        key = base64.b64decode(secret.split("_", 1)[1] if "_" in secret else secret)
    except Exception:
        return False
    expected = base64.b64encode(
        hmac.new(key, f"{svix_id}.{svix_ts}.{body}".encode(), hashlib.sha256).digest()).decode()
    for part in svix_sig.split():           # space-separated "v1,<sig>" tokens
        _, _, sig = part.partition(",")
        if sig and hmac.compare_digest(sig, expected):
            return True
    return False


_RESEND_STATUS = {"email.bounced": "bounced", "email.complained": "complained"}


@app.post("/resend/webhook")
async def resend_webhook(request: Request):
    secret = os.getenv("RESEND_WEBHOOK_SECRET")
    raw = (await request.body()).decode("utf-8")
    if not _verify_svix(secret, request.headers.get("svix-id", ""),
                        request.headers.get("svix-timestamp", ""),
                        request.headers.get("svix-signature", ""), raw):
        raise HTTPException(status_code=401, detail="bad signature")
    try:
        event = json.loads(raw or "{}")
    except ValueError:
        return {"ok": True}
    status = _RESEND_STATUS.get(event.get("type", ""))
    data = event.get("data") or {}
    recips = data.get("to") or ([data["email"]] if data.get("email") else [])
    if status:
        for e in recips:
            try:
                store.mark_email_status(e, status)
            except Exception:
                print("resend webhook: mark_email_status failed")
    return {"ok": True}
```

- [ ] **Step 4: Run the webhook tests + full gate**

Run: `.venv/bin/python -m pytest tests/test_api.py -k resend -v && .venv/bin/python -m pytest -q --ignore=tests/test_extraction.py`
Expected: PASS — signature verify (valid → mark; invalid/unset → 401); whole suite green.

- [ ] **Step 5: Commit**

```bash
git add api.py tests/test_api.py
git commit -m "$(cat <<'EOF'
feat(api): Resend bounce/complaint webhook, signature-verified

POST /resend/webhook verifies the Svix signature fail-closed and marks
bounced/complained addresses so they're skipped on the next send.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01TQ1fNc6CoWAnrjCSMC2fNn
EOF
)"
```

---

### Task 5: `digest.py` — per-recipient send + idempotency guard + unsubscribe footer

**Files:**
- Modify: `digest.py`
- Modify: `tests/test_digest.py`

**Interfaces:**
- Consumes: `store.confirmed_email_subscribers`, `store.digest_already_sent`, `store.mark_digest_sent` (Task 2); `emailer.send_email`, `emailer.unsubscribe_footer` (Task 1); existing `digest.banner_attachment`, `digest.build_digest`, `digest.select_new_entries`, `digest.curate`, `digest.effective_since`, `digest.load_state`/`save_state`.
- Produces:
  - `digest.broadcast_email(subject, html, recipients, banner=None) -> dict` where `recipients` is `[{"email","unsub_url"}]` (`unsub_url` may be `None`); returns `{"sent","failed"}`; best-effort per recipient; appends the unsubscribe footer when `unsub_url` is set.
  - `digest.deliver_if_new(key, subject, html, recipients, banner=None) -> dict` — returns `{"skipped": True}` when `store.digest_already_sent(key)`; otherwise broadcasts, then `store.mark_digest_sent(key)`, and returns the broadcast result.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_digest.py`:

```python
import store as _store  # for monkeypatching in these tests

def test_broadcast_email_best_effort_and_footer(monkeypatch):
    calls = []
    def fake_send(to, subject, html, attachments=None, **k):
        if to == "boom@x.com":
            raise RuntimeError("bounce")
        calls.append((to, html))
    monkeypatch.setattr(digest.emailer, "send_email", fake_send)
    recipients = [
        {"email": "a@x.com", "unsub_url": "https://app/unsubscribe?token=A"},
        {"email": "boom@x.com", "unsub_url": "https://app/unsubscribe?token=B"},
        {"email": "c@x.com", "unsub_url": None},
    ]
    out = digest.broadcast_email("Subj", "<p>body</p>", recipients)
    assert out == {"sent": 2, "failed": 1}
    a_html = dict(calls)["a@x.com"]
    assert "unsubscribe?token=A" in a_html          # footer appended
    assert "unsubscribe" not in dict(calls)["c@x.com"].lower()  # no footer when no token

def test_deliver_if_new_skips_when_already_sent(monkeypatch):
    monkeypatch.setattr(digest.store, "digest_already_sent", lambda k: True)
    sent = {"n": 0}
    monkeypatch.setattr(digest, "broadcast_email",
                        lambda *a, **k: sent.__setitem__("n", sent["n"] + 1))
    out = digest.deliver_if_new("2026-09-08", "S", "<p>x</p>", [{"email": "a@x.com", "unsub_url": None}])
    assert out == {"skipped": True} and sent["n"] == 0

def test_deliver_if_new_sends_and_marks(monkeypatch):
    monkeypatch.setattr(digest.store, "digest_already_sent", lambda k: False)
    marked = {}
    monkeypatch.setattr(digest.store, "mark_digest_sent", lambda k: marked.update(k=k))
    monkeypatch.setattr(digest, "broadcast_email", lambda *a, **k: {"sent": 1, "failed": 0})
    out = digest.deliver_if_new("2026-09-08", "S", "<p>x</p>", [{"email": "a@x.com", "unsub_url": None}])
    assert out == {"sent": 1, "failed": 0} and marked["k"] == "2026-09-08"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_digest.py -k "broadcast or deliver" -v`
Expected: FAIL — `digest.broadcast_email` / `digest.deliver_if_new` / `digest.store` don't exist.

- [ ] **Step 3: Implement in `digest.py`**

Add `import store` to the top of `digest.py` (alongside `import emailer` from Task 1). Add:

```python
def broadcast_email(subject, html, recipients, banner=None):
    """Send `html` to each recipient, best-effort (one failure never aborts the
    rest). recipients: [{"email", "unsub_url"}]; unsub footer appended when set."""
    sent = failed = 0
    for r in recipients:
        body = html + (emailer.unsubscribe_footer(r["unsub_url"]) if r.get("unsub_url") else "")
        try:
            emailer.send_email(r["email"], subject, body, attachments=banner)
            sent += 1
        except Exception as e:  # noqa: BLE001 - best effort per recipient
            print(f"  [warn] digest send to {r.get('email')} failed: {e}")
            failed += 1
    return {"sent": sent, "failed": failed}


def deliver_if_new(key, subject, html, recipients, banner=None):
    """Idempotency guard: skip if this digest key was already sent; else send
    then record the key (durable, in Supabase — survives a CI retry)."""
    if store.digest_already_sent(key):
        print(f"Digest {key} already sent. Nothing sent.")
        return {"skipped": True}
    result = broadcast_email(subject, html, recipients, banner=banner)
    store.mark_digest_sent(key)
    return result
```

Then rewire `main()` to use them. Replace the send section of `main()` (from where `entries` is built through the `save_state(state)` call) with:

```python
    if not entries:
        print("No new high-signal nuggets since last digest. Nothing sent.")
        return
    subject, html = build_digest(entries, feed_url=feed_url)
    base = os.getenv("PUBLIC_BASE_URL") or feed_url.rstrip("/")
    try:
        subs = store.confirmed_email_subscribers()
    except Exception:
        subs = []
    recipients = [{"email": s["email"],
                   "unsub_url": f'{base}/unsubscribe?token={s["unsub_token"]}'} for s in subs]
    if not recipients and to:   # owner fallback while there are no confirmed subscribers
        recipients = [{"email": to, "unsub_url": None}]
    if not recipients:
        print("No confirmed subscribers and no DIGEST_TO. Nothing sent.")
        return
    key = datetime.now(timezone.utc).date().isoformat()
    result = deliver_if_new(key, subject, html, recipients, banner=banner_attachment())
    if result.get("skipped"):
        return
    state["last_sent"] = max(e["scraped_at"] for e in entries)
    save_state(state)
    print(f"Digest {key}: sent {result['sent']}, failed {result['failed']}.")
```

(The `feed_url`, `to`, `cfg`, `state`, `since`, `entries` lines earlier in `main()` are unchanged.)

- [ ] **Step 4: Run the digest tests + full gate**

Run: `.venv/bin/python -m pytest tests/test_digest.py -v && .venv/bin/python -m pytest -q --ignore=tests/test_extraction.py`
Expected: PASS — new broadcast/deliver tests green; existing digest tests green; whole suite green.

- [ ] **Step 5: Commit**

```bash
git add digest.py tests/test_digest.py
git commit -m "$(cat <<'EOF'
feat(digest): send to confirmed subscribers, guarded and per-recipient

digest now broadcasts to store.confirmed_email_subscribers() best-effort
(one failure never aborts the run), appends a one-click unsubscribe footer,
and wraps the send in a durable sent_digests[date] guard so a retried CI
run can't double-send. Falls back to DIGEST_TO when there are no subscribers.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01TQ1fNc6CoWAnrjCSMC2fNn
EOF
)"
```

---

### Task 6: subscribe box in `static/index.html` + `.env.example`

**Files:**
- Modify: `static/index.html` (insert a subscribe section before `<footer>` at line ~465, plus a small script)
- Modify: `.env.example`
- Modify: `tests/test_api.py` (a cheap presence regression test)

**Interfaces:**
- Consumes: `POST /subscribe` (Task 3).
- Produces: a `#subscribe-form` on the landing page.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_api.py`:

```python
def test_index_html_has_subscribe_form():
    with open("static/index.html", encoding="utf-8") as f:
        html = f.read()
    assert 'id="subscribe-form"' in html
    assert "/subscribe" in html
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_api.py -k subscribe_form -v`
Expected: FAIL — the form isn't in the page yet.

- [ ] **Step 3: Insert the subscribe section**

In `static/index.html`, immediately **before** the `<footer>` line (around line 465, after the `</section>` that closes `#corpus`), insert:

```html
    <section class="subscribe" aria-label="Subscribe to the daily digest"
             style="max-width:560px;margin:34px auto 0;background:var(--surface);
                    border:1px solid var(--border);border-radius:16px;
                    padding:22px 22px 20px;box-shadow:var(--shadow-sm);text-align:center">
      <h2 style="font-family:var(--font-display);color:var(--text);font-size:20px;margin:0 0 4px">
        Get the daily digest</h2>
      <p style="color:var(--text-2);font-size:14px;margin:0 0 14px">
        A short email of what's new across the AI labs. Double opt-in, one-click unsubscribe.</p>
      <form id="subscribe-form" autocomplete="off"
            style="display:flex;gap:8px;flex-wrap:wrap;justify-content:center">
        <input id="subscribe-email" type="email" required placeholder="you@example.com"
               aria-label="Your email"
               style="flex:1;min-width:220px;padding:11px 14px;border:1px solid var(--border-strong);
                      border-radius:10px;background:var(--bg);color:var(--text);font-size:15px">
        <button type="submit"
                style="padding:11px 18px;border:0;border-radius:10px;background:var(--accent);
                       color:var(--accent-contrast);font-weight:600;font-size:15px;cursor:pointer">
          Subscribe</button>
      </form>
      <p id="subscribe-msg" role="status" aria-live="polite"
         style="min-height:18px;margin:10px 0 0;font-size:13px;color:var(--text-2)"></p>
    </section>
```

- [ ] **Step 4: Add the submit handler**

Near the other inline scripts at the bottom of `static/index.html` (before `</body>`), add:

```html
  <script>
    (function () {
      var form = document.getElementById('subscribe-form');
      if (!form) return;
      var msg = document.getElementById('subscribe-msg');
      var input = document.getElementById('subscribe-email');
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        msg.style.color = 'var(--text-2)';
        msg.textContent = 'Subscribing…';
        fetch('/subscribe', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: input.value.trim() })
        }).then(function (r) {
          return r.json().then(function (d) { return { ok: r.ok, d: d }; });
        }).then(function (res) {
          if (res.ok) {
            msg.style.color = 'var(--accent-text)';
            msg.textContent = res.d.message || 'Check your inbox to confirm.';
            form.reset();
          } else {
            msg.style.color = 'var(--danger-text)';
            msg.textContent = (res.d && res.d.detail) || 'Something went wrong. Try again.';
          }
        }).catch(function () {
          msg.style.color = 'var(--danger-text)';
          msg.textContent = 'Network error. Try again.';
        });
      });
    })();
  </script>
```

- [ ] **Step 5: Update `.env.example`**

Add these documented lines to `.env.example`:

```
# Public subscription (Phase 2)
PUBLIC_BASE_URL=https://blog-rag.onrender.com   # base for confirm/unsubscribe links (falls back to FEED_URL)
RESEND_WEBHOOK_SECRET=whsec_...                 # from the Resend webhook config; verifies bounce/complaint callbacks
DIGEST_POSTAL_ADDRESS=                          # physical address for the CAN-SPAM footer (REQUIRED before public launch)
```

- [ ] **Step 6: Verify the page + full gate**

Run: `.venv/bin/python -m pytest tests/test_api.py -k subscribe_form -v && .venv/bin/python -m pytest -q --ignore=tests/test_extraction.py`
Expected: PASS. Then a quick visual sanity check: `.venv/bin/python -c "print(open('static/index.html').read().count('subscribe-form'))"` prints `1`.

- [ ] **Step 7: Commit**

```bash
git add static/index.html .env.example tests/test_api.py
git commit -m "$(cat <<'EOF'
feat(web): subscribe box on the landing page + document new env vars

Adds a double-opt-in subscribe form (matching the existing design system)
that POSTs to /subscribe with inline status, and documents PUBLIC_BASE_URL,
RESEND_WEBHOOK_SECRET, and DIGEST_POSTAL_ADDRESS in .env.example.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01TQ1fNc6CoWAnrjCSMC2fNn
EOF
)"
```

---

## Self-Review

**1. Spec coverage:**
- `email_subscribers` table + add/confirm/unsubscribe/list/mark → Task 2. ✓
- `rate_limits` + `/subscribe` per-IP limit → Task 2 (`rate_limit_ok`) + Task 3 (endpoint). ✓
- `sent_digests` durable idempotency guard → Task 2 + Task 5 (`deliver_if_new`). ✓
- Double opt-in (subscribe → confirm) + one-click unsubscribe → Task 3 + Task 1 footer + Task 5. ✓
- Resend bounce/complaint webhook, signature-verified fail-closed → Task 4. ✓
- Per-recipient best-effort send + owner fallback → Task 5. ✓
- `emailer.py` extraction shared by digest + transactional → Task 1. ✓
- Subscribe box matching the design system → Task 6. ✓
- No-enumeration `/subscribe` response → Task 3 (`test_subscribe_no_enumeration_for_existing`). ✓
- New env vars documented → Task 6. ✓
- Postal-address footer: env var documented (Task 6); actual footer insertion is a go-live config step (deferred with the domain per spec) — **noted, not built now** since it's dead text until launch. ✓
- Supabase tables + `service_role` grants → a user prerequisite for the live step (below), not a code task. ✓

**2. Placeholder scan:** No TBD/TODO/"handle edge cases". Every code step has concrete code and exact commands. ✓

**3. Type consistency:** `send_email(to, subject, html, attachments=, api_key=, sender=)` is used consistently in Tasks 1/3/5. `recipients` items are `{"email","unsub_url"}` in both Task 5 functions and their tests. `add_email_subscriber` returns a dict with `status`/`confirm_token`/`unsub_token`, consumed exactly that way in Task 3. `confirm_email`/`unsubscribe_email` return `bool`, used as such. `rate_limit_ok(bucket, limit)`, `digest_already_sent(key)`, `mark_digest_sent(key)` names match across Tasks 2/3/5. ✓

## Prerequisites & follow-ups (not code tasks)

- **Before the owner-only live test (user, in Supabase):** create tables and grant the service role —
  ```sql
  create table email_subscribers (email text primary key, status text not null default 'pending',
    confirm_token text, unsub_token text, subscribed_at timestamptz default now(), confirmed_at timestamptz);
  create table rate_limits (bucket text primary key, count int not null default 0, window_start timestamptz default now());
  create table sent_digests (digest_key text primary key, sent_at timestamptz default now());
  grant select,insert,update,delete on email_subscribers, rate_limits, sent_digests to service_role;
  ```
- **Owner-only live verification:** owner subscribes with their verified address → confirm → forced digest run (`gh workflow run daily.yml -f force=true`) delivers with a working unsubscribe; trigger a test bounce to confirm the webhook marks status.
- **Public go-live (later, gated, config-only):** verify a Resend sending domain + DNS; set `DIGEST_FROM` to it; register the Resend webhook at `/resend/webhook` → `RESEND_WEBHOOK_SECRET`; set `DIGEST_POSTAL_ADDRESS` and add the address to the digest footer; set `PUBLIC_BASE_URL` on Render.
