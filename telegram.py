"""Pure Telegram helpers: parse incoming updates and format outgoing text.
No network or state — everything here is unit-testable with plain dicts."""

MAX_LEN = 4096  # Telegram hard limit on message text

def parse_update(update):
    msg = update.get("message") if isinstance(update, dict) else None
    if not isinstance(msg, dict):
        return {"kind": "ignore", "text": "", "chat": {}}
    text = (msg.get("text") or "").strip()
    c = msg.get("chat") or {}
    chat = {"id": c.get("id"), "first_name": c.get("first_name", ""), "username": c.get("username", "")}
    if not text:
        return {"kind": "ignore", "text": "", "chat": chat}
    if text.startswith("/"):
        cmd = text.split()[0].lstrip("/").split("@")[0].lower()
        if cmd in ("start", "stop", "latest"):
            return {"kind": cmd, "text": "", "chat": chat}
        return {"kind": "question", "text": text, "chat": chat}  # unknown command -> treat as text
    return {"kind": "question", "text": text, "chat": chat}
