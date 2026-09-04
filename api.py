import glob
import json
import os
from collections import Counter
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from langchain_anthropic import ChatAnthropic

import rag_core

load_dotenv()
PERSIST_DIR = "chroma_db"
ARTICLES_DIR = "data/articles"
MANIFEST_PATH = "data/manifest.json"
MODEL = "claude-haiku-4-5"
FEED_MAX_DAYS = 30

# Slug -> human label for the discovery UI. Keeps display names in one place.
SITE_LABELS = {
    "anthropic-research": "Anthropic · Research",
    "anthropic-engineering": "Anthropic · Engineering",
    "anthropic-news": "Anthropic · News",
    "openai-research": "OpenAI · Research",
    "openai-index": "OpenAI · Index",
    "google-research": "Google Research",
    "deepmind": "Google DeepMind",
    "meta-ai": "Meta AI",
    "huggingface": "Hugging Face",
    "microsoft-research": "Microsoft Research",
    "mistral": "Mistral",
    "cohere": "Cohere",
}
PROMPT_TMPL = (
    "Answer the question using ONLY the context below. "
    "If the answer is not in the context, say you don't know.\n\n"
    "Context:\n{context}\n\nQuestion: {question}"
)

def nice_title(title: str, url: str) -> str:
    """Fall back to a readable title derived from the URL slug when a site
    (e.g. Hugging Face) didn't expose a title the scraper could capture."""
    if title and not title.startswith("http"):
        return title
    slug = url.rstrip("/").split("/")[-1].split("?")[0]
    words = slug.replace("-", " ").replace("_", " ").strip()
    return (words[:1].upper() + words[1:]) if words else url


app = FastAPI(title="blog-rag")


class Ask(BaseModel):
    question: str


def _llm():
    return ChatAnthropic(model=MODEL, max_tokens=1024)


def answer_question(question: str) -> dict:
    if not os.path.isdir(PERSIST_DIR):
        raise HTTPException(status_code=503, detail="No index. Run ingest.py first.")
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
    return answer_question(q)


def corpus_stats() -> dict:
    """Counts + freshness for the discovery UI, read from disk (no index load)."""
    files = glob.glob(os.path.join(ARTICLES_DIR, "*.md"))
    counts = Counter(os.path.basename(f).split("__", 1)[0] for f in files)
    sites = [{"name": s, "label": SITE_LABELS.get(s, s), "count": n}
             for s, n in counts.most_common()]
    updated = ""
    try:
        with open(MANIFEST_PATH, encoding="utf-8") as f:
            manifest = json.load(f)
        dates = [v.get("scraped_at", "")[:10] for v in manifest.values()
                 if v.get("scraped_at")]
        updated = max(dates) if dates else ""
    except (OSError, ValueError):
        pass
    return {"articles": len(files), "sites": sites, "updated": updated}


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


@app.get("/stats")
def stats():
    return corpus_stats()


@app.get("/feed")
def feed(days: int = 7):
    return feed_data(days)


@app.get("/articles")
def articles(site: str, limit: int = 20):
    """Recent posts for one lab, newest first — a metadata listing, not a search.

    Manifest insertion order is scrape order, which is the listing (reverse-
    chronological) order, so we preserve it rather than re-sorting."""
    try:
        with open(MANIFEST_PATH, encoding="utf-8") as f:
            manifest = json.load(f)
    except (OSError, ValueError):
        manifest = {}
    items = [{"url": url, "title": nice_title(v.get("title", ""), url), "date": v.get("date", "")}
             for url, v in manifest.items() if v.get("site") == site]
    return {"site": site, "label": SITE_LABELS.get(site, site),
            "count": len(items), "articles": items[: max(1, min(limit, 100))]}


@app.get("/")
def index():
    # no-cache so an edited page is always served fresh on the next load.
    return FileResponse("static/index.html",
                        headers={"Cache-Control": "no-cache, must-revalidate"})
