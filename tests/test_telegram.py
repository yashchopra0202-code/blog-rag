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
