import article_format as af

def test_slugify_basic():
    assert af.slugify("Hello, World! 2026") == "hello-world-2026"

def test_slugify_empty_fallback():
    assert af.slugify("!!!") == "untitled"

def test_article_filename_from_url():
    name = af.article_filename("anthropic-news", "https://www.anthropic.com/news/some-post/")
    assert name == "anthropic-news__some-post.md"

def test_write_then_parse_roundtrip(tmp_path):
    meta = {"url": "https://x.com/a", "title": "A: B", "site": "s",
            "date": "2026-08-30", "scraped_at": "2026-09-04T00:00:00Z"}
    body = "Line one.\n\nLine two."
    path = af.write_article(str(tmp_path), meta, body)
    got_meta, got_body = af.parse_article(path)
    assert got_meta == meta
    assert got_body.strip() == body
