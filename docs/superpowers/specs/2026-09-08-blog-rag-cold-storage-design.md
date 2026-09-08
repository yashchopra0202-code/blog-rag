# Cold Storage (Phase 4) — Design Spec

**Date:** 2026-09-08
**Status:** Approved design, pending spec review → implementation plan
**Repo:** `~/blog-rag` (FastAPI + RAG on Render, daily pipeline via GitHub Actions)
**Parent:** `docs/superpowers/specs/2026-09-08-blog-rag-production-roadmap-design.md` (Phase 4)

## Goal

Move the raw scraped article `.md` files out of git into **Supabase Storage** as the durable source of truth, so the git repo stops accumulating article content on every daily commit while nothing is lost. The manifest (in git) keeps a pointer per article; the `/ask` vector index is rebuilt from Storage at deploy time. Backfill the existing ~293 articles and wire the Render build to Storage.

## Decisions (locked with the user)

| Decision | Choice | Rationale |
|---|---|---|
| Source of truth | **Supabase Storage; articles leave git** | Meets "git stops bloating" + durable archive. Higher blast radius (touches `/ask` rebuild) accepted. |
| Render index rebuild | **`ingest.py` downloads articles from Storage at build** | Smallest change; keeps the rebuild-on-deploy model. Needs SUPABASE creds in Render's BUILD env. |
| Upload location | **New post-scrape step in the project venv** | Keeps Storage I/O out of the separate scrapling venv; scraper stays unchanged. |
| Scope | **Full: code + backfill + wire Render, this phase** | Go-live gated on the user setting Render build creds. |
| Bucket | `article-archive` (private), auto-created by the backfill | One private bucket; service-role access only. |

## Non-goals (v1 / YAGNI)

- **No incremental-diff upload logic.** Because `data/articles/` becomes gitignored, a fresh CI checkout is empty and the scraper (which dedups via the committed *manifest*, not files) writes only the run's new articles locally — so "upload every local `.md`" is already incremental. No explicit diffing.
- **No prebuilt-index-in-Storage.** Render still rebuilds the index from articles at deploy (the alternative — CI builds + uploads the 71 MB index — is a later optimization, not now).
- **No change to the scraper or the scrapling venv.** The scraper still writes `.md` locally; a separate project-venv step uploads.
- **No migration of the manifest, nuggets, or `chroma_db` off their current homes.** Only article `.md` bodies move.
- **No public/CDN serving of article files.** The bucket is private; only the pipeline (upload) and the build (download) touch it via the service-role key.

## Key constraints (surfaced, not assumed)

1. **Articles-in-git is currently the delivery mechanism for the index**, not just storage: the daily Action commits `data/articles/` → the push auto-redeploys Render → Render's build runs `ingest.py`, which reads `data/articles/` from the checkout to rebuild Chroma. Removing articles from git must replace **both** the build-time article source (→ download from Storage) and keep a redeploy trigger (→ the still-committed `manifest.json`).
2. **The scraper dedups via the manifest, not local files** (`scrape_site` builds `todo` from URLs absent in `manifest`). So an empty `data/articles/` on a fresh checkout is fine — only genuinely new URLs are fetched/written/uploaded.
3. **At runtime, Render needs no article files** — `/ask` answers from the Chroma index (built at deploy). The only runtime reader of `data/articles/` is `api.py:corpus_stats` (a `glob`), which must switch to manifest-based counts since the dir won't exist on Render.
4. **`ingest.py` runs in two places** — locally (dev) and in the Render build. It must work with creds (download from Storage) and degrade for offline local dev (use whatever `.md` are on disk).
5. **Supabase service-role key is server-side/build-side only.** It must be set in Render's build env (new) in addition to runtime; never shipped to the browser.
6. **Cutover ordering is load-bearing:** articles must be backfilled to Storage *before* they leave git / before a Render deploy, or the build produces an empty index and `/ask` breaks.

## Architecture / data flow

```
  SCRAPE (scrapling venv)  →  data/articles/*.md   (local working files — now GITIGNORED)
        │                              │
        │                     UPLOAD step (project venv): article_store.upload_article() per file
        │                              │  (httpx → Supabase Storage REST, x-upsert)
        ▼                              ▼
   manifest.json (git; has        SUPABASE STORAGE  bucket `article-archive`  (durable source of truth)
   per-entry "file" pointer)            ▲
   committed by daily Action            │ article_store.download_all(dest)
   → push auto-redeploys Render   ┌──────┴──────────────────────────────────┐
                                  │ ingest.py (Render build): download all → rag_core builds Chroma │
                                  └─────────────────────────────────────────┘
   RUNTIME (Render): /ask ← Chroma index (no article files needed);
                     /stats ← manifest counts;  /feed,/articles ← manifest (already)
```

## Components (files)

