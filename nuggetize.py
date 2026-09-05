from datetime import datetime, timezone

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

import article_format as af
import rag_core
from scraper import load_manifest, save_manifest, looks_like_boilerplate

MANIFEST_PATH = "data/manifest.json"
ARTICLES_DIR = "data/articles"
MODEL = "claude-haiku-4-5"
MAX_BODY_CHARS = 8000  # cap tokens/cost; the intro carries the gist
MIN_BODY_CHARS = 300   # below this the body is too thin to summarize — skip it
# Phrases that mean the model refused (thin/empty body) — never store these as a nugget.
_REFUSAL_MARKERS = ("unable to summarize", "don't see a blog post", "do not see a blog post",
                    "no blog post", "wasn't provided", "was not provided", "provide the full",
                    "paste the actual", "actual content of the article", "only the header",
                    "no actual content", "i don't have the")


def looks_like_refusal(nugget: str) -> bool:
    n = nugget.lower()
    return any(m in n for m in _REFUSAL_MARKERS)

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
            if len(body.strip()) < MIN_BODY_CHARS or looks_like_boilerplate(body):
                continue  # too thin / cookie-consent junk — leave un-nuggeted
            nugget = summarize_article(body, llm)
            if looks_like_refusal(nugget):
                print(f"  [warn] refusal-style summary, skipping {url}")
                continue  # don't store the model's "I can't summarize this" text
            entry["nugget"] = nugget
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
