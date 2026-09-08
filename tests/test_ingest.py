import ingest

def test_prepare_articles_downloads_when_creds(monkeypatch):
    monkeypatch.setattr(ingest.article_store, "_creds_present", lambda: True)
    called = {}
    monkeypatch.setattr(ingest.article_store, "download_all",
                        lambda dest: (called.__setitem__("dest", dest) or 5))
    n = ingest.prepare_articles("data/articles")
    assert n == 5 and called["dest"] == "data/articles"

def test_prepare_articles_skips_without_creds(monkeypatch):
    monkeypatch.setattr(ingest.article_store, "_creds_present", lambda: False)
    calls = {"n": 0}
    monkeypatch.setattr(ingest.article_store, "download_all",
                        lambda dest: calls.__setitem__("n", calls["n"] + 1))
    assert ingest.prepare_articles("data/articles") is None
    assert calls["n"] == 0   # did not hit Storage
