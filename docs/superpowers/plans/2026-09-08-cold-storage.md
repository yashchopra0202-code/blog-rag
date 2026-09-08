# Cold Storage (Phase 4) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move raw article `.md` out of git into Supabase Storage (bucket `article-archive`) as the durable source of truth, with `ingest.py` rebuilding the `/ask` index from Storage at deploy — while keeping the merge behavior-preserving (dual-write) and isolating the git-removal + Render cutover as explicit ordered steps.

**Architecture:** A new `article_store.py` wraps the Supabase Storage REST API over `httpx` (same creds/pattern as `store.py`). A post-scrape `upload_articles.py` step uploads local `.md`; `ingest.py` downloads all articles from Storage before building; `api.corpus_stats` switches from globbing `data/articles/` to counting the manifest. The six code tasks are safe to merge (Storage is additive/dual-write, `ingest` falls back to on-disk files when creds are absent); a separate **Cutover** section does the backfill, git removal, Render creds, and deploy in the load-bearing order.

**Tech Stack:** Python 3.12, httpx (Supabase Storage REST), stdlib, pytest.

**Spec:** `docs/superpowers/specs/2026-09-08-blog-rag-cold-storage-design.md`

## Global Constraints

- **Python 3.12; NO new dependencies** — only `httpx` + stdlib.
- **Test gate command:** `.venv/bin/python -m pytest -q --ignore=tests/test_extraction.py` — must stay green (baseline 119 tests).
- **Tests require no live Storage** — all `httpx` is monkeypatched; Supabase env set via `monkeypatch.setenv`.
- **Supabase Storage REST:** base `{SUPABASE_URL}/storage/v1`; auth headers `{"Authorization": "Bearer <SUPABASE_SERVICE_KEY>", "apikey": "<SUPABASE_SERVICE_KEY>"}`; service-role key is server/build-side only.
- **Bucket:** `article-archive` (private). **Object key = the file basename** (already unique `{site}__{slug}.md`).
- **Merge stays behavior-preserving:** do NOT add `data/articles/` to `.gitignore`, do NOT `git rm --cached`, and do NOT change the daily commit-back's `git add` in the six code tasks — those are Cutover steps.
- **Commit trailer** on every commit body:
  `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`
  `Claude-Session: https://claude.ai/code/session_01TQ1fNc6CoWAnrjCSMC2fNn`
- **Branch:** feature branch `feat/cold-storage`, not `main`.

## File structure

- **`article_store.py`** (new) — Supabase Storage REST client. One responsibility: article-object I/O.
- **`upload_articles.py`** (new) — pipeline step: upload local `.md` to Storage.
- **`ingest.py`** (modify) — download from Storage before building the index.
- **`api.py`** (modify `corpus_stats` only) — count from the manifest.
- **`render.yaml`** / **`.github/workflows/daily.yml`** (modify) — make creds available at build + add the dual-write upload step.
- **`scripts/backfill_articles.py`** (new) — one-time backfill.

---

### Task 1: `article_store.py` — Supabase Storage REST client

**Files:**
- Create: `article_store.py`
- Create: `tests/test_article_store.py`

**Interfaces:**
- Produces:
  - `article_store._creds_present() -> bool` — both `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` set.
  - `article_store.ensure_bucket() -> None` — create the private `article-archive` bucket; idempotent (a 400/409 "already exists" is success).
  - `article_store.upload_article(local_path: str) -> None` — upsert the file's bytes to `article-archive/<basename>`.
  - `article_store.download_all(dest_dir: str) -> int` — list every object and download each into `dest_dir`; returns the count.
  - `article_store.BUCKET = "article-archive"`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_article_store.py`:

```python
import article_store

class _Resp:
    def __init__(self, data=None, code=200, content=b""):
        self._d = data if data is not None else {}
        self.status_code = code
        self.content = content
    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"http {self.status_code}")
    def json(self): return self._d

def _env(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://proj.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_KEY", "svc-key")

def test_creds_present(monkeypatch):
    _env(monkeypatch)
    assert article_store._creds_present() is True
    monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)
    assert article_store._creds_present() is False

