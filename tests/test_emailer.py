import emailer

class _Resp:
    def raise_for_status(self): pass
    def json(self): return {"id": "e1"}

def test_send_email_posts_to_resend(monkeypatch):
    seen = {}
    def fake_post(url, headers=None, json=None, timeout=None):
        seen.update(url=url, headers=headers, json=json); return _Resp()
    monkeypatch.setattr(emailer.httpx, "post", fake_post)
    out = emailer.send_email("to@x.com", "Subj", "<b>hi</b>", api_key="k", sender="from@x.com")
    assert out == {"id": "e1"}
    assert seen["url"] == emailer.RESEND_ENDPOINT
    assert seen["headers"]["Authorization"] == "Bearer k"
    assert seen["json"]["from"] == "from@x.com"
    assert seen["json"]["to"] == ["to@x.com"]
    assert seen["json"]["subject"] == "Subj"

def test_send_email_defaults_sender_and_key(monkeypatch):
    monkeypatch.setenv("RESEND_API_KEY", "envkey")
    monkeypatch.delenv("DIGEST_FROM", raising=False)
    seen = {}
    monkeypatch.setattr(emailer.httpx, "post",
                        lambda url, headers=None, json=None, timeout=None: (seen.update(headers=headers, json=json), _Resp())[1])
    emailer.send_email("a@b.com", "S", "<p>x</p>")
    assert seen["headers"]["Authorization"] == "Bearer envkey"
    assert seen["json"]["from"] == "onboarding@resend.dev"

def test_confirmation_html_contains_and_escapes_url():
    html = emailer.confirmation_html("https://app/confirm?token=abc&x=1")
    assert "https://app/confirm?token=abc&amp;x=1" in html   # & escaped
    assert "Confirm" in html

def test_unsubscribe_footer_contains_link():
    foot = emailer.unsubscribe_footer("https://app/unsubscribe?token=zzz")
    assert "https://app/unsubscribe?token=zzz" in foot
    assert "unsubscribe" in foot.lower()
