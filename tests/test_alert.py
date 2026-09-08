import alert


def test_healthy_when_all_ok():
    status = {"sites_total": 18, "sites_ok": 18, "new_articles": 3}
    outcomes = {"scrape": "success", "nuggetize": "success", "digest": "success"}
    assert alert.check_health(status, outcomes) == []


def test_flags_all_sites_failed():
    status = {"sites_total": 18, "sites_ok": 0, "new_articles": 0}
    outcomes = {"scrape": "success", "nuggetize": "success", "digest": "success"}
    problems = alert.check_health(status, outcomes)
    assert any("all 18 sites" in p for p in problems)


def test_flags_step_failures():
    status = {"sites_total": 18, "sites_ok": 18, "new_articles": 1}
    outcomes = {"scrape": "success", "nuggetize": "failure", "digest": "failure"}
    problems = alert.check_health(status, outcomes)
    assert any("nuggetize" in p for p in problems)
    assert any("digest" in p for p in problems)


def test_flags_scrape_crash_when_no_status():
    problems = alert.check_health(None, {"scrape": "failure", "nuggetize": "success", "digest": "success"})
    assert any("scrape" in p for p in problems)


def test_healthy_when_no_status_but_scrape_succeeded():
    # status file may be absent for reasons other than a crash; only flag if scrape also failed
    assert alert.check_health(None, {"scrape": "success", "nuggetize": "success", "digest": "success"}) == []


def test_flags_telegram_failure():
    status = {"sites_total": 18, "sites_ok": 18, "new_articles": 1}
    outcomes = {"scrape": "success", "nuggetize": "success",
                "digest": "success", "telegram": "failure"}
    problems = alert.check_health(status, outcomes)
    assert any("telegram" in p for p in problems)


def test_send_alert_posts_to_resend(monkeypatch):
    captured = {}

    class _Resp:
        def raise_for_status(self): pass
        def json(self): return {"id": "1"}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured.update(url=url, headers=headers, json=json)
        return _Resp()

    monkeypatch.setattr(alert.httpx, "post", fake_post)
    alert.send_alert(["scraping failed on all 18 sites"], "key", "from@x", "to@y", "http://run/1")
    assert captured["url"] == alert.RESEND_ENDPOINT
    assert captured["json"]["to"] == ["to@y"]
    assert "attention" in captured["json"]["subject"].lower()
    assert "all 18 sites" in captured["json"]["html"]
    assert "http://run/1" in captured["json"]["html"]
