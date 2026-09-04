import os
import re


def slugify(text: str) -> str:
    text = (text or "").lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:80] or "untitled"


def article_filename(site: str, url: str) -> str:
    last = url.rstrip("/").split("/")[-1]
    return f"{site}__{slugify(last)}.md"


_KEYS = ("url", "title", "site", "date", "scraped_at")


def write_article(articles_dir: str, meta: dict, body: str) -> str:
    os.makedirs(articles_dir, exist_ok=True)
    path = os.path.join(articles_dir, article_filename(meta["site"], meta["url"]))
    lines = ["---"]
    for k in _KEYS:
        lines.append(f"{k}: {meta.get(k, '')}")
    lines.append("---")
    lines.append("")
    lines.append(body.strip())
    lines.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


def parse_article(path: str) -> tuple[dict, str]:
    with open(path, encoding="utf-8") as f:
        text = f.read()
    meta: dict = {}
    body = text
    if text.startswith("---"):
        _, header, body = text.split("---", 2)
        for line in header.strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    return meta, body.lstrip("\n")
