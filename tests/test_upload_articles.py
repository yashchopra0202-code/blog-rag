import upload_articles

def test_upload_dir_best_effort(monkeypatch, tmp_path):
    (tmp_path / "a__x.md").write_text("A", encoding="utf-8")
    (tmp_path / "b__y.md").write_text("B", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("skip", encoding="utf-8")   # non-.md ignored
    monkeypatch.setattr(upload_articles.article_store, "ensure_bucket", lambda: None)
    uploaded = []
    def fake_upload(path):
        if path.endswith("b__y.md"):
            raise RuntimeError("storage down")   # one failure must not abort
        uploaded.append(path)
    monkeypatch.setattr(upload_articles.article_store, "upload_article", fake_upload)
    out = upload_articles.upload_dir(str(tmp_path))
    assert out == {"uploaded": 1, "failed": 1}
    assert any(p.endswith("a__x.md") for p in uploaded)
