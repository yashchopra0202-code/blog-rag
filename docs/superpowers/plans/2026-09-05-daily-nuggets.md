# Daily Nuggets Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn blog-rag into a daily-use tool that summarizes each new AI-lab post into a short "nugget" and delivers those nuggets through a web "Today" feed and a daily email digest, refreshed by a scheduled job.

**Architecture:** A new incremental `nuggetize.py` step summarizes each new article (via `claude-haiku-4-5`) and stores the summary in `manifest.json`. A new `GET /feed` endpoint and a "Today" view in the existing page serve nuggets straight from the manifest (no vector index). A new `digest.py` emails recent nuggets via Resend. A GitHub Actions cron runs scrape → nuggetize → digest daily and commits the text data back; it does **not** build or commit the Chroma index.

**Tech Stack:** Python 3.12, FastAPI, LangChain + `langchain-anthropic` (`claude-haiku-4-5`), `httpx` (Resend HTTP API), scrapling (scraper venv), pytest.

**Spec:** `docs/superpowers/specs/2026-09-05-daily-nuggets-design.md`

## Global Constraints

- **Python floor:** 3.12. Two venvs: RAG `.venv` runs everything except the scraper; the scraper runs on the scrapling venv (`~/.venvs/scrapling` locally).
- **No new pip dependencies.** Resend is called over HTTP with `httpx`, already in `requirements.txt`.
- **Models (verbatim):** embeddings `voyage-3.5`; LLM `claude-haiku-4-5`.
- **Nugget = 2-3 sentence summary card:** "what happened → why it matters", plain text (no markdown).
- **Nuggets are stored in `manifest.json`** under a `nugget` field; absence means "not summarized yet". Nugget generation is incremental (skip entries that already have one).
- **Trust boundary:** first-party lab/company blogs only. Nugget/source text is rendered into HTML on the feed and in email — **escape it on output** (feed: `textContent`; email: an explicit escape helper).
- **CI must not build or commit `chroma_db`** (binary sqlite → repo bloat). The index is rebuilt locally with `ingest.py` on demand.
- **Manifest entry shape (existing):** `manifest[url] = {title, date, site, file, scraped_at}`. New optional fields: `nugget`, `nugget_at`.
- **Reuse existing helpers:** `article_format.parse_article`, `scraper.load_manifest` / `scraper.save_manifest` (both import cleanly on the RAG venv — scrapling is imported lazily inside scraper functions), `rag_core.require_env`, `api.SITE_LABELS`, `api.nice_title`.

---

## File Structure

- `nuggetize.py` *(new)* — incremental nugget generation into the manifest.
- `digest.py` *(new)* — build + send the daily Resend email; track `data/digest_state.json`.
- `api.py` *(modify)* — add `feed_data()` + `GET /feed`.
- `static/index.html` *(modify)* — add a "Today" feed view.
- `sites.py` *(modify)* — add first-party lab blogs.
- `.github/workflows/daily.yml` *(new)* — scheduled pipeline.
- `.env.example` *(modify)* — Resend config.
- `README.md` *(modify)* — daily-nuggets docs.
- Tests: `tests/test_nuggetize.py` *(new)*, `tests/test_digest.py` *(new)*, `tests/test_api.py` *(modify)*, `tests/test_sites.py` *(modify)*.

Task order: **1 → 2 → 3 → 4 → 5 → 6.** Task 6 (CI) depends on Tasks 1 and 4 existing.

---

### Task 1: `nuggetize.py` — incremental nugget generation

**Files:**
- Create: `nuggetize.py`
- Test: `tests/test_nuggetize.py`

**Interfaces:**
- Consumes: `article_format.parse_article(path) -> (meta, body)`; `scraper.load_manifest(path) -> dict`; `scraper.save_manifest(path, manifest)`; `rag_core.require_env(name)`.
- Produces: `summarize_article(body: str, llm) -> str`; `nuggetize_manifest(manifest: dict, articles_dir: str, llm, save=None) -> int` (mutates `manifest`, adds `nugget` + `nugget_at`, returns count written); `main()`. `llm` is any object with `.invoke(prompt) -> obj` where `obj.content` is the text.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_nuggetize.py
from types import SimpleNamespace
import nuggetize


class _LLM:
    def __init__(self, text="NUGGET"):
        self.text = text
        self.calls = 0

    def invoke(self, prompt):
        self.calls += 1
        return SimpleNamespace(content=self.text)


