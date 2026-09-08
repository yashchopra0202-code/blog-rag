"""Broadcast the daily digest to Telegram subscribers. Run by CI after the
email step, gated by config.json cadence. Best-effort per recipient."""
import os
import time
from dotenv import load_dotenv

import config
import digest
import telegram as tg
import telegram_api
import store
from scraper import load_manifest

MANIFEST_PATH = "data/manifest.json"
STATE_PATH = "data/telegram_state.json"
SEND_DELAY = 0.04   # ~25 msg/s pacing (Telegram bulk limit is ~30/s)

def broadcast(now=None, sleep=None, delay=SEND_DELAY):
    """Broadcast the digest to active subscribers, best-effort and paced.
    `sleep`/`delay` are injectable so tests don't actually sleep. A 403 (bot
    blocked/kicked) deactivates that subscriber so it's never retried; a 429 is
    retried once honoring retry_after; any other error just counts as failed."""
    sleep = sleep or time.sleep
    cfg = config.load_config()
    cadence = cfg.get("cadence", "daily")
    force = os.getenv("DIGEST_FORCE", "").lower() in ("1", "true", "yes")
    if not digest.should_send_today(cfg, now=now, force=force):
        print(f"Cadence is {cadence}; not a send day. Nothing broadcast.")
        return {"sent": 0, "failed": 0, "dropped": 0, "skipped": True}
    limit = cfg["weekly_limit"] if cadence == "weekly" else int(os.getenv("DIGEST_LIMIT", "20"))
    manifest = load_manifest(MANIFEST_PATH)
    state = digest.load_state(STATE_PATH)
    since = digest.effective_since(state, now=now, cadence=cadence)
    entries = digest.curate(digest.select_new_entries(manifest, since, enabled_labs=cfg.get("enabled_labs")))[:limit]
    if not entries:
        print("No new nuggets since last broadcast.")
        return {"sent": 0, "failed": 0, "dropped": 0, "skipped": False}
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    feed_url = os.getenv("FEED_URL") or "https://blog-rag.onrender.com/"
    msg = tg.format_digest_message(entries, feed_url)
    sent = failed = dropped = 0
    for i, sub in enumerate(store.active_subscribers()):
        cid = sub.get("chat_id")
        if i:
            sleep(delay)   # pace between sends (not before the first)
        try:
            telegram_api.send_message(token, cid, msg)
            sent += 1
        except telegram_api.TelegramError as e:
            if e.status_code == 403:   # bot blocked/kicked — drop this dead chat
                try:
                    store.deactivate_subscriber(cid)
                except Exception as de:  # noqa: BLE001 - dropping is best-effort too
                    print(f"  [warn] could not deactivate {cid}: {de}")
                dropped += 1
                print(f"  [drop] {cid} blocked the bot (403); deactivated")
            elif e.status_code == 429:   # rate-limited — retry once after retry_after
                try:
                    sleep(e.retry_after if e.retry_after is not None else 1)
                    telegram_api.send_message(token, cid, msg)
                    sent += 1
                except Exception as e2:  # noqa: BLE001
                    failed += 1
                    print(f"  [warn] {cid} failed after 429 retry: {e2}")
            else:
                failed += 1
                print(f"  [warn] {cid} failed (HTTP {e.status_code})")
        except Exception as e:  # noqa: BLE001 - one bad recipient must not abort
            failed += 1
            print(f"  [warn] send to {cid} failed: {e}")
    state["last_sent"] = max(e["scraped_at"] for e in entries)
    digest.save_state(state, STATE_PATH)
    print(f"Broadcast: {sent} sent, {failed} failed, {dropped} dropped (blocked).")
    return {"sent": sent, "failed": failed, "dropped": dropped, "skipped": False}

def main():
    load_dotenv()
    broadcast()

if __name__ == "__main__":
    main()
