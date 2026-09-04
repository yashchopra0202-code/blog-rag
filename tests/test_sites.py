import re
from sites import SITES

def test_sites_shape():
    assert len(SITES) >= 9
    names = [s["name"] for s in SITES]
    assert len(names) == len(set(names))  # unique
    for s in SITES:
        assert s["listing_urls"] and all(u.startswith("http") for u in s["listing_urls"])
        re.compile(s["article_url_pattern"])   # valid regex
        assert isinstance(s["render_js"], bool)

def test_patterns_match_expected_article_urls():
    by_name = {s["name"]: s for s in SITES}
    p = by_name["anthropic-news"]["article_url_pattern"]
    assert re.search(p, "https://www.anthropic.com/news/some-post")
    assert not re.search(p, "https://www.anthropic.com/news")
