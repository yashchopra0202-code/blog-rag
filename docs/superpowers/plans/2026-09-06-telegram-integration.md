# Telegram Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let people use blog-rag from Telegram — ask questions / browse articles via a bot, and receive the daily digest as opt-in subscribers.

**Architecture:** A webhook endpoint on the existing FastAPI app receives Telegram messages and reuses the RAG core to answer; subscribers are stored in Supabase (via `httpx`/PostgREST). A cadence-gated CI step broadcasts the daily digest to subscribers. Pure logic (parsing, formatting) is isolated from I/O so it is unit-testable without any credentials.

**Tech Stack:** Python 3.12, FastAPI, httpx (existing), Supabase PostgREST, Telegram Bot API. Testing: pytest with monkeypatched `httpx`.

**Spec:** `docs/superpowers/specs/2026-09-06-telegram-integration-design.md`

## Global Constraints

- **No new dependencies** — use `httpx` (already in `requirements.txt`) for Supabase and Telegram; do not add `supabase-py` or a Telegram library.
- **Secrets are server-side only** — `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` come from env; never hard-code, never expose to `static/index.html`.
- **Telegram message limit** — 4096 characters; all outbound text must be truncated to fit.
- **Best-effort broadcast** — one recipient's failure must never abort the run.
- **Follow existing test patterns** — monkeypatch the module's `httpx` (as `tests/test_digest.py` does for Resend); tests must pass with no network and no credentials.
- **TDD** — failing test first, watch it fail, minimal code, watch it pass, commit.

## File Structure

- Create `telegram.py` — pure logic: `parse_update`, `format_answer`, `format_latest`, `format_digest_message`. No I/O.
- Create `store.py` — Supabase REST helpers: `add_subscriber`, `deactivate_subscriber`, `active_subscribers`.
- Create `telegram_api.py` — Telegram Bot API client: `send_message`, `set_webhook`.
- Create `telegram_digest.py` — CI broadcast entry point.
- Create `scripts/set_telegram_webhook.py` — one-time webhook registration.
- Modify `api.py` — factor RAG answering into `rag_answer(question)`; add `POST /telegram/webhook`.
- Modify `.github/workflows/daily.yml` — add a cadence-gated Telegram broadcast step.
- Tests: `tests/test_telegram.py`, `tests/test_store.py`, `tests/test_telegram_api.py`, `tests/test_telegram_webhook.py`, `tests/test_telegram_digest.py`.

Reused existing interfaces (do not redefine):
- `config.load_config(path="config.json") -> dict` (keys: `cadence`, `weekly_day`, `weekly_limit`, `enabled_labs`).
- `digest.select_new_entries(manifest, since, limit=None, enabled_labs=None) -> list[dict]` (each: `url,title,site,nugget,topic,signal,scraped_at`).
- `digest.curate(entries, min_signal=3, per_lab_cap=3) -> list[dict]`.
- `digest.effective_since(state, now=None, cadence="daily") -> str`.
- `digest.should_send_today(cfg, now=None, force=False) -> bool`.
- `digest.load_state(path) -> dict`, `digest.save_state(state, path) -> None`.
- `digest.lab_label(site) -> str`.
- `scraper.load_manifest(path) -> dict`.

---

## PHASE 1 — Q&A bot

### Task 1: Intent parsing (`telegram.parse_update`)

**Files:**
- Create: `telegram.py`
- Test: `tests/test_telegram.py`

**Interfaces:**
- Produces: `parse_update(update: dict) -> dict` returning `{"kind": str, "text": str, "chat": dict}` where `kind` ∈ `{"start","stop","latest","question","ignore"}` and `chat` is `{"id": int, "first_name": str, "username": str}` (empty dict when absent).

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_telegram.py
import telegram

def _msg(text):
    return {"message": {"text": text, "chat": {"id": 7, "first_name": "Yash", "username": "yc"}}}

