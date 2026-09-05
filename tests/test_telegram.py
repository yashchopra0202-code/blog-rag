import telegram

def _msg(text):
    return {"message": {"text": text, "chat": {"id": 7, "first_name": "Yash", "username": "yc"}}}

def test_parse_start_command():
    out = telegram.parse_update(_msg("/start"))
    assert out["kind"] == "start"
    assert out["chat"]["id"] == 7 and out["chat"]["first_name"] == "Yash"

def test_parse_start_with_bot_suffix():
    assert telegram.parse_update(_msg("/start@FrontierLabsBot"))["kind"] == "start"

def test_parse_stop_and_latest():
    assert telegram.parse_update(_msg("/stop"))["kind"] == "stop"
    assert telegram.parse_update(_msg("/latest"))["kind"] == "latest"

def test_parse_freetext_is_question():
    out = telegram.parse_update(_msg("What is new in open models?"))
    assert out["kind"] == "question"
    assert out["text"] == "What is new in open models?"

def test_parse_non_message_update_is_ignore():
    assert telegram.parse_update({"edited_message": {}})["kind"] == "ignore"
    assert telegram.parse_update({"message": {"chat": {"id": 1}}})["kind"] == "ignore"  # no text

def test_format_answer_escapes_and_links():
    out = telegram.format_answer("A <b>bold</b> & tricky answer", [
        {"title": "Post <1>", "url": "https://x/a", "label": "Anthropic · News"},
    ])
    assert "&lt;b&gt;" in out and "&amp;" in out          # body escaped
    assert '<a href="https://x/a">Post &lt;1&gt;</a>' in out  # link title escaped
    assert "Anthropic · News" in out

def test_format_answer_truncates_to_limit():
    out = telegram.format_answer("x" * 6000, [])
    assert len(out) <= telegram.MAX_LEN

def test_format_answer_caps_sources_at_five():
    srcs = [{"title": f"T{i}", "url": f"https://x/{i}", "site": "s"} for i in range(9)]
    out = telegram.format_answer("ans", srcs)
    assert out.count("<a href=") == 5

def test_format_latest_lists_links():
    groups = [{"date": "2026-09-06", "items": [
        {"title": "Big model", "url": "https://x/a", "label": "Mistral", "site": "mistral", "nugget": "n"},
        {"title": "New agent", "url": "https://x/b", "label": "xAI", "site": "xai", "nugget": "n"},
    ]}]
    out = telegram.format_latest(groups)
    assert '<a href="https://x/a">Big model</a>' in out and "Mistral" in out
    assert '<a href="https://x/b">New agent</a>' in out

def test_format_latest_empty():
    assert "no recent" in telegram.format_latest([]).lower()

def test_format_latest_respects_limit():
    items = [{"title": f"P{i}", "url": f"https://x/{i}", "label": "L", "site": "s", "nugget": "n"} for i in range(20)]
    out = telegram.format_latest([{"date": "2026-09-06", "items": items}], limit=5)
    assert out.count("<a href=") == 5

def test_format_digest_message_has_links_and_feed():
    entries = [{"title": "A big release", "url": "https://x/a", "site": "mistral", "nugget": "It ships."},
               {"title": "New research", "url": "https://x/b", "site": "deepmind", "nugget": "Findings."}]
    out = telegram.format_digest_message(entries, "https://feed/", top=5)
    assert '<a href="https://x/a">A big release</a>' in out
    assert "https://feed/" in out

def test_format_digest_message_caps_top():
    entries = [{"title": f"T{i}", "url": f"https://x/{i}", "site": "s", "nugget": "n"} for i in range(10)]
    out = telegram.format_digest_message(entries, "https://feed/", top=3)
    assert out.count("<a href=\"https://x/") == 3

def test_format_answer_escapes_quote_in_title():
    out = telegram.format_answer("a", [{"title": 'He said "hi"', "url": "https://x/a", "site": "s"}])
    assert "&quot;" in out

def test_format_answer_long_body_keeps_sources_tag_intact():
    out = telegram.format_answer("x" * 5000, [{"title": "T", "url": "https://x/a", "label": "Lab"}])
    assert len(out) <= telegram.MAX_LEN
    assert out.count("<a ") == out.count("</a>")  # no anchor tag left unclosed by truncation

def test_format_digest_message_truncates_safely():
    entries = [{"title": "T" + str(i), "url": f"https://x/{i}", "site": "s", "nugget": "y" * 900} for i in range(6)]
    out = telegram.format_digest_message(entries, "https://feed/", top=6)
    assert len(out) <= telegram.MAX_LEN
    assert '<a href="https://feed/"' in out

def test_format_answer_stays_within_limit_with_long_sources():
    srcs = [{"title": "T" * 1200, "url": "https://x/" + "a" * 1200, "label": "L"} for _ in range(5)]
    out = telegram.format_answer("short answer", srcs)
    assert len(out) <= telegram.MAX_LEN
    assert out.count("<a ") == out.count("</a>")
