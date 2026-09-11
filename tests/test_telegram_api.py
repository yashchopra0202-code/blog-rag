import telegram_api


class _FakeResp:
    status_code = 200

    def raise_for_status(self):
        pass

    def json(self):
        return {"ok": True}


def test_send_photo_posts_to_sendphoto(monkeypatch):
    captured = {}
    monkeypatch.setattr(telegram_api.httpx, "post",
                        lambda url, json, timeout: captured.update(url=url, json=json) or _FakeResp())
    telegram_api.send_photo("TOK", 5, "https://img/x.jpg", "a caption")
    assert captured["url"].endswith("/botTOK/sendPhoto")
    assert captured["json"]["chat_id"] == 5
    assert captured["json"]["photo"] == "https://img/x.jpg"
    assert captured["json"]["caption"] == "a caption"
