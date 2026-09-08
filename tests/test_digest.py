from datetime import datetime, timezone

import digest
import store as _store  # for monkeypatching in these tests


# --- cadence controls (#4) --------------------------------------------------

def test_should_send_today_daily_always_sends():
    cfg = {"cadence": "daily", "weekly_day": "mon"}
    wed = datetime(2026, 9, 9, 13, 0, tzinfo=timezone.utc)  # a Wednesday
    assert digest.should_send_today(cfg, now=wed) is True


def test_should_send_today_weekly_only_on_configured_day():
    cfg = {"cadence": "weekly", "weekly_day": "mon"}
    mon = datetime(2026, 9, 7, 13, 0, tzinfo=timezone.utc)   # Monday
    tue = datetime(2026, 9, 8, 13, 0, tzinfo=timezone.utc)   # Tuesday
    assert digest.should_send_today(cfg, now=mon) is True
    assert digest.should_send_today(cfg, now=tue) is False


def test_should_send_today_force_overrides_weekly_off_day():
    cfg = {"cadence": "weekly", "weekly_day": "mon"}
    tue = datetime(2026, 9, 8, 13, 0, tzinfo=timezone.utc)   # not the send day
    assert digest.should_send_today(cfg, now=tue, force=True) is True


def test_effective_since_weekly_first_run_looks_back_seven_days():
    fixed_now = datetime(2026, 9, 8, 12, 0, 0, tzinfo=timezone.utc)
    since = digest.effective_since({}, now=fixed_now, cadence="weekly")
    assert since == "2026-09-01T12:00:00+00:00"   # 7 days, not 24h


def test_select_new_entries_filters_by_enabled_labs():
    manifest = {
        "u1": {"nugget": "a", "scraped_at": "2026-09-05T10:00:00+00:00", "title": "A", "site": "xai"},
        "u2": {"nugget": "b", "scraped_at": "2026-09-05T11:00:00+00:00", "title": "B", "site": "cohere"},
    }
    out = digest.select_new_entries(manifest, since=None, enabled_labs=["xai"])
    assert [e["url"] for e in out] == ["u1"]  # cohere excluded even though it has a nugget


def test_effective_since_uses_last_sent_when_present():
    state = {"last_sent": "2026-09-04T12:00:00+00:00"}
    assert digest.effective_since(state) == "2026-09-04T12:00:00+00:00"


def test_effective_since_falls_back_to_24h_ago_when_no_last_sent():
    fixed_now = datetime(2026, 9, 5, 12, 0, 0, tzinfo=timezone.utc)
    assert digest.effective_since({}, now=fixed_now) == "2026-09-04T12:00:00+00:00"


def test_select_excludes_no_nugget_and_old():
    manifest = {
        "u1": {"nugget": "a", "scraped_at": "2026-09-05T10:00:00+00:00", "title": "A", "site": "s"},
        "u2": {"scraped_at": "2026-09-05T11:00:00+00:00", "title": "B", "site": "s"},   # no nugget
        "u3": {"nugget": "c", "scraped_at": "2026-09-04T10:00:00+00:00", "title": "C", "site": "s"},  # old
    }
    out = digest.select_new_entries(manifest, since="2026-09-04T12:00:00+00:00")
    assert [e["url"] for e in out] == ["u1"]


def test_select_all_when_no_since():
    manifest = {"u1": {"nugget": "a", "scraped_at": "2026-09-05T10:00:00+00:00", "title": "A", "site": "s"}}
    assert len(digest.select_new_entries(manifest, since=None)) == 1


def test_select_caps_to_newest_limit():
    manifest = {
        "old": {"nugget": "o", "scraped_at": "2026-09-05T08:00:00+00:00", "title": "O", "site": "s"},
        "mid": {"nugget": "m", "scraped_at": "2026-09-05T09:00:00+00:00", "title": "M", "site": "s"},
        "new": {"nugget": "n", "scraped_at": "2026-09-05T10:00:00+00:00", "title": "N", "site": "s"},
    }
    out = digest.select_new_entries(manifest, since=None, limit=2)
    assert [e["url"] for e in out] == ["new", "mid"]  # newest first, capped to 2


def test_build_digest_escapes_and_includes():
    entries = [{"url": 'https://x/a?q="quoted"', "title": "Big <news>", "site": "lab",
                "nugget": "why & how", "scraped_at": "2026-09-05T10:00:00+00:00"}]
    subject, html = digest.build_digest(entries, feed_url="http://f/")
    assert "1 new" in subject
    assert "Big &lt;news&gt;" in html
    assert "why &amp; how" in html
    assert "https://x/a" in html
    assert "&quot;quoted&quot;" in html
    assert '"quoted"' not in html


