import base64
import json
import os
from datetime import datetime, timedelta, timezone

import httpx
from dotenv import load_dotenv

import emailer
import store
from config import load_config
from scraper import load_manifest

_WEEKDAYS = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}

MANIFEST_PATH = "data/manifest.json"
STATE_PATH = "data/digest_state.json"
BANNER_PATH = "static/email-banner.gif"
RESEND_ENDPOINT = "https://api.resend.com/emails"
FULL_COUNT = 5  # how many nuggets get a full card; the rest are grouped links

# site slug -> (display label, accent color) for badges/links
LAB = {
    "anthropic-research": ("Anthropic · Research", "#C15F3C"),
    "anthropic-engineering": ("Anthropic · Engineering", "#C15F3C"),
    "anthropic-news": ("Anthropic · News", "#C15F3C"),
    "openai-research": ("OpenAI · Research", "#0A7A6B"),
    "openai-index": ("OpenAI", "#0A7A6B"),
    "google-research": ("Google Research", "#4285F4"),
    "deepmind": ("Google DeepMind", "#4285F4"),
    "meta-ai": ("Meta AI", "#0866FF"),
    "huggingface": ("Hugging Face", "#E38B00"),
    "microsoft-research": ("Microsoft Research", "#0067B8"),
    "mistral": ("Mistral", "#FA5111"),
    "cohere": ("Cohere", "#39594D"),
    "xai": ("xAI", "#111827"),
    "stability": ("Stability AI", "#7A3FF2"),
    "ai2": ("Allen AI (AI2)", "#E0439A"),
    "together": ("Together AI", "#1046E4"),
    "perplexity": ("Perplexity", "#20808D"),
    "nvidia": ("NVIDIA", "#5F9400"),
}


def lab_label(site):
    return LAB.get(site, (site.replace("-", " ").title(), "#556155"))[0]


def lab_color(site):
    return LAB.get(site, (site, "#556155"))[1]


def load_state(path=STATE_PATH):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_state(state, path=STATE_PATH):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def should_send_today(cfg, now=None, force=False):
    """Whether an email goes out on this run. Daily always sends; weekly sends
    only on the configured weekday. `force` (manual run) bypasses the gate."""
    if force or cfg.get("cadence", "daily") != "weekly":
        return True
    now = now or datetime.now(timezone.utc)
    return now.weekday() == _WEEKDAYS.get(cfg.get("weekly_day", "mon"), 0)


def select_new_entries(manifest, since, limit=None, enabled_labs=None):
    out = []
    for url, v in manifest.items():
        if not v.get("nugget"):
            continue
        if enabled_labs and v.get("site", "") not in enabled_labs:
            continue
        stamp = v.get("scraped_at", "")
        if since and stamp <= since:
            continue
        try:
            signal = int(v.get("signal", 3))
        except (TypeError, ValueError):
            signal = 3
        out.append({"url": url, "title": v.get("title", url), "site": v.get("site", ""),
                    "nugget": v["nugget"], "topic": v.get("topic", "Other"),
                    "signal": signal, "scraped_at": stamp})
    out.sort(key=lambda e: (e["signal"], e["scraped_at"]), reverse=True)  # signal, then recency
    if limit is not None:
        out = out[:limit]
    return out


def _title_key(title):
    import re
    return re.sub(r"[^a-z0-9]+", " ", str(title).lower()).strip()


def curate(entries, min_signal=3, per_lab_cap=3):
    """Drop low-signal items, de-duplicate near-identical titles, and cap how
    many any single lab contributes — so one lab's benchmark-post flood or a
    re-post can't dominate. Input is assumed sorted best-first."""
    seen, per_lab, out = set(), {}, []
    for e in entries:
        if e["signal"] < min_signal:
            continue
        key = _title_key(e["title"])
        if key in seen:
            continue
        if per_lab.get(e["site"], 0) >= per_lab_cap:
            continue
        seen.add(key)
        per_lab[e["site"]] = per_lab.get(e["site"], 0) + 1
        out.append(e)
    return out


def effective_since(state, now=None, cadence="daily"):
    """The lower-bound timestamp for a digest: the last-sent time, or a first-run
    fallback window (24h daily, 7 days weekly) when no digest has been sent yet."""
    last = state.get("last_sent")
    if last:
        return last
    now = now or datetime.now(timezone.utc)
    hours = 24 * 7 if cadence == "weekly" else 24
    return (now - timedelta(hours=hours)).isoformat(timespec="seconds")


