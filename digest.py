import json
import os
from datetime import datetime, timezone

import httpx
from dotenv import load_dotenv

from scraper import load_manifest

MANIFEST_PATH = "data/manifest.json"
STATE_PATH = "data/digest_state.json"
RESEND_ENDPOINT = "https://api.resend.com/emails"


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


def select_new_entries(manifest, since):
    out = []
    for url, v in manifest.items():
        if not v.get("nugget"):
            continue
        stamp = v.get("scraped_at", "")
        if since and stamp <= since:
            continue
        out.append({"url": url, "title": v.get("title", url), "site": v.get("site", ""),
                    "nugget": v["nugget"], "scraped_at": stamp})
    return out


def _esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_digest(entries, feed_url="http://127.0.0.1:8000/"):
    day = datetime.now(timezone.utc).date().isoformat()
    subject = f"AI nuggets · {day} · {len(entries)} new"
    rows = []
    for e in entries:
        rows.append(
            '<div style="margin:0 0 18px;padding:14px 16px;border:1px solid #e3e5dc;border-radius:12px">'
            f'<div style="color:#0a4b3d;font-size:12px;font-weight:600">{_esc(e["site"])}</div>'
            '<div style="font-size:16px;font-weight:600;margin:4px 0 6px">'
            f'<a href="{_esc(e["url"])}" style="color:#15201a;text-decoration:none">{_esc(e["title"])}</a></div>'
            f'<div style="color:#57615a;font-size:14px;line-height:1.5">{_esc(e["nugget"])}</div>'
            '</div>')
    html = (
        '<div style="font-family:system-ui,-apple-system,Segoe UI,sans-serif;max-width:600px;margin:0 auto">'
        f'<h2 style="font-size:18px">Fresh from the AI labs · {day}</h2>'
        f'{"".join(rows)}'
        f'<p style="font-size:13px"><a href="{_esc(feed_url)}">Open the full feed →</a></p>'
        '</div>')
    return subject, html


def send_digest(subject, html, api_key, sender, to):
    resp = httpx.post(RESEND_ENDPOINT,
                      headers={"Authorization": f"Bearer {api_key}"},
                      json={"from": sender, "to": [to], "subject": subject, "html": html},
                      timeout=30)
    resp.raise_for_status()
    return resp.json()


def main() -> None:
    load_dotenv()
    api_key = os.getenv("RESEND_API_KEY")
    to = os.getenv("DIGEST_TO")
    sender = os.getenv("DIGEST_FROM", "onboarding@resend.dev")
    feed_url = os.getenv("FEED_URL", "http://127.0.0.1:8000/")
    if not api_key or not to:
        raise SystemExit("Set RESEND_API_KEY and DIGEST_TO in .env")
    manifest = load_manifest(MANIFEST_PATH)
    state = load_state()
    entries = select_new_entries(manifest, state.get("last_sent"))
    if not entries:
        print("No new nuggets since last digest. Nothing sent.")
        return
    subject, html = build_digest(entries, feed_url=feed_url)
    send_digest(subject, html, api_key, sender, to)
    state["last_sent"] = max(e["scraped_at"] for e in entries)
    save_state(state)
    print(f"Sent digest with {len(entries)} nugget(s) to {to}.")


if __name__ == "__main__":
    main()
