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