def _write(tmp_path, name, body):
    p = tmp_path / name
    p.write_text(f"---\nurl: u\nsite: s\n---\n\n{body}\n", encoding="utf-8")
    return str(p)


def test_skips_entries_that_already_have_a_nugget(tmp_path):
    f = _write(tmp_path, "a.md", "some body text")
    manifest = {"https://x/a": {"file": f, "nugget": "old"}}
    llm = _LLM()
    n = nuggetize.nuggetize_manifest(manifest, str(tmp_path), llm)
    assert n == 0
    assert llm.calls == 0
    assert manifest["https://x/a"]["nugget"] == "old"


def test_writes_nugget_for_entry_without_one(tmp_path):
    f = _write(tmp_path, "a.md", "some body text")
    manifest = {"https://x/a": {"file": f}}
    llm = _LLM("A crisp summary.")
    n = nuggetize.nuggetize_manifest(manifest, str(tmp_path), llm)
    assert n == 1
    assert manifest["https://x/a"]["nugget"] == "A crisp summary."
    assert "nugget_at" in manifest["https://x/a"]


def test_one_failure_does_not_stop_the_rest(tmp_path):
    good = _write(tmp_path, "good.md", "good body")
    manifest = {
        "https://x/bad": {"file": str(tmp_path / "missing.md")},  # parse raises
        "https://x/good": {"file": good},
    }
    llm = _LLM("ok")
    n = nuggetize.nuggetize_manifest(manifest, str(tmp_path), llm)
    assert n == 1
    assert "nugget" not in manifest["https://x/bad"]
    assert manifest["https://x/good"]["nugget"] == "ok"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_nuggetize.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'nuggetize'`.

- [ ] **Step 3: Write the implementation**

```python
# nuggetize.py  -- runs on the RAG .venv
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

import article_format as af
import rag_core
from scraper import load_manifest, save_manifest

MANIFEST_PATH = "data/manifest.json"
ARTICLES_DIR = "data/articles"
MODEL = "claude-haiku-4-5"
MAX_BODY_CHARS = 8000  # cap tokens/cost; the intro carries the gist

NUGGET_PROMPT = (
    "Summarize this AI blog post in 2-3 sentences for a daily reading digest. "
    "First say what the post is or what happened, then why it matters. "
    "Plain text only: no preamble, no markdown, no bullet points.\n\n"
    "Post:\n{body}"
)


def _llm():
    return ChatAnthropic(model=MODEL, max_tokens=256)


def summarize_article(body: str, llm) -> str:
    text = body.strip()[:MAX_BODY_CHARS]
    return llm.invoke(NUGGET_PROMPT.format(body=text)).content.strip()


