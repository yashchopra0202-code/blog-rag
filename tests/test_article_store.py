import article_store

class _Resp:
    def __init__(self, data=None, code=200, content=b""):
        self._d = data if data is not None else {}
        self.status_code = code
        self.content = content
    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"http {self.status_code}")
    def json(self): return self._d

def _env(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://proj.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_KEY", "svc-key")

def test_creds_present(monkeypatch):
    _env(monkeypatch)
    assert article_store._creds_present() is True
    monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)
    assert article_store._creds_present() is False

def test_upload_article_upserts_bytes(monkeypatch, tmp_path):
    _env(monkeypatch)
    f = tmp_path / "openai-index__hello.md"
    f.write_text("---\nurl: u\n---\nbody", encoding="utf-8")
    seen = {}
    def fake_post(url, headers=None, content=None, timeout=None):
        seen.update(url=url, headers=headers, content=content); return _Resp()
    monkeypatch.setattr(article_store.httpx, "post", fake_post)
    article_store.upload_article(str(f))
    assert seen["url"] == "https://proj.supabase.co/storage/v1/object/article-archive/openai-index__hello.md"
    assert seen["headers"]["x-upsert"] == "true"
    assert seen["headers"]["Authorization"] == "Bearer svc-key"
    assert seen["content"] == b"---\nurl: u\n---\nbody"

def test_ensure_bucket_idempotent(monkeypatch):
    _env(monkeypatch)
    monkeypatch.setattr(article_store.httpx, "post",
                        lambda url, headers=None, json=None, timeout=None: _Resp(code=409))
    article_store.ensure_bucket()   # must NOT raise on already-exists

def test_download_all_lists_then_gets(monkeypatch, tmp_path):
    _env(monkeypatch)
    pages = [[{"name": "a.md"}, {"name": "b.md"}], []]   # one full-ish page then empty
    def fake_post(url, headers=None, json=None, timeout=None):
        assert url.endswith("/object/list/article-archive")
        return _Resp(data=pages.pop(0))
    def fake_get(url, headers=None, timeout=None):
        return _Resp(content=("body of " + url.rsplit("/", 1)[1]).encode())
    monkeypatch.setattr(article_store.httpx, "post", fake_post)
    monkeypatch.setattr(article_store.httpx, "get", fake_get)
    n = article_store.download_all(str(tmp_path))
    assert n == 2
    assert (tmp_path / "a.md").read_text() == "body of a.md"
    assert (tmp_path / "b.md").read_text() == "body of b.md"