def test_parse_start_command():
    out = telegram.parse_update(_msg("/start"))
    assert out["kind"] == "start"
    assert out["chat"]["id"] == 7 and out["chat"]["first_name"] == "Yash"

def test_parse_start_with_bot_suffix():
    assert telegram.parse_update(_msg("/start@FrontierLabsBot"))["kind"] == "start"

def test_parse_stop_and_latest():
    assert telegram.parse_update(_msg("/stop"))["kind"] == "stop"
    assert telegram.parse_update(_msg("/latest"))["kind"] == "latest"

def test_parse_freetext_is_question():
    out = telegram.parse_update(_msg("What is new in open models?"))
    assert out["kind"] == "question"
    assert out["text"] == "What is new in open models?"

def test_parse_non_message_update_is_ignore():
    assert telegram.parse_update({"edited_message": {}})["kind"] == "ignore"
    assert telegram.parse_update({"message": {"chat": {"id": 1}}})["kind"] == "ignore"  # no text
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/test_telegram.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'telegram'`

- [ ] **Step 3: Write minimal implementation**

```python
# telegram.py
"""Pure Telegram helpers: parse incoming updates and format outgoing text.
No network or state — everything here is unit-testable with plain dicts."""

MAX_LEN = 4096  # Telegram hard limit on message text

def parse_update(update):
    msg = update.get("message") if isinstance(update, dict) else None
    if not isinstance(msg, dict):
        return {"kind": "ignore", "text": "", "chat": {}}
    text = (msg.get("text") or "").strip()
    c = msg.get("chat") or {}
    chat = {"id": c.get("id"), "first_name": c.get("first_name", ""), "username": c.get("username", "")}
    if not text:
        return {"kind": "ignore", "text": "", "chat": chat}
    if text.startswith("/"):
        cmd = text.split()[0].lstrip("/").split("@")[0].lower()
        if cmd in ("start", "stop", "latest"):
            return {"kind": cmd, "text": "", "chat": chat}
        return {"kind": "question", "text": text, "chat": chat}  # unknown command -> treat as text
    return {"kind": "question", "text": text, "chat": chat}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/test_telegram.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add telegram.py tests/test_telegram.py
git commit -m "feat(telegram): parse incoming updates into intents"
```

---

### Task 2: Answer formatting (`telegram.format_answer`)

**Files:**
- Modify: `telegram.py`
- Test: `tests/test_telegram.py`

**Interfaces:**
- Consumes: `MAX_LEN` from Task 1.
- Produces: `format_answer(answer: str, sources: list[dict]) -> str` — Telegram HTML (`parse_mode=HTML`), HTML-escaped body, appends up to 5 sources as `<a href="url">title</a> — label` lines, truncated to `MAX_LEN`. `sources` items: `{"title","url","site"?}`; a `"label"` key wins over `"site"` for the display name.

- [ ] **Step 1: Write the failing tests**

```python
def test_format_answer_escapes_and_links():
    out = telegram.format_answer("A <b>bold</b> & tricky answer", [
        {"title": "Post <1>", "url": "https://x/a", "label": "Anthropic · News"},
    ])
    assert "&lt;b&gt;" in out and "&amp;" in out          # body escaped
    assert '<a href="https://x/a">Post &lt;1&gt;</a>' in out  # link title escaped
    assert "Anthropic · News" in out

def test_format_answer_truncates_to_limit():
    out = telegram.format_answer("x" * 6000, [])
    assert len(out) <= telegram.MAX_LEN

