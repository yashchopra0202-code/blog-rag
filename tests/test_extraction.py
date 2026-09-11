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

def test_extract_article_pulls_og_image():
    html = ('<html><head><title>T</title>'
            '<meta property="og:image" content="https://x.com/hero.jpg"></head>'
            '<body><article><h1>Title</h1>'
            '<p>A genuine article paragraph with enough real content to keep it.</p>'
            '</article></body></html>')
    out = scraper.extract_article(html, "https://x.com/post")
    assert out["image"] == "https://x.com/hero.jpg"

def test_extract_article_image_empty_when_absent():
    html = ('<html><head><title>T</title></head><body><article><h1>Title</h1>'
            '<p>A genuine article paragraph with enough real content to keep it.</p>'
            '</article></body></html>')
    out = scraper.extract_article(html, "https://x.com/post")
    assert out["image"] == ""

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

def test_extract_falls_back_to_full_text_when_body_is_not_in_p():
    # OpenAI/NVIDIA render the body in <div>/<span>, not <p>.
    html = (
        "<html><head><title>T</title></head><body>"
        "<article><h1>Headline</h1>"
        "<div>The body of this article lives in divs and spans, not p tags, so a "
        "p-only extractor would miss all of this real content about a new AI model "
        "and why it matters to developers building on it today.</div>"
        "<div>A second block of genuine article content continues here with detail.</div>"
        "</article></body></html>"
    )
    out = scraper.extract_article(html, "https://openai.com/index/x/")
    assert "lives in divs and spans" in out["body"]
    assert "second block of genuine" in out["body"]

def test_extract_strips_cookie_consent_then_recovers_body():
    # NVIDIA-style: a OneTrust cookie subtree full of <p> tags, real body in a <div>.
    html = (
        '<html><body>'
        '<div id="onetrust-consent-sdk"><p>These cookies are required and cannot be '
        'turned off.</p><p>Performance cookies measure visits to the website.</p></div>'
        '<main><h1>Title</h1><div>The genuine article body about a new chip lives here '
        'in a div with plenty of real sentences describing the announcement and why it '
        'matters to the industry.</div></main></body></html>'
    )
    out = scraper.extract_article(html, "https://blogs.nvidia.com/blog/x/")
    assert "genuine article body" in out["body"]
    assert "cookies" not in out["body"].lower()

def test_looks_like_boilerplate_detects_cookie_consent():
    cookie = ("Required Cookies. These cookies enable core functionality and cannot be "
              "turned off. Performance Cookies measure visits.")
    assert scraper.looks_like_boilerplate(cookie) is True
    assert scraper.looks_like_boilerplate("A normal article about a new AI model release.") is False
