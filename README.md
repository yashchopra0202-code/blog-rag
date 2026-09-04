# blog-rag

RAG over recent AI-lab blog posts. Ask questions from a web page.

## Setup
1. `python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt`
2. `cp .env.example .env` and fill in `ANTHROPIC_API_KEY` and `VOYAGE_API_KEY`.
3. `scrapling` must be available at `~/.venvs/scrapling` (see the scrapling skill).

## Run (in order)
1. Scrape:  `~/.venvs/scrapling/bin/python scraper.py`   # writes data/articles/*.md (incremental)
2. Index:   `.venv/bin/python ingest.py`                 # builds chroma_db/
3. Serve:   `.venv/bin/uvicorn api:app` then open http://127.0.0.1:8000

Re-run the scraper any time to pick up new posts, then re-run ingest.

## Tests
- RAG venv:      `.venv/bin/python -m pytest tests/test_article_format.py tests/test_sites.py tests/test_rag_core.py tests/test_api.py`
- Scraper venv:  `~/.venvs/scrapling/bin/python -m pytest tests/test_scraper.py tests/test_extraction.py`

## Security
The `/ask` endpoint feeds raw scraped third-party article text to the LLM as context, so it implicitly trusts the content of the configured blogs. This is acceptable for a local personal tool over trusted lab sources, but it means you should only add sites you trust to `sites.py`.