def test_upload_article_upserts_bytes(monkeypatch, tmp_path):
    _env(monkeypatch)
    f = tmp_path / "openai-index__hello.md"
    f.write_text("---\nurl: u\n---\nbody", encoding="utf-8")
    seen = {}
    def fake_post(url, headers=None, content=None, timeout=None):
        seen.update(url=url, headers=headers, content=content); return _Resp()
    monkeypatch.setattr(article_store.httpx, "post", fake_post)
    article_store.upload_article(str(f))
    assert seen["url"] == "https://proj.supabase.co/storage/v1/object/article-archive/openai-index__hello.md"
    assert seen["headers"]["x-upsert"] == "true"
    assert seen["headers"]["Authorization"] == "Bearer svc-key"
    assert seen["content"] == b"---\nurl: u\n---\nbody"

def test_ensure_bucket_idempotent(monkeypatch):
    _env(monkeypatch)
    monkeypatch.setattr(article_store.httpx, "post",
                        lambda url, headers=None, json=None, timeout=None: _Resp(code=409))
    article_store.ensure_bucket()   # must NOT raise on already-exists

def test_download_all_lists_then_gets(monkeypatch, tmp_path):
    _env(monkeypatch)
    pages = [[{"name": "a.md"}, {"name": "b.md"}], []]   # one full-ish page then empty
    def fake_post(url, headers=None, json=None, timeout=None):
        assert url.endswith("/object/list/article-archive")
        return _Resp(data=pages.pop(0))
    def fake_get(url, headers=None, timeout=None):
        return _Resp(content=("body of " + url.rsplit("/", 1)[1]).encode())
    monkeypatch.setattr(article_store.httpx, "post", fake_post)
    monkeypatch.setattr(article_store.httpx, "get", fake_get)
    n = article_store.download_all(str(tmp_path))
    assert n == 2
    assert (tmp_path / "a.md").read_text() == "body of a.md"
    assert (tmp_path / "b.md").read_text() == "body of b.md"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_article_store.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'article_store'`.

- [ ] **Step 3: Create `article_store.py`**

```python
"""Supabase Storage REST client for the article archive (over httpx — no SDK).
Service-role key: server/build-side only. Bucket holds one object per article,
keyed by the file basename."""
import os
import httpx

BUCKET = "article-archive"
_LIST_PAGE = 100


def _conf():
    url = os.environ["SUPABASE_URL"].rstrip("/")
    key = os.environ["SUPABASE_SERVICE_KEY"]
    return url, {"Authorization": f"Bearer {key}", "apikey": key}


def _creds_present() -> bool:
    return bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_KEY"))


def ensure_bucket() -> None:
    url, headers = _conf()
    r = httpx.post(f"{url}/storage/v1/bucket",
                   headers={**headers, "Content-Type": "application/json"},
                   json={"id": BUCKET, "name": BUCKET, "public": False}, timeout=30)
    if r.status_code in (400, 409):   # already exists — fine
        return
    r.raise_for_status()


def upload_article(local_path: str) -> None:
    url, headers = _conf()
    name = os.path.basename(local_path)
    with open(local_path, "rb") as f:
        body = f.read()
    r = httpx.post(f"{url}/storage/v1/object/{BUCKET}/{name}",
                   headers={**headers, "Content-Type": "text/markdown", "x-upsert": "true"},
                   content=body, timeout=60)
    r.raise_for_status()


def download_all(dest_dir: str) -> int:
    url, headers = _conf()
    os.makedirs(dest_dir, exist_ok=True)
    names, offset = [], 0
    while True:
        r = httpx.post(f"{url}/storage/v1/object/list/{BUCKET}",
                       headers={**headers, "Content-Type": "application/json"},
                       json={"prefix": "", "limit": _LIST_PAGE, "offset": offset}, timeout=30)
        r.raise_for_status()
        page = r.json()
        names += [o["name"] for o in page if o.get("name")]
        if len(page) < _LIST_PAGE:
            break
        offset += _LIST_PAGE
    for name in names:
        g = httpx.get(f"{url}/storage/v1/object/{BUCKET}/{name}", headers=headers, timeout=60)
        g.raise_for_status()
        with open(os.path.join(dest_dir, name), "wb") as f:
            f.write(g.content)
    return len(names)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_article_store.py -v`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add article_store.py tests/test_article_store.py
git commit -m "$(cat <<'EOF'
feat(storage): article_store.py — Supabase Storage REST client

upload_article (upsert), download_all (list+get), ensure_bucket
(idempotent), _creds_present — over httpx, service-role key, no SDK.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01TQ1fNc6CoWAnrjCSMC2fNn
EOF
)"
```

