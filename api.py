import glob
import hmac
import json
import os
import re
from collections import Counter
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from langchain_anthropic import ChatAnthropic

import rag_core
import telegram as tg
import telegram_api
import store
import emailer

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
    "xai": "xAI",
    "stability": "Stability AI",
    "ai2": "Allen AI (AI2)",
    "together": "Together AI",
    "perplexity": "Perplexity",
    "nvidia": "NVIDIA",
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


def _llm():
    return ChatAnthropic(model=MODEL, max_tokens=1024)


def rag_answer(question: str) -> dict:
    """Non-raising RAG core: returns {"answer","sources"} on success, or
    {"error","status"} when the index is missing. Reused by /ask and by the
    Telegram webhook, neither of which should have to catch HTTPException."""
    if not os.path.isdir(PERSIST_DIR):
        return {"error": "No index. Run ingest.py first.", "status": 503}
    vectordb = rag_core.load_index(PERSIST_DIR)
    retriever = rag_core.get_retriever(vectordb, k=4)
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


def answer_question(question: str) -> dict:
    """Raising wrapper over rag_answer, kept for /ask's existing external
    contract (400/503 via HTTPException) and for direct-call test coverage."""
    result = rag_answer(question)
    if "error" in result:
        raise HTTPException(status_code=result["status"], detail=result["error"])
    return result


@app.post("/ask")
def ask(payload: Ask):
    q = payload.question.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Question is empty.")
    return answer_question(q)


WELCOME = ("Hi{name}! I answer questions about what the AI labs are publishing. "
           "Send me any question, or /latest for recent posts. /stop to unsubscribe.")


@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    secret = os.getenv("TELEGRAM_WEBHOOK_SECRET")
    header = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    if not secret or not hmac.compare_digest(header, secret):
        raise HTTPException(status_code=401, detail="bad secret")
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    update = await request.json()
    intent = tg.parse_update(update)
    chat = intent.get("chat") or {}
    cid = chat.get("id")
    if cid is None:
        return {"ok": True}
    try:
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
    except Exception:
        print("telegram webhook: dispatch failed")
    return {"ok": True}


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
