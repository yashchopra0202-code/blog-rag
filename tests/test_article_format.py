import article_format as af
import pytest

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

def test_write_article_sanitizes_newlines_in_metadata(tmp_path):
    """Test that metadata values with newlines are collapsed to single spaces."""
    meta = {"url": "https://x.com/a", "title": "Line A\nLine B", "site": "s",
            "date": "2026-08-30", "scraped_at": "2026-09-04T00:00:00Z"}
    body = "Body text."
    path = af.write_article(str(tmp_path), meta, body)
    got_meta, got_body = af.parse_article(path)
    # Title should have newline collapsed to single space
    assert got_meta["title"] == "Line A Line B"
    # Round-trip should be parseable
    assert got_meta["url"] == meta["url"]
    assert got_meta["site"] == meta["site"]
    assert got_body.strip() == body

def test_write_article_sanitizes_dashes_in_metadata(tmp_path):
    """Test that a run of 3+ dashes in a metadata value can't corrupt frontmatter."""
    meta = {"url": "https://x.com/a", "title": "Foo --- Bar", "site": "s",
            "date": "2026-08-30", "scraped_at": "2026-09-04T00:00:00Z"}
    body = "Line one.\n\nLine two."
    path = af.write_article(str(tmp_path), meta, body)
    got_meta, got_body = af.parse_article(path)
    # Body must round-trip exactly, with no header remnants leaked into it
    assert got_body.strip() == body
    # Title must no longer contain a run of 3+ dashes
    assert "---" not in got_meta["title"]

def test_write_article_raises_on_missing_url(tmp_path):
    """Test that write_article raises ValueError when 'url' is missing."""
    meta = {"title": "Test", "site": "s", "date": "2026-08-30", "scraped_at": "2026-09-04T00:00:00Z"}
    body = "Body text."
    with pytest.raises(ValueError, match="url"):
        af.write_article(str(tmp_path), meta, body)

def test_write_article_raises_on_missing_site(tmp_path):
    """Test that write_article raises ValueError when 'site' is missing."""
    meta = {"url": "https://x.com/a", "title": "Test", "date": "2026-08-30", "scraped_at": "2026-09-04T00:00:00Z"}
    body = "Body text."
    with pytest.raises(ValueError, match="site"):
        af.write_article(str(tmp_path), meta, body)
