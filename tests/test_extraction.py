import pathlib
import scraper

def test_extract_article_pulls_title_date_body():
    html = pathlib.Path("tests/fixtures/sample_article.html").read_text()
    out = scraper.extract_article(html, "https://x.com/post")
    assert out["title"] == "Real Article Title"
    assert out["date"] == "2026-08-30"
    assert "First paragraph of real content." in out["body"]
    assert "Second paragraph" in out["body"]
    assert "menu junk" not in out["body"]
    assert "footer junk" not in out["body"]

def test_extract_article_empty_body_when_no_paragraphs():
    html = "<html><body><div>no paragraphs here</div></body></html>"
    out = scraper.extract_article(html, "https://x.com/p")
    assert out["body"] == ""

def test_extract_escalates_past_share_widget(tmp_path=None):
    # NVIDIA-style: <article> holds only a share widget; the real body is in <section>.
    html = (
        "<html><head><title>T</title></head><body>"
        "<article><h1>Title</h1><p>Share This Article</p><p>X</p>"
        "<p>Facebook</p><p>Copy link</p><p>October 20-22</p></article>"
        "<section><p>The real article body has plenty of actual sentences that "
        "describe what happened and why it matters to the reader.</p>"
        "<p>A second real paragraph continues the substantive content.</p></section>"
        "</body></html>"
    )
    out = scraper.extract_article(html, "https://blogs.nvidia.com/blog/x/")
    assert "real article body" in out["body"].lower()
    assert "Share This Article" not in out["body"]
    assert "Facebook" not in out["body"]

def test_looks_like_boilerplate_detects_cookie_consent():
    cookie = ("Required Cookies. These cookies enable core functionality and cannot be "
              "turned off. Performance Cookies measure visits.")
    assert scraper.looks_like_boilerplate(cookie) is True
    assert scraper.looks_like_boilerplate("A normal article about a new AI model release.") is False
