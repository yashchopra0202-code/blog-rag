from types import SimpleNamespace
import fastapi
import pytest
from fastapi.testclient import TestClient
import api

class _FakeDoc:
    def __init__(self, text, meta): self.page_content = text; self.metadata = meta

def test_answer_question_returns_answer_and_dedup_sources(monkeypatch):
    docs = [
        _FakeDoc("ctx one", {"source": "https://x/a", "title": "A", "site": "s"}),
        _FakeDoc("ctx two", {"source": "https://x/a", "title": "A", "site": "s"}),
        _FakeDoc("ctx three", {"source": "https://x/b", "title": "B", "site": "s"}),
    ]
    monkeypatch.setattr(api.os.path, "isdir", lambda p: True)
    monkeypatch.setattr(api.rag_core, "load_index", lambda p: object())
    monkeypatch.setattr(api.rag_core, "get_retriever",
                        lambda store, k=4: SimpleNamespace(invoke=lambda q: docs))
    monkeypatch.setattr(api, "_llm",
                        lambda: SimpleNamespace(invoke=lambda prompt: SimpleNamespace(content="ANSWER")))
    out = api.answer_question("q?")
    assert out["answer"] == "ANSWER"
    assert out["sources"] == [
        {"title": "A", "url": "https://x/a", "site": "s"},
        {"title": "B", "url": "https://x/b", "site": "s"},
    ]

def test_ask_endpoint(monkeypatch):
    monkeypatch.setattr(api, "answer_question", lambda q: {"answer": "OK", "sources": []})
    client = TestClient(api.app)
    r = client.post("/ask", json={"question": "hi"})
    assert r.status_code == 200
    assert r.json()["answer"] == "OK"

def test_ask_endpoint_rejects_empty():
    client = TestClient(api.app)
    r = client.post("/ask", json={"question": "  "})
    assert r.status_code == 400

def test_answer_question_no_index_503(monkeypatch):
    monkeypatch.setattr(api.os.path, "isdir", lambda p: False)
    with pytest.raises(fastapi.HTTPException) as ei:
        api.answer_question("q?")
    assert ei.value.status_code == 503