---

### Task 2: `upload_articles.py` — post-scrape upload step

**Files:**
- Create: `upload_articles.py`
- Create: `tests/test_upload_articles.py`

**Interfaces:**
- Consumes: `article_store.ensure_bucket`, `article_store.upload_article` (Task 1).
- Produces: `upload_articles.upload_dir(articles_dir="data/articles") -> dict` returning `{"uploaded", "failed"}`; `main()` (loads dotenv, calls `upload_dir`).

- [ ] **Step 1: Write the failing test**

Create `tests/test_upload_articles.py`:

```python
import upload_articles

def test_upload_dir_best_effort(monkeypatch, tmp_path):
    (tmp_path / "a__x.md").write_text("A", encoding="utf-8")
    (tmp_path / "b__y.md").write_text("B", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("skip", encoding="utf-8")   # non-.md ignored
    monkeypatch.setattr(upload_articles.article_store, "ensure_bucket", lambda: None)
    uploaded = []
    def fake_upload(path):
        if path.endswith("b__y.md"):
            raise RuntimeError("storage down")   # one failure must not abort
        uploaded.append(path)
    monkeypatch.setattr(upload_articles.article_store, "upload_article", fake_upload)
    out = upload_articles.upload_dir(str(tmp_path))
    assert out == {"uploaded": 1, "failed": 1}
    assert any(p.endswith("a__x.md") for p in uploaded)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_upload_articles.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'upload_articles'`.

- [ ] **Step 3: Create `upload_articles.py`**

```python
"""Upload local article .md files to Supabase Storage (run after scrape, in the
project venv). Best-effort per file. Because data/articles is gitignored, a CI
checkout only holds THIS run's new articles — so this naturally uploads just the
new ones while ingest.py downloads the full set."""
import glob
import os
from dotenv import load_dotenv

import article_store

ARTICLES_DIR = "data/articles"


def upload_dir(articles_dir=ARTICLES_DIR):
    article_store.ensure_bucket()
    uploaded = failed = 0
    for path in sorted(glob.glob(os.path.join(articles_dir, "*.md"))):
        try:
            article_store.upload_article(path)
            uploaded += 1
        except Exception as e:  # noqa: BLE001 - one bad file must not abort the run
            print(f"  [warn] upload failed for {path}: {e}")
            failed += 1
    print(f"Uploaded {uploaded} article(s) to Storage; {failed} failed.")
    return {"uploaded": uploaded, "failed": failed}


def main():
    load_dotenv()
    upload_dir()


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_upload_articles.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add upload_articles.py tests/test_upload_articles.py
git commit -m "$(cat <<'EOF'
feat(storage): upload_articles.py — post-scrape upload step

Uploads local data/articles/*.md to Storage best-effort (ensure_bucket
first). Naturally incremental: a gitignored checkout holds only the run's
new articles.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01TQ1fNc6CoWAnrjCSMC2fNn
EOF
)"
```

---

### Task 3: `ingest.py` — download from Storage before building

**Files:**
- Modify: `ingest.py`
- Test: `tests/test_ingest.py` (new)

**Interfaces:**
- Consumes: `article_store._creds_present`, `article_store.download_all` (Task 1); existing `rag_core.load_articles`, `rag_core.chunk_documents`, `rag_core.reset_index_dir`, `rag_core.build_index`, `rag_core.require_env`.
- Produces: a `prepare_articles(articles_dir) -> int | None` helper (downloads when creds present, returns count; returns `None` and warns when absent) called at the top of `main()`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_ingest.py`:

```python
import ingest

def test_prepare_articles_downloads_when_creds(monkeypatch):
    monkeypatch.setattr(ingest.article_store, "_creds_present", lambda: True)
    called = {}
    monkeypatch.setattr(ingest.article_store, "download_all",
                        lambda dest: called.setdefault("dest", dest) or 5)
    n = ingest.prepare_articles("data/articles")
    assert n == 5 and called["dest"] == "data/articles"

