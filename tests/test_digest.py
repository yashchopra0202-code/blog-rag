from datetime import datetime, timezone

import digest


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


def test_build_digest_top5_full_rest_grouped():
    entries = [{"url": f"https://x/{i}", "title": f"Post {i}", "site": "nvidia",
                "nugget": f"nugget {i}", "scraped_at": f"2026-09-05T{10+i:02d}:00:00+00:00"}
               for i in range(7)]
    subject, html = digest.build_digest(entries)
    assert "7 new" in subject
    assert html.count("Read the full post") == 5           # only 5 full cards
    assert "More from the labs" in html                    # the rest are grouped
    assert "Post 1" in html and "Post 0" in html           # tail titles present as links
    assert "cid:banner" in html                            # banner image referenced


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
