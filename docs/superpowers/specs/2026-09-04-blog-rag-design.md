# blog-rag — Design Spec

**Date:** 2026-09-04
**Status:** Approved (brainstorming), pending implementation plan

## Goal

Scrape recent posts from a fixed set of AI-lab research/engineering blogs, save
them locally, and answer questions over them through a web page (not the
terminal). The retrieval-augmented-generation (RAG) back half reuses the proven
`~/rag-agent` pipeline (chunk → embed → vector DB → LLM). The genuinely new work
is the scraper and a small question-answering web front-end.

## Scope decisions (settled during brainstorming)

- **Crawl depth:** full articles — follow links from each listing page and
  extract the full article body (not just listing summaries).
- **History depth:** recent N posts per site (default ~25), not the full
  back-catalog.
- **Project home:** new folder `~/blog-rag`, reusing `rag-agent`'s pipeline
  pattern. `rag-agent` is left untouched.
- **Refresh model:** incremental — a manifest tracks scraped URLs so re-runs
  only fetch new posts.
- **Backend for the page:** Python FastAPI serving a single HTML page. This is a
  deliberate, user-approved divergence from the default Next.js/Supabase/Vercel
  stack, chosen because the RAG core is Python and Chroma runs embedded (a local
  personal tool, not a deployed app).
- **Scraper architecture:** Approach A — a shared generic article extractor plus
  a tiny per-site config. Variance across sites lives almost entirely in *link
  discovery* on listing pages, not in article-body structure, so per-site effort
  is confined to a small config entry.

## Target sites

| Site | Listing URL(s) |
|------|----------------|
| Anthropic | anthropic.com/research, anthropic.com/engineering, anthropic.com/news |
| OpenAI | openai.com/research/index/, openai.com/index/ |
| Google Research | research.google/blog/ |
| DeepMind | deepmind.google/discover/blog/ |
| Meta AI | ai.meta.com/blog/ |
| Hugging Face | huggingface.co/blog |
| Microsoft Research | microsoft.com/en-us/research/blog/ |
| Mistral | mistral.ai/news/ |
| Cohere | cohere.com/blog |

Sites vary in transport: static HTML (Hugging Face, Cohere), JS-rendered SPAs
(OpenAI, DeepMind, Google Research), and some behind bot protection. The
`scrapling` library handles all three behind one fetch interface (static, dynamic
JS rendering, stealth).

## Project layout

```
blog-rag/
  .env  /  .env.example        # ANTHROPIC_API_KEY, VOYAGE_API_KEY
  .gitignore
  requirements.txt
  sites.py            # per-site config (the only place sites differ)
  scraper.py          # listing -> discover article links -> fetch -> extract -> save
  rag_core.py         # lifted from rag-agent, extended for article metadata
  ingest.py           # build Chroma index from data/articles/
  api.py              # FastAPI: POST /ask + serves the page
  static/index.html   # impeccable-designed question page
  data/
    articles/*.md     # one file per post (metadata header + body)
    manifest.json     # incremental tracking (url -> hash, date, file)
  chroma_db/          # persisted vector index
  tests/
```

## Components

Each unit has one purpose and a defined interface.

### `sites.py`
A list of config entries. Per site:
- `name` — stable slug (e.g. `anthropic-news`), used in filenames and citations.
- `listing_urls` — one or more index pages to start from.
- `article_url_pattern` — regex deciding whether a discovered link is an article.
- `render_js` — whether the listing page needs a real browser to reveal links.

This is the entire per-site surface. Adding a site = one entry. A site redesign
usually means editing only its `article_url_pattern`.

### `scraper.py`
For each site:
1. Fetch each listing URL (via `scrapling`, using JS rendering / stealth when
   `render_js` or bot protection requires it).
2. Collect all `<a href>`, keep links matching `article_url_pattern`, dedupe,
   take the most recent N.
3. Skip URLs already in `manifest.json`.
4. For each remaining URL: fetch the article, run the **shared generic
   extractor** (title, publish date if present, main body text with nav/footer
   boilerplate removed), save as `data/articles/<site>__<slug>.md`, and record it
   in the manifest.