def test_prepare_articles_skips_without_creds(monkeypatch):
    monkeypatch.setattr(ingest.article_store, "_creds_present", lambda: False)
    calls = {"n": 0}
    monkeypatch.setattr(ingest.article_store, "download_all",
                        lambda dest: calls.__setitem__("n", calls["n"] + 1))
    assert ingest.prepare_articles("data/articles") is None
    assert calls["n"] == 0   # did not hit Storage
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_ingest.py -v`
Expected: FAIL — `AttributeError: module 'ingest' has no attribute 'prepare_articles'` (and `article_store` not imported).

- [ ] **Step 3: Modify `ingest.py`**

Replace the file contents with:

```python
# ingest.py
from dotenv import load_dotenv
import rag_core
import article_store

ARTICLES_DIR = "data/articles"
PERSIST_DIR = "chroma_db"


def prepare_articles(articles_dir=ARTICLES_DIR):
    """Populate the local articles dir from Supabase Storage (the source of
    truth) when creds are present; otherwise leave whatever is on disk (offline
    dev). Returns the downloaded count, or None when skipped."""
    if article_store._creds_present():
        n = article_store.download_all(articles_dir)
        print(f"Downloaded {n} article(s) from Storage into {articles_dir}/.")
        return n
    print("[warn] SUPABASE creds absent — using on-disk articles (offline dev).")
    return None


def main() -> None:
    load_dotenv()
    rag_core.require_env("VOYAGE_API_KEY")
    prepare_articles(ARTICLES_DIR)
    docs = rag_core.load_articles(ARTICLES_DIR)
    if not docs:
        raise SystemExit(f"No articles in {ARTICLES_DIR}/. Run the scraper first.")
    chunks = rag_core.chunk_documents(docs)
    print(f"Rebuilding index in {PERSIST_DIR}/ ...")
    rag_core.reset_index_dir(PERSIST_DIR)
    rag_core.build_index(chunks, PERSIST_DIR)
    print(f"Indexed {len(chunks)} chunks from {len(docs)} articles into {PERSIST_DIR}/.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the test + full gate**

Run: `.venv/bin/python -m pytest tests/test_ingest.py -v && .venv/bin/python -m pytest -q --ignore=tests/test_extraction.py`
Expected: PASS; whole suite green.

- [ ] **Step 5: Commit**

```bash
git add ingest.py tests/test_ingest.py
git commit -m "$(cat <<'EOF'
feat(ingest): rebuild the index from Storage when creds are present

ingest.prepare_articles downloads all articles from Supabase Storage
before building (Render build path); falls back to on-disk files for
offline local dev. Still SystemExits on zero articles.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01TQ1fNc6CoWAnrjCSMC2fNn
EOF
)"
```

---

### Task 4: `api.corpus_stats` — count from the manifest

**Files:**
- Modify: `api.py` (`corpus_stats`, at `api.py:185`)
- Modify: `tests/test_api.py`

**Interfaces:**
- Consumes: existing `api.MANIFEST_PATH`, `api.SITE_LABELS`.
- Produces: `corpus_stats()` returns the same shape (`{"articles": int, "sites": [{"name","label","count"}], "updated": str}`) but sourced from the manifest, not a `data/articles/` glob.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_api.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_api.py -k corpus_stats -v`
Expected: FAIL — current `corpus_stats` globs `data/articles/` (ignores `MANIFEST_PATH` for counts), so counts won't match the manifest fixture.

- [ ] **Step 3: Rewrite `corpus_stats` in `api.py`**

Replace the `corpus_stats` function body (currently `api.py:185`) with:

```python
def corpus_stats() -> dict:
    """Counts + freshness for the discovery UI, read from the manifest (no
    article files needed — they live in Storage, not on the Render fs)."""
    try:
        with open(MANIFEST_PATH, encoding="utf-8") as f:
            manifest = json.load(f)
    except (OSError, ValueError):
        return {"articles": 0, "sites": [], "updated": ""}
    counts = Counter(v.get("site", "") for v in manifest.values() if v.get("site"))
    sites = [{"name": s, "label": SITE_LABELS.get(s, s), "count": n}
             for s, n in counts.most_common()]
    dates = [(v.get("scraped_at", "") or "")[:10] for v in manifest.values() if v.get("scraped_at")]
    updated = max(dates) if dates else ""
    return {"articles": len(manifest), "sites": sites, "updated": updated}
```

(`glob` may now be unused in `api.py` — check with `grep -n "glob" api.py`; if `corpus_stats` was its only user, remove the `import glob` line.)

- [ ] **Step 4: Run the test + full gate**

Run: `.venv/bin/python -m pytest tests/test_api.py -k corpus_stats -v && .venv/bin/python -m pytest -q --ignore=tests/test_extraction.py`
Expected: PASS; whole suite green.

- [ ] **Step 5: Commit**

```bash
git add api.py tests/test_api.py
git commit -m "$(cat <<'EOF'
refactor(api): corpus_stats counts from the manifest, not the files dir

Articles will live in Storage (not on the Render fs), so stats now derive
from manifest entries instead of globbing data/articles. Same output shape.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01TQ1fNc6CoWAnrjCSMC2fNn
EOF
)"
```

---

### Task 5: Wire the pipeline (dual-write) — `daily.yml` upload step + `render.yaml` build creds

**Files:**
- Modify: `.github/workflows/daily.yml`
- Modify: `render.yaml`

**Interfaces:**
- Consumes: `upload_articles.py` (Task 2); `SUPABASE_URL`/`SUPABASE_SERVICE_KEY` GitHub secrets (already set for Telegram) and Render env.
- Produces: a dual-write daily pipeline (articles committed to git AND uploaded to Storage) + Storage creds available to the Render build. **Does NOT** change the commit-back `git add` or `.gitignore` (those are Cutover).

- [ ] **Step 1: Add the upload step to `daily.yml`**

In `.github/workflows/daily.yml`, immediately after the `Scrape` step (id `scrape`) and before `Nuggetize`, add:

```yaml
      - name: Upload articles to Storage
        id: upload_articles
        continue-on-error: true
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}
        run: .venv/bin/python upload_articles.py
