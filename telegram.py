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

def _esc(s):
    return (str(s if s is not None else "")
            .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def format_answer(answer, sources):
    body = _esc(answer)
    lines = []
    for s in (sources or [])[:5]:
        name = _esc(s.get("label") or s.get("site") or "")
        url = str(s.get("url") or "")
        title = _esc(s.get("title") or url or "source")
        link = f'<a href="{_esc(url)}">{title}</a>' if url.startswith("http") else title
        lines.append(f"• {link}" + (f" — {name}" if name else ""))
    out = body + ("\n\n<b>Sources</b>\n" + "\n".join(lines) if lines else "")
    return out[:MAX_LEN]

def format_latest(groups, limit=10):
    rows, n = [], 0
    for g in (groups or []):
        for it in g.get("items", []):
            if n >= limit:
                break
            url = str(it.get("url") or "")
            title = _esc(it.get("title") or url)
            name = _esc(it.get("label") or it.get("site") or "")
            link = f'<a href="{_esc(url)}">{title}</a>' if url.startswith("http") else title
            rows.append(f"• {link}" + (f" — {name}" if name else ""))
            n += 1
    if not rows:
        return "No recent posts in the last week. Ask me a question instead!"
    return ("<b>Latest from the labs</b>\n" + "\n".join(rows))[:MAX_LEN]

def format_digest_message(entries, feed_url, top=5):
    rows = []
    for e in (entries or [])[:top]:
        url = str(e.get("url") or "")
        title = _esc(e.get("title") or url)
        name = _esc(e.get("label") or e.get("site") or "")
        link = f'<a href="{_esc(url)}">{title}</a>' if url.startswith("http") else title
        head = f"• {link}" + (f" — {name}" if name else "")
        nug = _esc(e.get("nugget") or "")
        rows.append(head + (f"\n{nug}" if nug else ""))
    body = "<b>Fresh from the AI labs</b>\n\n" + "\n\n".join(rows)
    if feed_url:
        body += f'\n\n<a href="{_esc(feed_url)}">Open the full feed →</a>'
    return body[:MAX_LEN]