The extractor is written once and shared across all sites. Per-site try/except:
one failing site logs a warning and the run continues. Timeouts + limited
retries; a small delay and a real User-Agent between requests.

Saved article file format (`.md`):
```
---
url: https://...
title: ...
site: anthropic-news
date: 2026-08-30
scraped_at: 2026-09-04T15:00:00Z
---

<article body text>
```

### `rag_core.py`
Lifted from `rag-agent` (`get_embeddings`, `chunk_documents`, `reset_index_dir`,
`build_index`, `load_index`, `get_retriever`, `format_docs`, `require_env`).
`EMBED_MODEL = "voyage-3.5"`. Chunk defaults 500 / 50 overlap.

Added: `load_articles(dir)` reads the `.md` files, parses the metadata header,
and returns LangChain `Document`s whose `metadata` carries `{source(url), title,
site, date}` — so retrieval can cite real source URLs on the page.

### `ingest.py`
Reads `data/articles/`, chunks, embeds with Voyage, rebuilds `chroma_db/`
(reset + build). Prints a summary (articles, chunks). Full rebuild is deliberate:
cheap at this scale and avoids stale/duplicate-chunk bugs. Incrementalism lives
in the *scrape* stage (network), not the *embed* stage.

### `api.py` (FastAPI)
- `POST /ask` with `{question}` → retrieve k=4, call `claude-haiku-4-5`
  (`max_tokens=1024`), return `{answer, sources: [{title, url, site}]}` where
  sources come from the retrieved chunks' metadata (deduped by url).
- `GET /` → serve `static/index.html`.
- Answers grounded strictly in retrieved context; when the context lacks the
  answer, the model says it doesn't know (same prompt discipline as rag-agent).

### `static/index.html`
Single page, vanilla HTML/CSS/JS, no build step, served by FastAPI. Question
input, answer display, clickable source citations, loading + error states.
Visual design produced with the `impeccable` skill.

## Data flow

```
scraper.py -> data/articles/*.md + manifest.json   (network stage, incremental)
ingest.py  -> chroma_db/                            (embed stage, full rebuild)
api.py     -> browser page  <-- user asks questions (query stage)
```

Run order: `python scraper.py` → `python ingest.py` → `uvicorn api:app`. The
three stages are decoupled so any one can run without the others.

## Error handling

- **Scraper:** per-site isolation (warn + continue); request timeouts + limited
  retries; graceful handling of a listing page that yields zero article links
  (warn, skip site).
- **API:** no index on disk → 503 with "run ingest first"; empty question → 400;
  model/network failure → clean JSON error, page shows a friendly message.
- **Config:** missing `ANTHROPIC_API_KEY` / `VOYAGE_API_KEY` → fail fast via
  `require_env`.

## Testing

- **Unit (no network, deterministic):** article-link filtering against
  `article_url_pattern`; manifest add/skip logic; `.md` metadata parse + write
  round-trip; chunking.
- **Extraction:** run the generic extractor against saved HTML fixtures (mocked
  fetch) — fast and stable, no live requests in tests.
- **API:** `POST /ask` with a mocked chain returns the expected answer + sources
  shape; error paths (no index, empty question).
- Same pytest layout/style as `rag-agent` (`tests/`, `conftest.py`).

## Dependencies

Reuse of rag-agent stack plus scraper + web layer:
`langchain`, `langchain-community`, `langchain-text-splitters`,
`langchain-voyageai`, `langchain-chroma`, `langchain-anthropic`, `chromadb`,
`python-dotenv`, `scrapling`, `fastapi`, `uvicorn`. No database beyond local
Chroma; no Supabase/Vercel for this local tool.

## Politeness / terms

Public blogs scraped for personal/research use. Keep the footprint light:
recent-N only, real User-Agent, inter-request delay, incremental re-runs. Respect
each site's terms of service.

## Out of scope (YAGNI)

- Full back-catalog crawling / pagination beyond recent N.
- Incremental / patched vector indexing (full rebuild instead).
- Auth, multi-user, deployment to Vercel, persistent chat history.
- Scheduled/automated re-scraping (run manually for now).
