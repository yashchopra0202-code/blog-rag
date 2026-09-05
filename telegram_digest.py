"""Broadcast the daily digest to Telegram subscribers. Run by CI after the
email step, gated by config.json cadence. Best-effort per recipient."""
import os
from dotenv import load_dotenv

import config
import digest
import telegram as tg
import telegram_api
import store
from scraper import load_manifest

MANIFEST_PATH = "data/manifest.json"
STATE_PATH = "data/telegram_state.json"

def broadcast(now=None):
    cfg = config.load_config()
    cadence = cfg.get("cadence", "daily")
    force = os.getenv("DIGEST_FORCE", "").lower() in ("1", "true", "yes")
    if not digest.should_send_today(cfg, now=now, force=force):
        print(f"Cadence is {cadence}; not a send day. Nothing broadcast.")
        return {"sent": 0, "failed": 0, "skipped": True}
    limit = cfg["weekly_limit"] if cadence == "weekly" else int(os.getenv("DIGEST_LIMIT", "20"))
    manifest = load_manifest(MANIFEST_PATH)
    state = digest.load_state(STATE_PATH)
    since = digest.effective_since(state, now=now, cadence=cadence)
    entries = digest.curate(digest.select_new_entries(manifest, since, enabled_labs=cfg.get("enabled_labs")))[:limit]
    if not entries:
        print("No new nuggets since last broadcast.")
        return {"sent": 0, "failed": 0, "skipped": False}
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    feed_url = os.getenv("FEED_URL") or "https://blog-rag.onrender.com/"
    msg = tg.format_digest_message(entries, feed_url)
    sent = failed = 0
    for sub in store.active_subscribers():
        try:
            telegram_api.send_message(token, sub["chat_id"], msg)
            sent += 1
        except Exception as e:  # noqa: BLE001 - one bad recipient must not abort
            print(f"  [warn] send to {sub.get('chat_id')} failed: {e}")
            failed += 1
    state["last_sent"] = max(e["scraped_at"] for e in entries)
    digest.save_state(state, STATE_PATH)
    print(f"Broadcast to {sent} subscriber(s); {failed} failed.")
    return {"sent": sent, "failed": failed, "skipped": False}

def main():
    load_dotenv()
    broadcast()

if __name__ == "__main__":
    main()
