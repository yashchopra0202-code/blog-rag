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
        if not data["body"]:
            print(f"  [warn] empty body, skipping {url}")
            continue
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        meta = {"url": url, "title": data["title"] or url, "site": site["name"],
                "date": data["date"], "scraped_at": now}
        path = af.write_article(articles_dir, meta, data["body"])
        manifest[url] = {"title": meta["title"], "date": meta["date"],
                         "site": site["name"], "file": path, "scraped_at": now}
        saved += 1
    return saved


def main():
    manifest = load_manifest(MANIFEST_PATH)
    total = 0
    for site in SITES:
        print(f"Scraping {site['name']} ...")
        try:
            n = scrape_site(site, manifest, ARTICLES_DIR, MAX_ARTICLES_PER_SITE)
            print(f"  +{n} new articles")
            total += n
        except Exception as e:  # noqa: BLE001 - isolate site failures
            print(f"  [error] {site['name']} failed: {e}")
        save_manifest(MANIFEST_PATH, manifest)  # checkpoint after each site
    print(f"Done. {total} new articles. Manifest has {len(manifest)} total.")


if __name__ == "__main__":
    main()