def _esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _full_card(e):
    label, color = lab_label(e["site"]), lab_color(e["site"])
    return (
        '<div style="border:1px solid #E3E5DC;border-radius:14px;padding:16px 18px;'
        'margin:0 0 14px;background:#ffffff">'
        f'<span style="display:inline-block;background:{color};color:#ffffff;font-size:11px;'
        f'font-weight:700;padding:3px 10px;border-radius:999px;letter-spacing:.02em">{_esc(label)}</span>'
        '<div style="font-size:17px;font-weight:700;line-height:1.3;margin:10px 0 7px">'
        f'<a href="{_esc(e["url"])}" style="color:#15201A;text-decoration:none">{_esc(e["title"])}</a></div>'
        f'<div style="color:#57615A;font-size:14px;line-height:1.55">{_esc(e["nugget"])}</div>'
        f'<div style="margin-top:11px"><a href="{_esc(e["url"])}" style="color:{color};font-weight:600;'
        'font-size:13px;text-decoration:none">Read the full post &rarr;</a></div>'
        '</div>')


_TOPIC_ORDER = ("Models", "Research", "Safety & Policy", "Infrastructure",
                "Product & Tools", "Business", "Other")


def _more_section(rest):
    if not rest:
        return ""
    groups = {}
    for e in rest:
        groups.setdefault(e.get("topic", "Other"), []).append(e)
    blocks = []
    for topic in _TOPIC_ORDER:
        items = groups.get(topic)
        if not items:
            continue
        links = "".join(
            f'<div style="margin:5px 0"><a href="{_esc(i["url"])}" '
            'style="color:#15201A;text-decoration:none;font-size:14px">'
            f'<span style="color:{lab_color(i["site"])};font-weight:700">&rsaquo;</span> '
            f'{_esc(i["title"])} '
            f'<span style="color:#9AA39C;font-size:12px">&middot; {_esc(lab_label(i["site"]))}</span>'
            '</a></div>'
            for i in items)
        blocks.append(
            '<div style="margin:0 0 16px"><div style="font-size:12px;font-weight:700;'
            'color:#0A5F4E;text-transform:uppercase;letter-spacing:.05em;'
            f'margin-bottom:7px">{_esc(topic)}</div>{links}</div>')
    return (
        '<div style="margin-top:26px;padding-top:20px;border-top:1px solid #E3E5DC">'
        '<div style="font-size:15px;font-weight:700;color:#15201A;margin-bottom:14px">'
        'More by topic</div>' + "".join(blocks) + '</div>')


def build_digest(entries, feed_url="http://127.0.0.1:8000/"):
    day = datetime.now(timezone.utc).date().isoformat()
    subject = f"AI nuggets · {day} · {len(entries)} new"
    top, rest = entries[:FULL_COUNT], entries[FULL_COUNT:]
    # Banner: animated GIF (cid attachment) over a gradient fallback that shows
    # even when the client blocks images.
    banner = (
        '<div style="background:linear-gradient(135deg,#0E7C66 0%,#45C79E 100%);'
        'border-radius:16px;overflow:hidden;margin:0 0 22px;text-align:center">'
        '<img src="cid:banner" alt="Fresh from the AI labs" width="600" '
        'style="display:block;width:100%;max-width:600px;height:auto;border:0"></div>')
    cards = "".join(_full_card(e) for e in top)
    html = (
        '<div style="font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;'
        'max-width:600px;margin:0 auto;padding:8px;background:#F5F6F0">'
        + banner +
        f'<div style="font-size:19px;font-weight:800;color:#15201A;margin:0 0 4px">Fresh from the AI labs</div>'
        f'<div style="font-size:13px;color:#7C867E;margin:0 0 18px">{day} · {len(entries)} new nuggets</div>'
        + cards
        + _more_section(rest)
        + f'<div style="margin-top:24px;font-size:12px;color:#7C867E">Generated from '
          f'{len(entries)} recent posts across the AI labs · '
          f'<a href="{_esc(feed_url)}" style="color:#0A5F4E">open the feed &rarr;</a></div>'
        '</div>')
    return subject, html