```

- [ ] **Step 2: Add build creds to `render.yaml`**

In `render.yaml`, under the web service's `envVars:`, add (alongside the existing `VOYAGE_API_KEY`/`ANTHROPIC_API_KEY`):

```yaml
      - key: SUPABASE_URL          # ingest.py downloads the article archive at BUILD
        sync: false
      - key: SUPABASE_SERVICE_KEY  # service-role; build + runtime, dashboard secret
        sync: false
```

- [ ] **Step 3: Validate the YAML**

Run: `.venv/bin/python -c "import yaml; yaml.safe_load(open('.github/workflows/daily.yml')); yaml.safe_load(open('render.yaml')); print('yaml ok')"`
Expected: `yaml ok`.

- [ ] **Step 4: Confirm the suite still green (no code changed)**

Run: `.venv/bin/python -m pytest -q --ignore=tests/test_extraction.py`
Expected: whole suite green (unchanged count).

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/daily.yml render.yaml
git commit -m "$(cat <<'EOF'
ci: dual-write article upload step + Storage creds for the Render build

daily.yml uploads scraped articles to Storage (continue-on-error) while
still committing them to git (dual-write, safe pre-cutover). render.yaml
declares SUPABASE_URL/SERVICE_KEY so the build's ingest can download.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01TQ1fNc6CoWAnrjCSMC2fNn
EOF
)"
```

---

### Task 6: `scripts/backfill_articles.py` — one-time backfill

**Files:**
- Create: `scripts/backfill_articles.py`
- Test: covered by reusing `upload_articles.upload_dir` — a thin wrapper, so a light test asserts it delegates.
- Create/Modify test: `tests/test_upload_articles.py` (add one test)

**Interfaces:**
- Consumes: `upload_articles.upload_dir` (Task 2).
- Produces: `scripts/backfill_articles.py` `main()` that uploads all of `data/articles/` to Storage (one-time).

- [ ] **Step 1: Write the failing test**

Add to `tests/test_upload_articles.py`:

```python
def test_backfill_delegates_to_upload_dir(monkeypatch):
    import importlib.util, os
    spec = importlib.util.spec_from_file_location(
        "backfill_articles", os.path.join("scripts", "backfill_articles.py"))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    called = {}
    monkeypatch.setattr(mod.upload_articles, "upload_dir",
                        lambda d="data/articles": called.setdefault("d", d) or {"uploaded": 3, "failed": 0})
    monkeypatch.setattr(mod, "load_dotenv", lambda: None)
    mod.main()
    assert called["d"] == "data/articles"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_upload_articles.py -k backfill -v`
Expected: FAIL — `scripts/backfill_articles.py` does not exist.