def test_build_digest_top5_full_rest_grouped_by_topic():
    entries = [{"url": f"https://x/{i}", "title": f"Post {i}", "site": "nvidia",
                "nugget": f"nugget {i}", "topic": "Models", "signal": 4,
                "scraped_at": f"2026-09-05T{10+i:02d}:00:00+00:00"}
               for i in range(7)]
    subject, html = digest.build_digest(entries)
    assert "7 new" in subject
    assert html.count("Read the full post") == 5           # only 5 full cards
    assert "More by topic" in html and "Models" in html    # the rest grouped by topic
    assert "Post 6" in html and "Post 5" in html           # tail titles present as links
    assert "cid:banner" in html                            # banner image referenced


def test_curate_drops_low_signal_dedups_and_caps():
    def e(u, sig, title="T", site="mistral"):
        return {"url": u, "title": title, "site": site, "nugget": "n",
                "topic": "Models", "signal": sig, "scraped_at": "2026-09-05T10:00:00+00:00"}
    entries = [
        e("a", 5, "Big model release"),
        e("b", 2, "Routine PR"),                # dropped: low signal
        e("c", 4, "Big model release!!!"),      # dropped: dup title of 'a' (normalized)
        e("d", 4, "Infra post", "together"),
        e("f", 4, "Cap two", "together"),
        e("g", 4, "Cap three", "together"),
        e("h", 4, "Cap four", "together"),      # dropped: together already at cap 3
    ]
    urls = [x["url"] for x in digest.curate(entries, min_signal=3, per_lab_cap=3)]
    assert "b" not in urls and "c" not in urls
    assert [urls.count(x) for x in ("d", "f", "g")] == [1, 1, 1] and "h" not in urls


def test_banner_attachment_present_and_absent(tmp_path):
    assert digest.banner_attachment(str(tmp_path / "nope.gif")) is None
    p = tmp_path / "b.gif"
    p.write_bytes(b"GIF89a-fake-bytes")
    att = digest.banner_attachment(str(p))
    assert att and att[0]["content_id"] == "banner"
    assert att[0]["content_type"] == "image/gif"


def test_send_digest_posts_to_resend(monkeypatch):
    captured = {}

    class _Resp:
        def raise_for_status(self): pass
        def json(self): return {"id": "1"}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured.update(url=url, headers=headers, json=json)
        return _Resp()

    monkeypatch.setattr(digest.httpx, "post", fake_post)
    digest.send_digest("subj", "<b>h</b>", "key", "from@x", "to@y")
    assert captured["url"] == digest.RESEND_ENDPOINT
    assert captured["json"]["to"] == ["to@y"]
    assert captured["headers"]["Authorization"] == "Bearer key"


# --- broadcast and delivery (#5) ---------------------------------------------------

def test_broadcast_email_best_effort_and_footer(monkeypatch):
    calls = []
    def fake_send(to, subject, html, attachments=None, **k):
        if to == "boom@x.com":
            raise RuntimeError("bounce")
        calls.append((to, html))
    monkeypatch.setattr(digest.emailer, "send_email", fake_send)
    recipients = [
        {"email": "a@x.com", "unsub_url": "https://app/unsubscribe?token=A"},
        {"email": "boom@x.com", "unsub_url": "https://app/unsubscribe?token=B"},
        {"email": "c@x.com", "unsub_url": None},
    ]
    out = digest.broadcast_email("Subj", "<p>body</p>", recipients)
    assert out == {"sent": 2, "failed": 1}
    a_html = dict(calls)["a@x.com"]
    assert "unsubscribe?token=A" in a_html          # footer appended
    assert "unsubscribe" not in dict(calls)["c@x.com"].lower()  # no footer when no token


def test_deliver_if_new_skips_when_already_sent(monkeypatch):
    monkeypatch.setattr(digest.store, "digest_already_sent", lambda k: True)
    sent = {"n": 0}
    monkeypatch.setattr(digest, "broadcast_email",
                        lambda *a, **k: sent.__setitem__("n", sent["n"] + 1))
    out = digest.deliver_if_new("2026-09-08", "S", "<p>x</p>", [{"email": "a@x.com", "unsub_url": None}])
    assert out == {"skipped": True} and sent["n"] == 0


def test_deliver_if_new_sends_and_marks(monkeypatch):
    monkeypatch.setattr(digest.store, "digest_already_sent", lambda k: False)
    marked = {}
    monkeypatch.setattr(digest.store, "mark_digest_sent", lambda k: marked.update(k=k))
    monkeypatch.setattr(digest, "broadcast_email", lambda *a, **k: {"sent": 1, "failed": 0})
    out = digest.deliver_if_new("2026-09-08", "S", "<p>x</p>", [{"email": "a@x.com", "unsub_url": None}])
    assert out == {"sent": 1, "failed": 0} and marked["k"] == "2026-09-08"