def banner_attachment(path=BANNER_PATH):
    """Resend inline attachment for the animated banner, or None if absent."""
    try:
        with open(path, "rb") as f:
            content = base64.b64encode(f.read()).decode()
    except OSError:
        return None
    return [{"filename": "banner.gif", "content": content,
             "content_type": "image/gif", "content_id": "banner"}]


def send_digest(subject, html, api_key, sender, to, attachments=None):
    return emailer.send_email(to, subject, html, attachments=attachments,
                              api_key=api_key, sender=sender)


def broadcast_email(subject, html, recipients, banner=None):
    """Send `html` to each recipient, best-effort (one failure never aborts the
    rest). recipients: [{"email", "unsub_url"}]; unsub footer appended when set."""
    sent = failed = 0
    for r in recipients:
        body = html + (emailer.unsubscribe_footer(r["unsub_url"]) if r.get("unsub_url") else "")
        try:
            emailer.send_email(r["email"], subject, body, attachments=banner)
            sent += 1
        except Exception as e:  # noqa: BLE001 - best effort per recipient
            print(f"  [warn] digest send to {r.get('email')} failed: {e}")
            failed += 1
    return {"sent": sent, "failed": failed}


def deliver_if_new(key, subject, html, recipients, banner=None):
    """Idempotency guard: skip if this digest key was already sent; else send
    then record the key (durable, in Supabase — survives a CI retry)."""
    if store.digest_already_sent(key):
        print(f"Digest {key} already sent. Nothing sent.")
        return {"skipped": True}
    result = broadcast_email(subject, html, recipients, banner=banner)
    if result.get("sent", 0) > 0:
        store.mark_digest_sent(key)
    return result


def main() -> None:
    load_dotenv()
    api_key = os.getenv("RESEND_API_KEY")
    to = os.getenv("DIGEST_TO")
    sender = os.getenv("DIGEST_FROM", "onboarding@resend.dev")
    # `or` (not getenv default) so an empty/unset FEED_URL secret in CI falls
    # back to localhost instead of producing a broken empty link in the email.
    feed_url = os.getenv("FEED_URL") or "http://127.0.0.1:8000/"
    if not api_key or not to:
        raise SystemExit("Set RESEND_API_KEY and DIGEST_TO in .env")
    cfg = load_config()
    cadence = cfg.get("cadence", "daily")
    force = os.getenv("DIGEST_FORCE", "").lower() in ("1", "true", "yes")
    if not should_send_today(cfg, force=force):
        print(f"Cadence is {cadence}; today is not the send day. Nothing sent.")
        return
    # weekly mode widens the pool; daily uses DIGEST_LIMIT (top 5 full, rest grouped)
    limit = cfg["weekly_limit"] if cadence == "weekly" else int(os.getenv("DIGEST_LIMIT", "20"))
    manifest = load_manifest(MANIFEST_PATH)
    state = load_state()
    since = effective_since(state, cadence=cadence)
    # curate: drop low-signal, de-dup, cap per lab; already sorted best-first
    entries = curate(select_new_entries(manifest, since, enabled_labs=cfg.get("enabled_labs")))[:limit]
    if not entries:
        print("No new high-signal nuggets since last digest. Nothing sent.")
        return
    subject, html = build_digest(entries, feed_url=feed_url)
    base = os.getenv("PUBLIC_BASE_URL") or feed_url.rstrip("/")
    try:
        subs = store.confirmed_email_subscribers()
    except Exception:
        subs = []
    recipients = [{"email": s["email"],
                   "unsub_url": f'{base}/unsubscribe?token={s["unsub_token"]}'} for s in subs]
    if not recipients and to:   # owner fallback while there are no confirmed subscribers
        recipients = [{"email": to, "unsub_url": None}]
    if not recipients:
        print("No confirmed subscribers and no DIGEST_TO. Nothing sent.")
        return
    key = datetime.now(timezone.utc).date().isoformat()
    result = deliver_if_new(key, subject, html, recipients, banner=banner_attachment())
    if result.get("skipped"):
        return
    if result.get("sent", 0) > 0:
        state["last_sent"] = max(e["scraped_at"] for e in entries)
        save_state(state)
    print(f"Digest {key}: sent {result['sent']}, failed {result['failed']}.")


if __name__ == "__main__":
    main()