- **`article_store.py`** *(new, project venv)* — Supabase Storage REST over `httpx`, creds from `SUPABASE_URL` + `SUPABASE_SERVICE_KEY` (reuse the `store.py` header pattern). Bucket `article-archive`, object key = the file basename.
  - `ensure_bucket()` — `POST /storage/v1/bucket` `{id, name, public:false}`; idempotent (ignore "already exists").
  - `upload_article(local_path)` — read bytes, `POST /storage/v1/object/article-archive/<basename>` with header `x-upsert: true`, `Content-Type: text/markdown`.
  - `download_all(dest_dir)` — `POST /storage/v1/object/list/article-archive` (paginate `{prefix,limit,offset}`), then `GET /storage/v1/object/article-archive/<name>` each into `dest_dir`; returns count.
  - `_creds_present()` helper (both env vars set) so callers can branch.
- **`upload_articles.py`** *(new, tiny)* — `main()`: `load_dotenv()`; for each `data/articles/*.md`, `article_store.upload_article(f)` best-effort (one failure logs + continues); print a count. Pipeline step after scrape.
- **`ingest.py`** *(change)* — before `rag_core.load_articles`: if `article_store._creds_present()`, `article_store.download_all(ARTICLES_DIR)` (print count); else print a warning and use on-disk files. Unchanged otherwise; still `SystemExit` if zero docs.
- **`api.py:corpus_stats`** *(change)* — build `sites`/`articles` counts from `manifest.values()` (`site` field) instead of `glob(data/articles/*.md)`; `articles` total = number of manifest entries. `updated` already from manifest. No dir access.
- **`.gitignore`** *(change)* — add `data/articles/`.
- **git tracking** — `git rm -r --cached data/articles` (stop tracking; local files + history retained).
- **`render.yaml`** *(change)* — add `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` to `envVars` (`sync:false`); build command unchanged (now `ingest` pulls from Storage).
- **`.github/workflows/daily.yml`** *(change)* — add an "Upload articles" step after Scrape (project venv; env `SUPABASE_URL`/`SUPABASE_SERVICE_KEY`); change the commit-back `git add` to drop `data/articles` (keep `manifest.json`, `digest_state.json`, `telegram_state.json`).
- **`scripts/backfill_articles.py`** *(new, one-time)* — `ensure_bucket()` then upload every existing `data/articles/*.md`; print progress + final count.

## Error handling

- **Upload:** best-effort per file (log + continue); the daily run never aborts on an upload failure. A missed upload self-heals — the local file is only in *this* checkout, so a failed upload means that article isn't in Storage; acceptable at this scale, and re-running catches nothing (checkout is fresh) — so uploads must be verified in the go-live check (see Rollout). (Future hardening: verify-after-upload.)
- **Download (ingest/build):** if creds present but `download_all` returns 0 into an empty dir → the existing "No articles" `SystemExit` fires and the build fails loudly rather than deploying an empty index.
- **Stats:** manifest read already guarded (`try/except (OSError, ValueError)`), returns empty counts on failure.

## Security

- Private bucket; all access via the service-role key, server/build-side only. Never in the browser (no page fetches article files).
- Object keys are the existing safe basenames (`{site}__{slug}.md`, already slugified) — no path traversal.

## Testing (TDD)

All Storage I/O mocked (`httpx`) — buildable green without a live bucket:
- `article_store`: `upload_article` posts to the right URL with `x-upsert`; `download_all` lists then GETs each and writes files (fake list + object responses); `ensure_bucket` idempotent (treats "already exists" as success); `_creds_present` true/false by env.
- `ingest`: with creds → calls `download_all` before building (monkeypatch `article_store.download_all` + `rag_core`); without creds → skips download, uses disk.
- `api.corpus_stats`: counts per `site` and total from a monkeypatched manifest, with `data/articles` absent.
- `upload_articles.main`: uploads each file best-effort; one failure doesn't abort.

## Rollout / sequencing (ordering is load-bearing)

1. **Build + unit-test** all of the above (mocked). Merge is safe *before* cutover because `ingest` still falls back to on-disk files when creds are absent and `data/articles` is still present locally.
2. **Backfill (before git removal):** run `scripts/backfill_articles.py` with the local `.env` creds → all 293 articles land in Storage; verify the Storage object count == local file count.
3. **Leave git:** `.gitignore` + `git rm -r --cached data/articles`, commit.
4. **Wire Render (go-live gate, user):** set `SUPABASE_URL` + `SUPABASE_SERVICE_KEY` in Render's build env. Until this is set, a Render build would download nothing → empty index; do not deploy the git-removal commit until the creds are set.
5. **Deploy + verify:** trigger a deploy → build log shows "downloaded N articles" → `/ask` returns a real cited answer; `/stats` shows the corpus count from the manifest.

## Hard dependencies on the user

- Confirm/allow the **`article-archive` bucket** (auto-created by the backfill via the service key; user only needs the Storage feature enabled on the Supabase project).
- **Set `SUPABASE_URL` + `SUPABASE_SERVICE_KEY` in Render's build environment** — the go-live gate.
- (I run the backfill locally using the existing `.env` creds and report the object count.)

## Open questions (defaults chosen; flag to change)

- **Bucket name:** `article-archive` (chosen). Trivial to change.
- **Object key namespacing:** flat `<basename>` (chosen; basenames are already unique `{site}__{slug}`). A `by-lab/` prefix is unnecessary at this scale.
- **Upload verification:** best-effort now (chosen); a verify-after-upload / reconcile pass is deferred (a future hardening if a silent upload miss ever bites).
