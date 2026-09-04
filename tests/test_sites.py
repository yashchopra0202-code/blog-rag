import re
import api
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

def test_every_site_has_valid_pattern_and_label():
    for s in SITES:
        assert {"name", "listing_urls", "article_url_pattern", "render_js"} <= set(s)
        re.compile(s["article_url_pattern"])          # compiles
        assert s["name"] in api.SITE_LABELS           # has a display label
