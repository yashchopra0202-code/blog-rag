# scraper.py  -- runs on ~/.venvs/scrapling/bin/python
import json
import os
import time
from datetime import datetime, timezone
from urllib.parse import urljoin

import article_format as af
from sites import SITES

ARTICLES_DIR = "data/articles"
MANIFEST_PATH = "data/manifest.json"
MAX_ARTICLES_PER_SITE = 25
REQUEST_DELAY_SEC = 1.5


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


# Share-widget / social boilerplate that some sites (e.g. NVIDIA) wrap inside
# <article>, which otherwise fools a naive "first container" extractor.
BOILERPLATE = {"share this article", "share", "x", "twitter", "facebook", "linkedin",
               "copy link", "email", "reddit", "whatsapp", "print"}
# If a semantic container yields at least this much *non-boilerplate* text it is
# the real body; NVIDIA's <article> collapses to ~13 chars once the share widget
# is filtered, which triggers escalation to <section>/<body>.
MIN_ARTICLE_CHARS = 40


def _paragraphs(node):
    """Non-boilerplate paragraph texts from a container node."""
    out = []
    for t in node.css("p::text").getall():
        t = (t or "").strip()
        if len(t) > 1 and t.lower() not in BOILERPLATE:
            out.append(t)
    return out


# Cookie/consent text some sites (e.g. NVIDIA) render as the only readable <p>
# content when the real article body is JS-rendered elsewhere. Treat a body
# dominated by these as junk — better no article than a "summary about cookies".
_JUNK_BODY_MARKERS = ("these cookies", "required cookies", "performance cookies",
                      "personalization cookies", "advertising cookies", "cookie policy",
                      "accept all cookies", "enable core functionality", "cannot be turned off")


def looks_like_boilerplate(text: str) -> bool:
    t = (text or "").lower()
    return sum(m in t for m in _JUNK_BODY_MARKERS) >= 2


def extract_article(html, url):
    from scrapling.parser import Selector
    sel = Selector(html)

    title = (sel.css("article h1::text").get()
             or sel.css("h1::text").get()
             or sel.css("title::text").get() or "").strip()

    date = (sel.css('meta[property="article:published_time"]::attr(content)').get()
            or sel.css("time::attr(datetime)").get() or "").strip()[:10]

    # Prefer the first semantic container that clearly holds the article body.
    # Some sites wrap only a share widget in <article>/<main>, so if the chosen
    # container is too thin, escalate to <section>/<body> and keep the richest.
    best, best_len = [], 0
    for selector in ("article", "main", '[role="main"]', "section", "body"):
        node = sel.css(selector)
        if not node:
            continue
        paras = _paragraphs(node)
        total = sum(len(p) for p in paras)
        if total >= MIN_ARTICLE_CHARS:
            best = paras
            break
        if total > best_len:
            best_len, best = total, paras
    body = "\n\n".join(best)
    # Fallback: some sites (OpenAI, NVIDIA) render the body in <div>/<span>, not
    # <p>, so <p>-extraction comes out thin. Use the richest semantic container's
    # full descendant text instead. Downstream thin/boilerplate guards still
    # decide whether the result is usable, so a cookie-only page stays skipped.
    if len(body) < MIN_ARTICLE_CHARS:
        for selector in ("article", "main", '[role="main"]'):
            node = sel.css(selector)
            if not node:
                continue
            full = " ".join(t.strip() for t in node.css("::text").getall() if t and t.strip())
            if len(full) > len(body):
                body = full
    return {"title": title, "date": date, "body": body}


def fetch_html(url, render_js):
    from scrapling.fetchers import Fetcher, DynamicFetcher
    if not render_js:
        try:
            page = Fetcher.get(url, stealthy_headers=True, timeout=30)
            if page.status == 200 and page.css("a::attr(href)").getall():
                return page.html_content
        except Exception as e:  # noqa: BLE001
            print(f"  [warn] plain fetch failed for {url}: {e}")
    try:
        page = DynamicFetcher.fetch(url, headless=True)
        return page.html_content
    except Exception as e:  # noqa: BLE001
        print(f"  [warn] dynamic fetch failed for {url}: {e}")
        return None


def _discover(site):
    from scrapling.parser import Selector
    found = []
    for listing in site["listing_urls"]:
        html = fetch_html(listing, site["render_js"])
        time.sleep(REQUEST_DELAY_SEC)
        if not html:
            continue
        links = Selector(html).css("a::attr(href)").getall()
        found += filter_article_links(links, site["article_url_pattern"], listing)
    # dedupe preserving order
    seen, uniq = set(), []
    for u in found:
        if u not in seen:
            seen.add(u); uniq.append(u)
    return uniq


def scrape_site(site, manifest, articles_dir, max_articles):
    # Listings are assumed reverse-chronological, so the first max_articles
    # are the newest posts (recent-N by design).
    candidates = _discover(site)[:max_articles]
    todo = new_urls(candidates, manifest)
    saved = 0
    for url in todo:
        html = fetch_html(url, site["render_js"])
        time.sleep(REQUEST_DELAY_SEC)
        if not html:
            continue
        data = extract_article(html, url)
        if not data["body"] or looks_like_boilerplate(data["body"]):
            print(f"  [warn] empty/boilerplate body, skipping {url}")
            continue
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        meta = {"url": url, "title": data["title"] or url, "site": site["name"],
                "date": data["date"], "scraped_at": now}
        path = af.write_article(articles_dir, meta, data["body"])
        manifest[url] = {"title": meta["title"], "date": meta["date"],
                         "site": site["name"], "file": path, "scraped_at": now}
        saved += 1
    return saved


SCRAPE_STATUS_PATH = "data/scrape_status.json"


def write_scrape_status(sites_total, sites_ok, new_articles, path=SCRAPE_STATUS_PATH):
    """Machine-readable run health for the workflow's alert step."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"sites_total": sites_total, "sites_ok": sites_ok,
                   "new_articles": new_articles}, f, indent=2)


def main():
    manifest = load_manifest(MANIFEST_PATH)
    total = 0
    sites_ok = 0
    for site in SITES:
        print(f"Scraping {site['name']} ...")
        try:
            n = scrape_site(site, manifest, ARTICLES_DIR, MAX_ARTICLES_PER_SITE)
            print(f"  +{n} new articles")
            total += n
            sites_ok += 1
        except Exception as e:  # noqa: BLE001 - isolate site failures
            print(f"  [error] {site['name']} failed: {e}")
        save_manifest(MANIFEST_PATH, manifest)  # checkpoint after each site
    print(f"Done. {total} new articles. Manifest has {len(manifest)} total.")
    write_scrape_status(len(SITES), sites_ok, total)


if __name__ == "__main__":
    main()