def test_format_answer_caps_sources_at_five():
    srcs = [{"title": f"T{i}", "url": f"https://x/{i}", "site": "s"} for i in range(9)]
    out = telegram.format_answer("ans", srcs)
    assert out.count("<a href=") == 5
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/test_telegram.py -k format_answer -v`
Expected: FAIL — `AttributeError: module 'telegram' has no attribute 'format_answer'`

- [ ] **Step 3: Write minimal implementation**

```python
# add to telegram.py
def _esc(s):
    return (str(s if s is not None else "")
            .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def format_answer(answer, sources):
    body = _esc(answer)
    lines = []
    for s in (sources or [])[:5]:
        name = _esc(s.get("label") or s.get("site") or "")
        url = str(s.get("url") or "")
        title = _esc(s.get("title") or url or "source")
        link = f'<a href="{_esc(url)}">{title}</a>' if url.startswith("http") else title
        lines.append(f"• {link}" + (f" — {name}" if name else ""))
    out = body + ("\n\n<b>Sources</b>\n" + "\n".join(lines) if lines else "")
    return out[:MAX_LEN]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/test_telegram.py -k format_answer -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add telegram.py tests/test_telegram.py
git commit -m "feat(telegram): format RAG answers as Telegram HTML with sources"
```

---

### Task 3: Latest-posts formatting (`telegram.format_latest`)

**Files:**
- Modify: `telegram.py`
- Test: `tests/test_telegram.py`

**Interfaces:**
- Produces: `format_latest(groups: list, limit: int = 10) -> str` — takes the `groups` list from `api.feed_data(...)["groups"]` (each `{"date","items":[{"title","url","label","site","nugget"}]}`), renders up to `limit` items newest-first as `<a>` links with lab labels, truncated to `MAX_LEN`. Empty groups → a friendly "no recent posts" string.

- [ ] **Step 1: Write the failing tests**

```python
def test_format_latest_lists_links():
    groups = [{"date": "2026-09-06", "items": [
        {"title": "Big model", "url": "https://x/a", "label": "Mistral", "site": "mistral", "nugget": "n"},
        {"title": "New agent", "url": "https://x/b", "label": "xAI", "site": "xai", "nugget": "n"},
    ]}]
    out = telegram.format_latest(groups)
    assert '<a href="https://x/a">Big model</a>' in out and "Mistral" in out
    assert '<a href="https://x/b">New agent</a>' in out

def test_format_latest_empty():
    assert "no recent" in telegram.format_latest([]).lower()

def test_format_latest_respects_limit():
    items = [{"title": f"P{i}", "url": f"https://x/{i}", "label": "L", "site": "s", "nugget": "n"} for i in range(20)]
    out = telegram.format_latest([{"date": "2026-09-06", "items": items}], limit=5)
    assert out.count("<a href=") == 5
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/test_telegram.py -k latest -v`
Expected: FAIL — no attribute `format_latest`

- [ ] **Step 3: Write minimal implementation**

```python
# add to telegram.py
def format_latest(groups, limit=10):
    rows, n = [], 0
    for g in (groups or []):
        for it in g.get("items", []):
            if n >= limit:
                break
            url = str(it.get("url") or "")
            title = _esc(it.get("title") or url)
            name = _esc(it.get("label") or it.get("site") or "")
            link = f'<a href="{_esc(url)}">{title}</a>' if url.startswith("http") else title
            rows.append(f"• {link}" + (f" — {name}" if name else ""))
            n += 1
    if not rows:
        return "No recent posts in the last week. Ask me a question instead!"
    return ("<b>Latest from the labs</b>\n" + "\n".join(rows))[:MAX_LEN]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/test_telegram.py -k latest -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add telegram.py tests/test_telegram.py
git commit -m "feat(telegram): format recent posts list"
```

---

### Task 4: Supabase subscriber store (`store.py`)

**Files:**
- Create: `store.py`
- Test: `tests/test_store.py`

**Interfaces:**
- Produces:
  - `add_subscriber(chat: dict) -> None` — upsert `{chat_id, first_name, username, active:true}`.
  - `deactivate_subscriber(chat_id: int) -> None` — PATCH `active=false`.
  - `active_subscribers() -> list[dict]` — GET rows where `active=eq.true`, returns list of `{"chat_id",...}`.
- Env: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`. Module reads them lazily via `_conf()` so tests can set them.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_store.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/test_store.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'store'`

- [ ] **Step 3: Write minimal implementation**

```python
# store.py
"""Supabase (PostgREST) helpers for the telegram_subscribers table, over httpx
so no extra dependency is needed. Service-role key — server-side only."""
import os
import httpx

TABLE = "telegram_subscribers"

def _conf():
    url = os.environ["SUPABASE_URL"].rstrip("/")
    key = os.environ["SUPABASE_SERVICE_KEY"]
    return url, {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}

def add_subscriber(chat):
    url, headers = _conf()
    headers = {**headers, "Prefer": "resolution=merge-duplicates"}
    row = {"chat_id": chat.get("id"), "first_name": chat.get("first_name", ""),
           "username": chat.get("username", ""), "active": True}
    r = httpx.post(f"{url}/rest/v1/{TABLE}", headers=headers, json=row, timeout=15)
    r.raise_for_status()

def deactivate_subscriber(chat_id):
    url, headers = _conf()
    r = httpx.patch(f"{url}/rest/v1/{TABLE}", headers=headers,
                    json={"active": False}, params={"chat_id": f"eq.{chat_id}"}, timeout=15)
    r.raise_for_status()

def active_subscribers():
    url, headers = _conf()
    r = httpx.get(f"{url}/rest/v1/{TABLE}", headers=headers,
                  params={"active": "eq.true", "select": "chat_id,first_name"}, timeout=15)
    r.raise_for_status()
    return r.json()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/test_store.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add store.py tests/test_store.py
git commit -m "feat(store): supabase subscriber add/deactivate/list over httpx"
```

---

### Task 5: Telegram Bot API client (`telegram_api.py`)

**Files:**
- Create: `telegram_api.py`
- Test: `tests/test_telegram_api.py`

**Interfaces:**
- Produces:
  - `send_message(token: str, chat_id: int, html: str) -> dict` — POST `sendMessage` with `parse_mode=HTML`, `disable_web_page_preview=True`.
  - `set_webhook(token: str, url: str, secret: str) -> dict` — POST `setWebhook` with `secret_token`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_telegram_api.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/test_telegram_api.py -v`
Expected: FAIL — no module `telegram_api`

- [ ] **Step 3: Write minimal implementation**

```python
# telegram_api.py
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/test_telegram_api.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add telegram_api.py tests/test_telegram_api.py
git commit -m "feat(telegram): bot API client (send_message, set_webhook)"
```

---

### Task 6: Refactor RAG answering into a reusable core (`api.rag_answer`)

**Files:**
- Modify: `api.py` (the `answer_question`/`ask` area, ~lines 70-93)
- Test: `tests/test_api.py` (must stay green)

**Interfaces:**
- Produces: `rag_answer(question: str) -> dict` — returns `{"answer": str, "sources": list}` on success, or `{"error": str, "status": int}` when the index is missing. Does **not** raise HTTP errors.
- The existing `POST /ask` route now calls `rag_answer` and raises `HTTPException(status, error)` when the result has an `"error"` key, preserving its current external behavior (400 on empty, 503 on missing index).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_api.py — add
import api

def test_rag_answer_returns_error_dict_when_no_index(monkeypatch):
    monkeypatch.setattr(api.os.path, "isdir", lambda p: False)
    out = api.rag_answer("anything")
    assert out.get("status") == 503 and "error" in out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_api.py -k rag_answer -v`
Expected: FAIL — no attribute `rag_answer`

- [ ] **Step 3: Refactor implementation**

Replace `answer_question` with a non-raising core and adapt the route:

```python
# api.py
def rag_answer(question: str) -> dict:
    if not os.path.isdir(PERSIST_DIR):
        return {"error": "No index. Run ingest.py first.", "status": 503}
    store = rag_core.load_index(PERSIST_DIR)
    retriever = rag_core.get_retriever(store, k=4)
    docs = retriever.invoke(question)
    context = rag_core.format_docs(docs)
    answer = _llm().invoke(PROMPT_TMPL.format(context=context, question=question)).content
    sources, seen = [], set()
    for d in docs:
        url = d.metadata.get("source", "")
        if url and url not in seen:
            seen.add(url)
            sources.append({"title": nice_title(d.metadata.get("title", ""), url),
                            "url": url, "site": d.metadata.get("site", "")})
    return {"answer": answer, "sources": sources}

@app.post("/ask")
def ask(payload: Ask):
    q = payload.question.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Question is empty.")
    result = rag_answer(q)
    if "error" in result:
        raise HTTPException(status_code=result["status"], detail=result["error"])
    return result
```

- [ ] **Step 4: Run the full api test file to verify all pass**

Run: `.venv/bin/pytest tests/test_api.py -v`
Expected: PASS (existing 400/503/answer tests still green + new one)

- [ ] **Step 5: Commit**

```bash
git add api.py tests/test_api.py
git commit -m "refactor(api): extract non-raising rag_answer core for reuse"
```

---

### Task 7: Webhook endpoint + dispatch (`POST /telegram/webhook`)

**Files:**
- Modify: `api.py`
- Test: `tests/test_telegram_webhook.py`

**Interfaces:**
- Consumes: `telegram.parse_update/format_answer/format_latest`, `store.add_subscriber/deactivate_subscriber`, `telegram_api.send_message`, `api.rag_answer`, `api.feed_data`.
- Produces: `POST /telegram/webhook` — verifies header `X-Telegram-Bot-Api-Secret-Token == TELEGRAM_WEBHOOK_SECRET` (else 401), parses the update, dispatches by intent, replies via `send_message`. Always returns `{"ok": True}` with 200 on authenticated calls (Telegram needs a fast 200).

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_telegram_webhook.py
import os
import api
from fastapi.testclient import TestClient

client = TestClient(api.app)

def _setup(monkeypatch, sent):
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "sec")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "TOK")
    monkeypatch.setattr(api.telegram_api, "send_message", lambda tok, cid, html: sent.append((cid, html)))

def test_webhook_rejects_bad_secret(monkeypatch):
    _setup(monkeypatch, [])
    r = client.post("/telegram/webhook", json={}, headers={"X-Telegram-Bot-Api-Secret-Token": "nope"})
    assert r.status_code == 401

def test_webhook_start_subscribes_and_greets(monkeypatch):
    sent = []; subbed = []
    _setup(monkeypatch, sent)
    monkeypatch.setattr(api.store, "add_subscriber", lambda chat: subbed.append(chat["id"]))
    r = client.post("/telegram/webhook",
                    json={"message": {"text": "/start", "chat": {"id": 7, "first_name": "Y"}}},
                    headers={"X-Telegram-Bot-Api-Secret-Token": "sec"})
    assert r.status_code == 200 and subbed == [7]
    assert sent and sent[0][0] == 7

def test_webhook_question_answers(monkeypatch):
    sent = []
    _setup(monkeypatch, sent)
    monkeypatch.setattr(api, "rag_answer", lambda q: {"answer": "AoT", "sources": []})
    client.post("/telegram/webhook",
                json={"message": {"text": "what is new?", "chat": {"id": 3}}},
                headers={"X-Telegram-Bot-Api-Secret-Token": "sec"})
    assert sent and "AoT" in sent[0][1]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/test_telegram_webhook.py -v`
Expected: FAIL — 404 (route not defined)

- [ ] **Step 3: Write minimal implementation**

Add imports and the route to `api.py`:

```python
# api.py — near the other imports
from fastapi import Request
import telegram as tg
import telegram_api
import store

WELCOME = ("Hi{name}! I answer questions about what the AI labs are publishing. "
           "Send me any question, or /latest for recent posts. /stop to unsubscribe.")

@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != os.getenv("TELEGRAM_WEBHOOK_SECRET"):
        raise HTTPException(status_code=401, detail="bad secret")
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    update = await request.json()
    intent = tg.parse_update(update)
    chat = intent.get("chat") or {}
    cid = chat.get("id")
    if cid is None:
        return {"ok": True}
    if intent["kind"] == "start":
        try: store.add_subscriber(chat)
        except Exception: pass
        name = " " + chat.get("first_name", "") if chat.get("first_name") else ""
        telegram_api.send_message(token, cid, WELCOME.format(name=name))
    elif intent["kind"] == "stop":
        try: store.deactivate_subscriber(cid)
        except Exception: pass
        telegram_api.send_message(token, cid, "You're unsubscribed. Send /start to rejoin.")
    elif intent["kind"] == "latest":
        groups = feed_data(7).get("groups", [])
        telegram_api.send_message(token, cid, tg.format_latest(groups))
    elif intent["kind"] == "question":
        result = rag_answer(intent["text"])
        if "error" in result:
            telegram_api.send_message(token, cid, "The archive isn't ready yet — please try again shortly.")
        else:
            telegram_api.send_message(token, cid, tg.format_answer(result["answer"], result["sources"]))
    return {"ok": True}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/test_telegram_webhook.py tests/test_api.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add api.py tests/test_telegram_webhook.py
git commit -m "feat(telegram): webhook endpoint dispatching start/stop/latest/question"
```

---

### Task 8: One-time webhook registration script

**Files:**
- Create: `scripts/set_telegram_webhook.py`

**Interfaces:**
- Consumes: `telegram_api.set_webhook`. Reads `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET`, `FEED_URL` (or `APP_URL`) from env.

- [ ] **Step 1: Write the script**

```python
# scripts/set_telegram_webhook.py
"""One-time: register the Telegram webhook. Run after the app is deployed.
Env: TELEGRAM_BOT_TOKEN, TELEGRAM_WEBHOOK_SECRET, APP_URL (e.g. https://blog-rag.onrender.com)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import telegram_api
from dotenv import load_dotenv

def main():
    load_dotenv()
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    secret = os.environ["TELEGRAM_WEBHOOK_SECRET"]
    base = os.environ.get("APP_URL", os.environ.get("FEED_URL", "")).rstrip("/")
    if not base:
        raise SystemExit("Set APP_URL to your deployed base URL.")
    print(telegram_api.set_webhook(token, f"{base}/telegram/webhook", secret))

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify it imports cleanly**

Run: `.venv/bin/python -c "import ast; ast.parse(open('scripts/set_telegram_webhook.py').read()); print('ok')"`
Expected: `ok`

- [ ] **Step 3: Commit**

```bash
git add scripts/set_telegram_webhook.py
git commit -m "feat(telegram): one-time webhook registration script"
```

**Phase 1 live-wiring checklist (needs user credentials — not code):**
1. User creates bot via @BotFather → `TELEGRAM_BOT_TOKEN`.
2. User creates Supabase project + runs the `telegram_subscribers` DDL → `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`.
3. Set `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET` (random), `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` in the **Render** dashboard.
4. After Render redeploys, run `set_telegram_webhook.py` (locally, with `APP_URL=https://blog-rag.onrender.com` and the same token/secret).
5. Verify: message the bot → `/start` subscribes + greets; a question returns a real answer with sources.

---

## PHASE 2 — Broadcast digest

### Task 9: Digest message formatting (`telegram.format_digest_message`)

**Files:**
- Modify: `telegram.py`
- Test: `tests/test_telegram.py`

**Interfaces:**
- Consumes: `MAX_LEN`, `_esc`.
- Produces: `format_digest_message(entries: list, feed_url: str, top: int = 5) -> str` — entries are `digest.curate(...)` output (`{title,url,site,nugget,...}`); renders a header + top-N `<a>` links (with `nugget` one-liners) + a "full feed" link, truncated to `MAX_LEN`. Uses `label` if present else `site`.

- [ ] **Step 1: Write the failing tests**

```python
def test_format_digest_message_has_links_and_feed():
    entries = [{"title": "A big release", "url": "https://x/a", "site": "mistral", "nugget": "It ships."},
               {"title": "New research", "url": "https://x/b", "site": "deepmind", "nugget": "Findings."}]
    out = telegram.format_digest_message(entries, "https://feed/", top=5)
    assert '<a href="https://x/a">A big release</a>' in out
    assert "https://feed/" in out

def test_format_digest_message_caps_top():
    entries = [{"title": f"T{i}", "url": f"https://x/{i}", "site": "s", "nugget": "n"} for i in range(10)]
    out = telegram.format_digest_message(entries, "https://feed/", top=3)
    assert out.count("<a href=\"https://x/") == 3
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/test_telegram.py -k digest_message -v`
Expected: FAIL — no attribute `format_digest_message`

- [ ] **Step 3: Write minimal implementation**

```python
# add to telegram.py
def format_digest_message(entries, feed_url, top=5):
    rows = []
    for e in (entries or [])[:top]:
        url = str(e.get("url") or "")
        title = _esc(e.get("title") or url)
        name = _esc(e.get("label") or e.get("site") or "")
        link = f'<a href="{_esc(url)}">{title}</a>' if url.startswith("http") else title
        head = f"• {link}" + (f" — {name}" if name else "")
        nug = _esc(e.get("nugget") or "")
        rows.append(head + (f"\n{nug}" if nug else ""))
    body = "<b>Fresh from the AI labs</b>\n\n" + "\n\n".join(rows)
    if feed_url:
        body += f'\n\n<a href="{_esc(feed_url)}">Open the full feed →</a>'
    return body[:MAX_LEN]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/test_telegram.py -k digest_message -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add telegram.py tests/test_telegram.py
git commit -m "feat(telegram): format the broadcast digest message"
```

---

### Task 10: Broadcast entry point (`telegram_digest.py`)

**Files:**
- Create: `telegram_digest.py`
- Test: `tests/test_telegram_digest.py`

**Interfaces:**
- Consumes: `config.load_config`, `digest.should_send_today/effective_since/select_new_entries/curate/load_state/save_state`, `scraper.load_manifest`, `telegram.format_digest_message`, `store.active_subscribers`, `telegram_api.send_message`.
- Produces: `broadcast(now=None) -> dict` returning `{"sent": int, "failed": int, "skipped": bool}`; `main()` calls it. State file `data/telegram_state.json` (separate from email's). Best-effort per recipient.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_telegram_digest.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/test_telegram_digest.py -v`
Expected: FAIL — no module `telegram_digest`

- [ ] **Step 3: Write minimal implementation**

```python
# telegram_digest.py
"""Broadcast the daily digest to Telegram subscribers. Run by CI after the
email step, gated by config.json cadence. Best-effort per recipient."""
import os
from dotenv import load_dotenv

import config
import digest
import telegram as tg
import telegram_api
import store
from scraper import load_manifest

MANIFEST_PATH = "data/manifest.json"
STATE_PATH = "data/telegram_state.json"

def broadcast(now=None):
    cfg = config.load_config()
    cadence = cfg.get("cadence", "daily")
    force = os.getenv("DIGEST_FORCE", "").lower() in ("1", "true", "yes")
    if not digest.should_send_today(cfg, now=now, force=force):
        print(f"Cadence is {cadence}; not a send day. Nothing broadcast.")
        return {"sent": 0, "failed": 0, "skipped": True}
    limit = cfg["weekly_limit"] if cadence == "weekly" else int(os.getenv("DIGEST_LIMIT", "20"))
    manifest = load_manifest(MANIFEST_PATH)
    state = digest.load_state(STATE_PATH)
    since = digest.effective_since(state, now=now, cadence=cadence)
    entries = digest.curate(digest.select_new_entries(manifest, since, enabled_labs=cfg.get("enabled_labs")))[:limit]
    if not entries:
        print("No new nuggets since last broadcast.")
        return {"sent": 0, "failed": 0, "skipped": False}
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    feed_url = os.getenv("FEED_URL") or "https://blog-rag.onrender.com/"
    msg = tg.format_digest_message(entries, feed_url)
    sent = failed = 0
    for sub in store.active_subscribers():
        try:
            telegram_api.send_message(token, sub["chat_id"], msg)
            sent += 1
        except Exception as e:  # noqa: BLE001 - one bad recipient must not abort
            print(f"  [warn] send to {sub.get('chat_id')} failed: {e}")
            failed += 1
    state["last_sent"] = max(e["scraped_at"] for e in entries)
    digest.save_state(state, STATE_PATH)
    print(f"Broadcast to {sent} subscriber(s); {failed} failed.")
    return {"sent": sent, "failed": failed, "skipped": False}

def main():
    load_dotenv()
    broadcast()

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/test_telegram_digest.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add telegram_digest.py tests/test_telegram_digest.py
git commit -m "feat(telegram): cadence-gated broadcast to subscribers"
```

---

### Task 11: Wire the broadcast into the daily workflow

**Files:**
- Modify: `.github/workflows/daily.yml`

**Interfaces:**
- Consumes: `telegram_digest.py`. New secrets: `TELEGRAM_BOT_TOKEN`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` (added to the repo's Actions secrets by the user).

- [ ] **Step 1: Add the broadcast step after the "Email digest" step**

```yaml
      - name: Telegram broadcast
        id: telegram
        continue-on-error: true
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}
          FEED_URL: ${{ secrets.FEED_URL }}
          DIGEST_FORCE: ${{ github.event.inputs.force }}
        run: .venv/bin/python telegram_digest.py
```

- [ ] **Step 2: Add the telegram state file to the commit-back step**

In the "Commit refreshed data" step, extend the `git add` line:

```yaml
          git add data/articles data/manifest.json data/digest_state.json data/telegram_state.json
```

- [ ] **Step 3: Verify the YAML parses**

Run: `.venv/bin/python -c "import yaml; yaml.safe_load(open('.github/workflows/daily.yml')); print('yaml OK')"`
Expected: `yaml OK`

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/daily.yml
git commit -m "ci: broadcast the daily digest to Telegram subscribers"
```

**Phase 2 live-wiring checklist (needs user):**
1. Add `TELEGRAM_BOT_TOKEN`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` to the repo's GitHub Actions secrets (`gh secret set`).
2. Trigger a run (`gh workflow run daily.yml -f force=true`) and confirm subscribers receive the digest.

---

## Self-Review

**Spec coverage:**
- Q&A bot (webhook, /start /stop /latest, free-text) → Tasks 1,2,3,6,7. ✓
- Subscribers in Supabase via httpx → Task 4. ✓
- Telegram API client → Task 5. ✓
- Broadcast, cadence-gated, best-effort → Tasks 9,10,11. ✓
- Webhook secret auth → Task 7. ✓
- One-time webhook registration → Task 8. ✓
- No new dependency (httpx only) → all tasks use `httpx`. ✓
- Secrets server-side only → Tasks 4,5,7,10 read from env; none touch `static/`. ✓
- 4096-char truncation → Tasks 2,3,9. ✓

**Placeholder scan:** No TBD/TODO; every code step has real code. ✓

**Type consistency:** `rag_answer` returns `{"answer","sources"}`/`{"error","status"}` (defined Task 6, consumed Task 7). `parse_update` returns `{"kind","text","chat"}` (Task 1, consumed Task 7). `active_subscribers()` rows use `chat_id` (Task 4, consumed Task 10). `send_message(token, chat_id, html)` consistent across Tasks 5,7,10. ✓