- [ ] **Step 3: Create `scripts/backfill_articles.py`**

```python
"""One-time: upload every existing data/articles/*.md to Supabase Storage.
Run once, before removing articles from git (see the plan's Cutover section).
`upload_dir` calls ensure_bucket first, so this also creates the bucket."""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import upload_articles


def main():
    load_dotenv()
    result = upload_articles.upload_dir("data/articles")
    print(f"Backfill complete: {result}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the test + full gate**

Run: `.venv/bin/python -m pytest tests/test_upload_articles.py -v && .venv/bin/python -m pytest -q --ignore=tests/test_extraction.py`
Expected: PASS; whole suite green.

- [ ] **Step 5: Commit**

```bash
git add scripts/backfill_articles.py tests/test_upload_articles.py
git commit -m "$(cat <<'EOF'
feat(storage): scripts/backfill_articles.py — one-time archive backfill

Uploads all existing data/articles to Storage (ensure_bucket + upload_dir).
Run once before the git-removal cutover.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01TQ1fNc6CoWAnrjCSMC2fNn
EOF
)"
```

---

## Cutover (post-merge, ORDER IS LOAD-BEARING — not code tasks)

Do these only after the six tasks merge to `main`. Each is deliberate; do not reorder.

1. **Backfill (controller, local `.env` has creds):** run `.venv/bin/python scripts/backfill_articles.py`. **Verify:** the reported `uploaded` count equals `ls data/articles | wc -l` (~293) and `failed == 0`. If any failed, re-run before proceeding.
2. **Render build creds (USER — go-live gate):** set `SUPABASE_URL` + `SUPABASE_SERVICE_KEY` in the Render service's environment (Dashboard → Environment). Until this is done, do NOT push the git-removal commit — a build would download nothing and deploy an empty index.
3. **Leave git (controller, after 1 & 2 confirmed):** on a branch,
   ```bash
   printf '\ndata/articles/\n' >> .gitignore
   git rm -r --cached data/articles
   ```
   and change the daily commit-back `git add` in `.github/workflows/daily.yml` to drop `data/articles` (keep `data/manifest.json data/digest_state.json data/telegram_state.json`). Commit + merge + push.
4. **Deploy + verify:** the push triggers a Render redeploy. **Verify in the build log:** "Downloaded N article(s) from Storage" with N ≈ corpus size; then hit the live site: `/stats` shows the corpus count (from the manifest) and `/ask` returns a real cited answer. If the index is empty, roll back step 3's commit (articles are still in git history) and recheck creds.

---

## Self-Review

**1. Spec coverage:**
- `article_store.py` (upload/download/ensure_bucket/creds) → Task 1. ✓
- Post-scrape upload step in the project venv → Task 2 + Task 5 (wired into daily.yml). ✓
- `ingest.py` downloads from Storage at build, disk fallback offline → Task 3. ✓
- `corpus_stats` → manifest counts → Task 4. ✓
- `render.yaml` build creds → Task 5. ✓
- `.gitignore` + `git rm --cached` + commit-back change → Cutover step 3 (deliberately not a code task, per spec's "merge stays behavior-preserving"). ✓
- Backfill of 293 → Task 6 (script) + Cutover step 1 (run it). ✓
- Bucket `article-archive` private, auto-created → Task 1 `ensure_bucket`, invoked by Task 2/6. ✓
- Load-bearing ordering (backfill → creds → git removal → deploy) → Cutover section. ✓

**2. Placeholder scan:** No TBD/TODO/"handle edge cases". Every code step has concrete code and exact commands.

**3. Type consistency:** `_creds_present()`, `ensure_bucket()`, `upload_article(path)`, `download_all(dest)->int`, `BUCKET` are used identically across Tasks 1/2/3/6. `upload_dir(articles_dir)->{"uploaded","failed"}` consistent in Tasks 2/6. `prepare_articles(articles_dir)->int|None` consistent in Task 3. `corpus_stats()` output shape matches the existing consumers (`/stats`). Storage REST URLs identical between `article_store.py` and its tests.

## Notes / follow-ups (not this plan)
- Upload verification / reconcile pass (a silent upload miss isn't auto-retried) — deferred per spec.
- Prebuilt-index-in-Storage (skip Render's rebuild entirely) — a later optimization.
