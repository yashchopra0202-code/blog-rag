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
            .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))

def _clip_text(s, n):
    """Trim tag-free text to <= n chars without leaving a partial &entity;."""
    if n <= 0:
        return ""
    if len(s) <= n:
        return s
    cut = s[:n]
    amp = cut.rfind("&")
    if amp != -1 and ";" not in cut[amp:]:
        cut = cut[:amp]
    return cut

def _link_line(url, title, name):
    """One '• <a href=..>title</a> — name' line, fully escaped."""
    url = str(url or "")
    t = _esc(title or url or "source")
    link = f'<a href="{_esc(url)}">{t}</a>' if url.startswith("http") else t
    return "• " + (f"{_esc(name)}: " if name else "") + link

def format_answer(answer, sources):
    lines = [_link_line(s.get("url"), s.get("title"), s.get("label") or s.get("site"))
             for s in (sources or [])[:5]]
    suffix = ("\n\n<b>Sources</b>\n" + "\n".join(lines)) if lines else ""
    body = _clip_text(_esc(answer), MAX_LEN - len(suffix))
    return body + suffix

def format_latest(groups, limit=10):
    rows, n = [], 0
    for g in (groups or []):
        for it in g.get("items", []):
            if n >= limit:
                break
            rows.append(_link_line(it.get("url"), it.get("title"), it.get("label") or it.get("site")))
            n += 1
    if not rows:
        return "No recent posts in the last week. Ask me a question instead!"
    out = "<b>Latest from the labs</b>"
    for r in rows:
        if len(out) + len(r) + 1 > MAX_LEN:
            break
        out += "\n" + r
    return out

def format_digest_message(entries, feed_url, top=5):
    footer = f'\n\n<a href="{_esc(feed_url)}">Open the full feed →</a>' if feed_url else ""
    out = "<b>Fresh from the AI labs</b>"
    for e in (entries or [])[:top]:
        head = _link_line(e.get("url"), e.get("title"), e.get("label") or e.get("site"))
        nug = _esc(e.get("nugget") or "")
        block = head + (f"\n{nug}" if nug else "")
        if len(out) + len(block) + 2 + len(footer) > MAX_LEN:
            break
        out += "\n\n" + block
    return out + footer
