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
