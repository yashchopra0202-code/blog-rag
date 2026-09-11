import scraper

def test_filter_article_links_resolves_and_filters():
    links = ["/news/post-a", "https://www.anthropic.com/news/post-b",
             "/news", "/news/post-a", "https://other.com/x"]
    out = scraper.filter_article_links(
        links, r"anthropic\.com/news/.+", "https://www.anthropic.com/news")
    assert out == ["https://www.anthropic.com/news/post-a",
                   "https://www.anthropic.com/news/post-b"]

def test_manifest_roundtrip_and_new_urls(tmp_path):
    p = str(tmp_path / "manifest.json")
    assert scraper.load_manifest(p) == {}
    m = {"https://x/a": {"title": "A"}}
    scraper.save_manifest(p, m)
    assert scraper.load_manifest(p) == m
    assert scraper.new_urls(["https://x/a", "https://x/b"], m) == ["https://x/b"]

def test_write_scrape_status(tmp_path):
    import json
    p = str(tmp_path / "scrape_status.json")
    scraper.write_scrape_status(18, 17, 5, path=p)
    with open(p) as f:
        s = json.load(f)
    assert s == {"sites_total": 18, "sites_ok": 17, "new_articles": 5}

def test_scrape_site_stores_og_image_in_manifest(tmp_path, monkeypatch):
    html = ('<html><head><title>T</title>'
            '<meta property="og:image" content="https://x.com/hero.jpg"></head>'
            '<body><article><h1>Real Title</h1>'
            '<p>A genuine article paragraph with enough real content to be kept.</p>'
            '</article></body></html>')
    monkeypatch.setattr(scraper, "_discover", lambda site: ["https://x.com/post"])
    monkeypatch.setattr(scraper, "fetch_html", lambda url, render_js: html)
    monkeypatch.setattr(scraper, "REQUEST_DELAY_SEC", 0)
    manifest = {}
    saved = scraper.scrape_site({"name": "xai", "render_js": False},
                                manifest, str(tmp_path), max_articles=5)
    assert saved == 1
    assert manifest["https://x.com/post"]["image"] == "https://x.com/hero.jpg"
