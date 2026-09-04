# scraper.py  -- runs on ~/.venvs/scrapling/bin/python
import json
import os
from urllib.parse import urljoin


def filter_article_links(links, pattern, base_url):
    import re
    rx = re.compile(pattern)
    seen, out = set(), []
    for link in links:
        if not link:
            continue
        full = urljoin(base_url, link.split("#")[0])
        if rx.search(full) and full not in seen:
            seen.add(full)
            out.append(full)
    return out


def load_manifest(path):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_manifest(path, manifest):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)


def new_urls(candidates, manifest):
    return [u for u in candidates if u not in manifest]


def extract_article(html, url):
    from scrapling.parser import Selector
    sel = Selector(html)

    title = (sel.css("article h1::text").get()
             or sel.css("h1::text").get()
             or sel.css("title::text").get() or "").strip()

    date = (sel.css('meta[property="article:published_time"]::attr(content)').get()
            or sel.css("time::attr(datetime)").get() or "").strip()[:10]

    container = None
    for selector in ("article", "main", '[role="main"]'):
        node = sel.css(selector)
        if node:
            container = node
            break
    node = container if container else sel
    paras = [t.strip() for t in node.css("p::text").getall() if t and t.strip()]
    body = "\n\n".join(paras)
    return {"title": title, "date": date, "body": body}
