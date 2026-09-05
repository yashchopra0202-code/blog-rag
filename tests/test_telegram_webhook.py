import os
import api
from fastapi.testclient import TestClient

client = TestClient(api.app)

def _setup(monkeypatch, sent):
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "sec")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "TOK")
    monkeypatch.setattr(api.telegram_api, "send_message", lambda tok, cid, html: sent.append((cid, html)))

def test_webhook_rejects_bad_secret(monkeypatch):
    _setup(monkeypatch, [])
    r = client.post("/telegram/webhook", json={}, headers={"X-Telegram-Bot-Api-Secret-Token": "nope"})
    assert r.status_code == 401

def test_webhook_rejects_when_secret_unset(monkeypatch):
    monkeypatch.delenv("TELEGRAM_WEBHOOK_SECRET", raising=False)
    r = client.post("/telegram/webhook", json={}, headers={"X-Telegram-Bot-Api-Secret-Token": "anything"})
    assert r.status_code == 401

def test_webhook_start_subscribes_and_greets(monkeypatch):
    sent = []; subbed = []
    _setup(monkeypatch, sent)
    monkeypatch.setattr(api.store, "add_subscriber", lambda chat: subbed.append(chat["id"]))
    r = client.post("/telegram/webhook",
                    json={"message": {"text": "/start", "chat": {"id": 7, "first_name": "Y"}}},
                    headers={"X-Telegram-Bot-Api-Secret-Token": "sec"})
    assert r.status_code == 200 and subbed == [7]
    assert sent and sent[0][0] == 7

def test_webhook_question_answers(monkeypatch):
    sent = []
    _setup(monkeypatch, sent)
    monkeypatch.setattr(api, "rag_answer", lambda q: {"answer": "AoT", "sources": []})
    client.post("/telegram/webhook",
                json={"message": {"text": "what is new?", "chat": {"id": 3}}},
                headers={"X-Telegram-Bot-Api-Secret-Token": "sec"})
    assert sent and "AoT" in sent[0][1]

def test_webhook_returns_200_when_send_fails(monkeypatch):
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "sec")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "TOK")
    monkeypatch.setattr(api, "rag_answer", lambda q: {"answer": "x", "sources": []})
    def boom(*a, **k):
        raise RuntimeError("telegram down")
    monkeypatch.setattr(api.telegram_api, "send_message", boom)
    r = client.post("/telegram/webhook",
                    json={"message": {"text": "hi", "chat": {"id": 5}}},
                    headers={"X-Telegram-Bot-Api-Secret-Token": "sec"})
    assert r.status_code == 200
