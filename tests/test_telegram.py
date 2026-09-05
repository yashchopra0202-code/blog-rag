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
