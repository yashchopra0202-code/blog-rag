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


def test_backfill_delegates_to_upload_dir(monkeypatch):
    import importlib.util, os
    spec = importlib.util.spec_from_file_location(
        "backfill_articles", os.path.join("scripts", "backfill_articles.py"))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    called = {}
    monkeypatch.setattr(mod.upload_articles, "upload_dir",
                        lambda d="data/articles": called.setdefault("d", d) or {"uploaded": 3, "failed": 0})
    monkeypatch.setattr(mod, "load_dotenv", lambda: None)
    mod.main()
    assert called["d"] == "data/articles"