def nuggetize_manifest(manifest, articles_dir, llm, save=None) -> int:
    written = 0
    for url, entry in manifest.items():
        if entry.get("nugget"):
            continue
        try:
            _, body = af.parse_article(entry.get("file", ""))
            if not body.strip():
                continue
            entry["nugget"] = summarize_article(body, llm)
            entry["nugget_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            written += 1
            if save:
                save()  # checkpoint after each success
        except Exception as e:  # noqa: BLE001 - isolate per-article failures
            print(f"  [warn] nugget failed for {url}: {e}")
    return written


def main() -> None:
    load_dotenv()
    rag_core.require_env("ANTHROPIC_API_KEY")
    manifest = load_manifest(MANIFEST_PATH)
    if not manifest:
        raise SystemExit(f"No manifest at {MANIFEST_PATH}. Run the scraper first.")
    llm = _llm()
    n = nuggetize_manifest(manifest, ARTICLES_DIR, llm,
                           save=lambda: save_manifest(MANIFEST_PATH, manifest))
    save_manifest(MANIFEST_PATH, manifest)
    print(f"Nuggetized {n} new article(s). Manifest has {len(manifest)} total.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_nuggetize.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add nuggetize.py tests/test_nuggetize.py
git commit -m "feat: incremental nugget generation into the manifest"
```

---

### Task 2: `GET /feed` endpoint

**Files:**
- Modify: `api.py` (add `datetime` import, `FEED_MAX_DAYS`, `feed_data()`, `/feed` route)
- Test: `tests/test_api.py` (add one test)

**Interfaces:**
- Consumes: `api.MANIFEST_PATH`, `api.SITE_LABELS`, `api.nice_title`.
- Produces: `feed_data(days: int = 7) -> {"days": int, "groups": [{"date": "YYYY-MM-DD", "items": [{"title","url","site","label","nugget"}]}]}` (newest day first; within a day, manifest/scrape order); `GET /feed?days=7`.

- [ ] **Step 1: Write the failing test** (append to `tests/test_api.py`)

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_api.py::test_feed_groups_filters_and_clamps -v`
Expected: FAIL with `AttributeError: module 'api' has no attribute 'feed_data'`.

- [ ] **Step 3: Implement**

Add to the imports at the top of `api.py` (there is currently no `datetime` import):

```python
from datetime import datetime, timezone, timedelta
```

Add near the other constants (after `MODEL = "claude-haiku-4-5"`):

```python
FEED_MAX_DAYS = 30
```

Add these two definitions (place `feed_data` next to `corpus_stats`, and the route next to `/stats`):

```python
def feed_data(days: int = 7) -> dict:
    """Nuggets from the last `days`, grouped by scrape date (newest first).

    Reads only the manifest — no vector index load. Within a day, manifest
    insertion order (scrape order, reverse-chronological) is preserved."""
    days = max(1, min(days, FEED_MAX_DAYS))
    try:
        with open(MANIFEST_PATH, encoding="utf-8") as f:
            manifest = json.load(f)
    except (OSError, ValueError):
        manifest = {}
    cutoff = (datetime.now(timezone.utc).date() - timedelta(days=days - 1)).isoformat()
    groups: dict = {}
    for url, v in manifest.items():
        nugget = v.get("nugget")
        day = (v.get("scraped_at") or "")[:10]
        if not nugget or not day or day < cutoff:
            continue
        site = v.get("site", "")
        groups.setdefault(day, []).append({
            "title": nice_title(v.get("title", ""), url), "url": url, "site": site,
            "label": SITE_LABELS.get(site, site), "nugget": nugget})
    ordered = [{"date": d, "items": groups[d]} for d in sorted(groups, reverse=True)]
    return {"days": days, "groups": ordered}


@app.get("/feed")
def feed(days: int = 7):
    return feed_data(days)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_api.py -v`
Expected: all pass (existing + the new one).

- [ ] **Step 5: Commit**

```bash
git add api.py tests/test_api.py
git commit -m "feat: GET /feed serves nuggets grouped by day from the manifest"
```

---

### Task 3: "Today" feed view in `static/index.html`

**Files:**
- Modify: `static/index.html` (add markup, CSS, and a fetch/render function)

**Interfaces:**
- Consumes: `GET /feed?days=7`.
- No new JS globals other than one `loadFeed()` function; render uses `textContent` (escapes nugget/source text — satisfies the trust-boundary output-escaping constraint).

- [ ] **Step 1: Read the file's existing structure first**

Open `static/index.html`. Locate: (a) the `.wrap` container in the body, (b) the closing `</style>`, and (c) the main `<script>` block. You will insert into each. Match the existing design tokens (`--surface`, `--border`, `--accent-text`, `--text-2`, `--shadow-sm`, `--font-display`).

- [ ] **Step 2: Add the markup** at the top of `.wrap` (before the existing discovery/ask content)

```html
<section id="today" class="today" aria-label="Today's nuggets">
  <h2 class="today-title">Fresh from the labs</h2>
  <div id="today-feed" class="feed"></div>
  <p id="today-empty" class="feed-empty" hidden>No new posts in the last week.</p>
</section>
```

- [ ] **Step 3: Add the CSS** just before `</style>`

```css
.today { padding: 8px 0 26px; }
.today-title { font-family: var(--font-display); font-weight: 700; letter-spacing: -.02em; font-size: 1.15rem; margin: 0 0 12px; }
.feed { display: flex; flex-direction: column; gap: 12px; }
.feed-empty { color: var(--text-3); }
.feed-day { color: var(--text-3); font-size: .82rem; text-transform: uppercase; letter-spacing: .06em; margin: 14px 0 2px; }
.nugget-card { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 16px 18px; box-shadow: var(--shadow-sm); }
.nugget-card .label { color: var(--accent-text); font-size: .78rem; font-weight: 600; }
.nugget-card h3 { font-family: var(--font-display); font-weight: 600; font-size: 1.02rem; margin: 4px 0 8px; line-height: 1.3; }
.nugget-card p { margin: 0 0 10px; color: var(--text-2); }
.nugget-card a { font-weight: 600; }
```

- [ ] **Step 4: Add the render function** inside the main `<script>` (and call it on load)

```javascript
async function loadFeed() {
  const wrap = document.getElementById('today-feed');
  const empty = document.getElementById('today-empty');
  try {
    const res = await fetch('/feed?days=7');
    const data = await res.json();
    wrap.innerHTML = '';
    if (!data.groups || !data.groups.length) { empty.hidden = false; return; }
    empty.hidden = true;
    for (const group of data.groups) {
      const day = document.createElement('div');
      day.className = 'feed-day';
      day.textContent = new Date(group.date + 'T00:00:00')
        .toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' });
      wrap.appendChild(day);
      for (const it of group.items) {
        const card = document.createElement('article');
        card.className = 'nugget-card';
        const label = document.createElement('div');
        label.className = 'label';
        label.textContent = it.label || it.site;
        const h = document.createElement('h3');
        h.textContent = it.title;
        const p = document.createElement('p');
        p.textContent = it.nugget;              // textContent escapes model/source text
        const a = document.createElement('a');
        a.href = it.url; a.target = '_blank'; a.rel = 'noopener';
        a.textContent = 'Read source →';
        card.append(label, h, p, a);
        wrap.appendChild(card);
      }
    }
  } catch (e) {
    empty.hidden = false;
  }
}
loadFeed();
```

- [ ] **Step 5: Manual verification**

Requires a manifest with at least one nugget. If you have none yet, create a one-off fixture:

```bash
.venv/bin/python - <<'PY'
import json, os
from datetime import datetime, timezone
os.makedirs("data", exist_ok=True)
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
json.dump({"https://example.com/post": {
    "title": "Example post", "site": "anthropic-news", "date": "2026-09-05",
    "scraped_at": now, "nugget": "A demo nugget. It shows the feed renders."}},
    open("data/manifest.json", "w"), indent=2)
print("wrote demo manifest")
PY
.venv/bin/uvicorn api:app  # then open http://127.0.0.1:8000
```

Confirm: `curl -s http://127.0.0.1:8000/feed | python3 -m json.tool` shows the group, and the page renders the card under a dated heading. (Restore the real manifest afterward if you overwrote it — `git checkout data/manifest.json`.)

- [ ] **Step 6: Commit**

```bash
git add static/index.html
git commit -m "feat: Today feed view rendering nuggets from /feed"
```

---

### Task 4: `digest.py` — daily Resend email

**Files:**
- Create: `digest.py`
- Modify: `.env.example`
- Test: `tests/test_digest.py`

**Interfaces:**
- Consumes: `scraper.load_manifest`; `httpx.post`.
- Produces: `select_new_entries(manifest, since) -> list[dict]`; `build_digest(entries, feed_url=...) -> (subject, html)` (pure); `send_digest(subject, html, api_key, sender, to) -> dict`; `load_state()/save_state(state)`; `main()`. State file `data/digest_state.json` holds `{"last_sent": iso}`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_digest.py
import digest


def test_select_excludes_no_nugget_and_old():
    manifest = {
        "u1": {"nugget": "a", "scraped_at": "2026-09-05T10:00:00+00:00", "title": "A", "site": "s"},
        "u2": {"scraped_at": "2026-09-05T11:00:00+00:00", "title": "B", "site": "s"},   # no nugget
        "u3": {"nugget": "c", "scraped_at": "2026-09-04T10:00:00+00:00", "title": "C", "site": "s"},  # old
    }
    out = digest.select_new_entries(manifest, since="2026-09-04T12:00:00+00:00")
    assert [e["url"] for e in out] == ["u1"]


def test_select_all_when_no_since():
    manifest = {"u1": {"nugget": "a", "scraped_at": "2026-09-05T10:00:00+00:00", "title": "A", "site": "s"}}
    assert len(digest.select_new_entries(manifest, since=None)) == 1


def test_build_digest_escapes_and_includes():
    entries = [{"url": "https://x/a", "title": "Big <news>", "site": "lab",
                "nugget": "why & how", "scraped_at": "2026-09-05T10:00:00+00:00"}]
    subject, html = digest.build_digest(entries, feed_url="http://f/")
    assert "1 new" in subject
    assert "Big &lt;news&gt;" in html
    assert "why &amp; how" in html
    assert "https://x/a" in html


def test_send_digest_posts_to_resend(monkeypatch):
    captured = {}

    class _Resp:
        def raise_for_status(self): pass
        def json(self): return {"id": "1"}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured.update(url=url, headers=headers, json=json)
        return _Resp()

    monkeypatch.setattr(digest.httpx, "post", fake_post)
    digest.send_digest("subj", "<b>h</b>", "key", "from@x", "to@y")
    assert captured["url"] == digest.RESEND_ENDPOINT
    assert captured["json"]["to"] == ["to@y"]
    assert captured["headers"]["Authorization"] == "Bearer key"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_digest.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'digest'`.

- [ ] **Step 3: Implement**

```python
# digest.py  -- runs on the RAG .venv
import json
import os
from datetime import datetime, timezone

import httpx
from dotenv import load_dotenv

from scraper import load_manifest

MANIFEST_PATH = "data/manifest.json"
STATE_PATH = "data/digest_state.json"
RESEND_ENDPOINT = "https://api.resend.com/emails"


def load_state(path=STATE_PATH):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_state(state, path=STATE_PATH):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def select_new_entries(manifest, since):
    out = []
    for url, v in manifest.items():
        if not v.get("nugget"):
            continue
        stamp = v.get("scraped_at", "")
        if since and stamp <= since:
            continue
        out.append({"url": url, "title": v.get("title", url), "site": v.get("site", ""),
                    "nugget": v["nugget"], "scraped_at": stamp})
    return out


def _esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_digest(entries, feed_url="http://127.0.0.1:8000/"):
    day = datetime.now(timezone.utc).date().isoformat()
    subject = f"AI nuggets · {day} · {len(entries)} new"
    rows = []
    for e in entries:
        rows.append(
            '<div style="margin:0 0 18px;padding:14px 16px;border:1px solid #e3e5dc;border-radius:12px">'
            f'<div style="color:#0a4b3d;font-size:12px;font-weight:600">{_esc(e["site"])}</div>'
            '<div style="font-size:16px;font-weight:600;margin:4px 0 6px">'
            f'<a href="{_esc(e["url"])}" style="color:#15201a;text-decoration:none">{_esc(e["title"])}</a></div>'
            f'<div style="color:#57615a;font-size:14px;line-height:1.5">{_esc(e["nugget"])}</div>'
            '</div>')
    html = (
        '<div style="font-family:system-ui,-apple-system,Segoe UI,sans-serif;max-width:600px;margin:0 auto">'
        f'<h2 style="font-size:18px">Fresh from the AI labs · {day}</h2>'
        f'{"".join(rows)}'
        f'<p style="font-size:13px"><a href="{_esc(feed_url)}">Open the full feed →</a></p>'
        '</div>')
    return subject, html


def send_digest(subject, html, api_key, sender, to):
    resp = httpx.post(RESEND_ENDPOINT,
                      headers={"Authorization": f"Bearer {api_key}"},
                      json={"from": sender, "to": [to], "subject": subject, "html": html},
                      timeout=30)
    resp.raise_for_status()
    return resp.json()


def main() -> None:
    load_dotenv()
    api_key = os.getenv("RESEND_API_KEY")
    to = os.getenv("DIGEST_TO")
    sender = os.getenv("DIGEST_FROM", "onboarding@resend.dev")
    feed_url = os.getenv("FEED_URL", "http://127.0.0.1:8000/")
    if not api_key or not to:
        raise SystemExit("Set RESEND_API_KEY and DIGEST_TO in .env")
    manifest = load_manifest(MANIFEST_PATH)
    state = load_state()
    entries = select_new_entries(manifest, state.get("last_sent"))
    if not entries:
        print("No new nuggets since last digest. Nothing sent.")
        return
    subject, html = build_digest(entries, feed_url=feed_url)
    send_digest(subject, html, api_key, sender, to)
    state["last_sent"] = max(e["scraped_at"] for e in entries)
    save_state(state)
    print(f"Sent digest with {len(entries)} nugget(s) to {to}.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_digest.py -v`
Expected: 4 passed.

- [ ] **Step 5: Update `.env.example`**

Append:

```
RESEND_API_KEY=
DIGEST_TO=
DIGEST_FROM=onboarding@resend.dev
FEED_URL=http://127.0.0.1:8000/
```

- [ ] **Step 6: Commit**

```bash
git add digest.py tests/test_digest.py .env.example
git commit -m "feat: daily nugget email digest via Resend"
```

---

### Task 5: More first-party lab blogs in `sites.py`

**Files:**
- Modify: `sites.py` (add entries), `api.py` (`SITE_LABELS` entries)
- Test: `tests/test_sites.py` (add a coverage/validity test)

**Interfaces:**
- Consumes: nothing new. Each entry uses the existing four keys: `name`, `listing_urls`, `article_url_pattern`, `render_js`.
- Produces: additional `SITES` entries and matching `SITE_LABELS` keys.

> These URL patterns are **best-guess and MUST be confirmed against the live site** before keeping them (site markup changes; a wrong pattern silently finds zero links). This is the same "correct per-site link patterns from a live probe" step used for the original sites. Keep only entries that pass the probe.

- [ ] **Step 1: Probe each candidate listing** (scraper venv) and inspect real hrefs

For each candidate, run (example shown for xAI):

```bash
~/.venvs/scrapling/bin/python - <<'PY'
from scraper import fetch_html
from scrapling.parser import Selector
url = "https://x.ai/blog"
html = fetch_html(url, render_js=True)
links = sorted(set(Selector(html).css("a::attr(href)").getall())) if html else []
for l in links:
    print(l)
PY
```

Read the printed hrefs and derive the regex that matches article links but not the listing/nav. Candidates to probe:

| name | listing_urls | starting-guess pattern | render_js |
|------|--------------|------------------------|-----------|
| `xai` | `https://x.ai/blog` | `r"x\.ai/blog/[^/]+/?$"` | True |
| `stability` | `https://stability.ai/news` | `r"stability\.ai/news/[^/]+/?$"` | True |
| `ai2` | `https://allenai.org/blog` | `r"allenai\.org/blog/[^/]+/?$"` | True |
| `together` | `https://www.together.ai/blog` | `r"together\.ai/blog/[^/]+/?$"` | True |
| `perplexity` | `https://www.perplexity.ai/hub/blog` | `r"perplexity\.ai/hub/blog/[^/]+/?$"` | True |
| `nvidia` | `https://blogs.nvidia.com/blog/category/generative-ai/` | `r"blogs\.nvidia\.com/blog/[a-z0-9-]+/?$"` | True |

- [ ] **Step 2: Add the confirmed entries** to the `SITES` list in `sites.py`, in the same dict format as the existing entries. Drop any candidate whose listing the probe couldn't fetch or that yields no article links from CI/local.

- [ ] **Step 3: Add matching labels** to `SITE_LABELS` in `api.py`, e.g.:

```python
    "xai": "xAI",
    "stability": "Stability AI",
    "ai2": "Allen AI (AI2)",
    "together": "Together AI",
    "perplexity": "Perplexity",
    "nvidia": "NVIDIA",
```

- [ ] **Step 4: Add a validity test** to `tests/test_sites.py`

```python
import re
import api
from sites import SITES


def test_every_site_has_valid_pattern_and_label():
    for s in SITES:
        assert {"name", "listing_urls", "article_url_pattern", "render_js"} <= set(s)
        re.compile(s["article_url_pattern"])          # compiles
        assert s["name"] in api.SITE_LABELS           # has a display label
```

- [ ] **Step 5: Run tests + a live smoke scrape of the new sites**

```bash
.venv/bin/python -m pytest tests/test_sites.py -v
# optional live check (scraper venv): confirms links are actually discovered
~/.venvs/scrapling/bin/python scraper.py    # watch the "+N new articles" lines for the new sites
```

Expected: tests pass; each kept site reports a non-zero discovery (or a logged reason if not).

- [ ] **Step 6: Commit**

```bash
git add sites.py api.py tests/test_sites.py
git commit -m "feat: add first-party lab blogs (xAI, Stability, AI2, ...) with labels"
```

---

### Task 6: Scheduled GitHub Actions pipeline + docs

**Files:**
- Create: `.github/workflows/daily.yml`
- Modify: `README.md`

**Interfaces:**
- Consumes: `scraper.py`, `nuggetize.py`, `digest.py`; repo secrets `ANTHROPIC_API_KEY`, `VOYAGE_API_KEY` (unused here but kept for parity), `RESEND_API_KEY`, `DIGEST_TO`, `DIGEST_FROM`.
- Produces: a daily cron that commits refreshed `data/` back to the repo. Does **not** run `ingest.py` or touch `chroma_db`.

- [ ] **Step 1: Create the workflow**

```yaml
# .github/workflows/daily.yml
name: daily-nuggets
on:
  schedule:
    - cron: "0 13 * * *"   # 13:00 UTC daily
  workflow_dispatch: {}
permissions:
  contents: write
concurrency:
  group: daily-nuggets
  cancel-in-progress: false
jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install RAG deps
        run: |
          python -m venv .venv
          .venv/bin/pip install -r requirements.txt
      - name: Install scraper (scrapling) deps
        run: |
          python -m venv .venv-scrapling
          .venv-scrapling/bin/pip install scrapling
          .venv-scrapling/bin/python -m playwright install --with-deps chromium || true
      - name: Scrape
        run: .venv-scrapling/bin/python scraper.py
      - name: Nuggetize
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: .venv/bin/python nuggetize.py
      - name: Email digest
        env:
          RESEND_API_KEY: ${{ secrets.RESEND_API_KEY }}
          DIGEST_TO: ${{ secrets.DIGEST_TO }}
          DIGEST_FROM: ${{ secrets.DIGEST_FROM }}
        run: .venv/bin/python digest.py
      - name: Commit refreshed data
        run: |
          git config user.name "yashchopra0202-code"
          git config user.email "yashchopra0202@gmail.com"
          git add data/articles data/manifest.json data/digest_state.json
          git diff --cached --quiet || git commit -m "chore: daily nugget refresh [skip ci]"
          git push
```

- [ ] **Step 2: Confirm `chroma_db/` is git-ignored** (so a stray local index never gets committed by the workflow's `git add data/...` — it won't, but verify the repo hygiene)

Run: `grep -n chroma .gitignore`
Expected: `chroma_db/` (or equivalent) is present. If absent, add it.

- [ ] **Step 3: Document in `README.md`**

Add a "Daily nuggets" section covering: the new run order (`scraper.py` → `nuggetize.py` → `ingest.py` → `digest.py`), what a nugget is and where it's stored (`manifest.json`), the `/feed` endpoint + Today view, the Resend env vars, and the GitHub Actions schedule + required repo secrets (`ANTHROPIC_API_KEY`, `RESEND_API_KEY`, `DIGEST_TO`, `DIGEST_FROM`). Note explicitly that CI does **not** build the vector index; run `ingest.py` locally for `/ask`.

- [ ] **Step 4: Validate the workflow end-to-end (the flagged risk)**

After the repo is on GitHub and secrets are set, trigger it manually:
- GitHub → Actions → **daily-nuggets** → **Run workflow** (`workflow_dispatch`).
- Inspect the **Scrape** step log: confirm which sites returned articles and which hit bot walls from the CI IP.
- Confirm the digest email arrived and the **Commit refreshed data** step pushed a commit.

**If scraping is unreliable from CI** (the flagged Cloudflare/bot-wall risk): fall back to running `scraper.py` on the Mac via `launchd`, and reduce the workflow to `nuggetize.py` + `digest.py` + commit only. Record whichever outcome holds in the README.

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/daily.yml README.md .gitignore
git commit -m "feat: daily GitHub Actions pipeline + docs"
```

---

## Self-Review

**Spec coverage:** nuggetize (T1); `/feed` (T2); Today view (T3); digest + `.env` (T4); more first-party sites (T5); GitHub Actions cron, README, no-chroma-in-CI (T6); output escaping on both surfaces (`textContent` T3, `_esc` T4); trust boundary (T5 first-party only); CI-scraping risk validation + fallback (T6 Step 4). All spec sections map to a task.

**Placeholder scan:** No "TBD"/"handle edge cases" steps. Task 5's URL patterns are explicitly marked best-guess-pending-live-probe with a concrete probe command — this is a discovery step with real content, not a placeholder.

**Type consistency:** `nuggetize_manifest(manifest, articles_dir, llm, save=None) -> int` and `summarize_article(body, llm) -> str` used consistently (T1). `feed_data(days) -> {days, groups:[{date, items:[...]}]}` matches the T2 test and the T3 consumer field names (`label`, `title`, `nugget`, `url`). `select_new_entries` / `build_digest` / `send_digest` signatures match their tests (T4). Manifest fields `nugget` / `nugget_at` / `scraped_at` used identically across T1, T2, T4.
