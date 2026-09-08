"""Supabase (PostgREST) helpers for the telegram_subscribers table, over httpx
so no extra dependency is needed. Service-role key — server-side only."""
import os
import httpx
import secrets
from datetime import datetime, timezone

TABLE = "telegram_subscribers"

def _conf():
    url = os.environ["SUPABASE_URL"].rstrip("/")
    key = os.environ["SUPABASE_SERVICE_KEY"]
    return url, {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}

def add_subscriber(chat):
    url, headers = _conf()
    headers = {**headers, "Prefer": "resolution=merge-duplicates"}
    row = {"chat_id": chat.get("id"), "first_name": chat.get("first_name", ""),
           "username": chat.get("username", ""), "active": True}
    r = httpx.post(f"{url}/rest/v1/{TABLE}", headers=headers, json=row, timeout=15)
    r.raise_for_status()

def deactivate_subscriber(chat_id):
    url, headers = _conf()
    r = httpx.patch(f"{url}/rest/v1/{TABLE}", headers=headers,
                    json={"active": False}, params={"chat_id": f"eq.{chat_id}"}, timeout=15)
    r.raise_for_status()

def active_subscribers():
    url, headers = _conf()
    r = httpx.get(f"{url}/rest/v1/{TABLE}", headers=headers,
                  params={"active": "eq.true", "select": "chat_id,first_name"}, timeout=15)
    r.raise_for_status()
    return r.json()


EMAIL_TABLE = "email_subscribers"
RL_TABLE = "rate_limits"
SENT_TABLE = "sent_digests"


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# --- email subscribers ------------------------------------------------------

def add_email_subscriber(email):
    """Insert a pending subscriber (ignore if already present), then return the
    current row so callers never downgrade an already-confirmed address."""
    email = email.strip().lower()
    url, headers = _conf()
    ins = {**headers, "Prefer": "resolution=ignore-duplicates,return=representation"}
    row = {"email": email, "status": "pending",
           "confirm_token": secrets.token_urlsafe(32),
           "unsub_token": secrets.token_urlsafe(32)}
    httpx.post(f"{url}/rest/v1/{EMAIL_TABLE}", headers=ins, json=row, timeout=15).raise_for_status()
    r = httpx.get(f"{url}/rest/v1/{EMAIL_TABLE}", headers=headers,
                  params={"email": f"eq.{email}",
                          "select": "email,status,confirm_token,unsub_token"}, timeout=15)
    r.raise_for_status()
    rows = r.json()
    return rows[0] if rows else row


def confirm_email(token):
    url, headers = _conf()
    h = {**headers, "Prefer": "return=representation"}
    r = httpx.patch(f"{url}/rest/v1/{EMAIL_TABLE}", headers=h,
                    json={"status": "confirmed", "confirmed_at": _now()},
                    params={"confirm_token": f"eq.{token}", "status": "eq.pending"}, timeout=15)
    r.raise_for_status()
    return bool(r.json())


def unsubscribe_email(token):
    url, headers = _conf()
    h = {**headers, "Prefer": "return=representation"}
    r = httpx.patch(f"{url}/rest/v1/{EMAIL_TABLE}", headers=h,
                    json={"status": "unsubscribed"},
                    params={"unsub_token": f"eq.{token}"}, timeout=15)
    r.raise_for_status()
    return bool(r.json())


def confirmed_email_subscribers():
    url, headers = _conf()
    r = httpx.get(f"{url}/rest/v1/{EMAIL_TABLE}", headers=headers,
                  params={"status": "eq.confirmed", "select": "email,unsub_token"}, timeout=15)
    r.raise_for_status()
    return r.json()


def mark_email_status(email, status):
    url, headers = _conf()
    httpx.patch(f"{url}/rest/v1/{EMAIL_TABLE}", headers=headers,
                json={"status": status},
                params={"email": f"eq.{email.strip().lower()}"}, timeout=15).raise_for_status()


# --- rate limit (fixed window) ----------------------------------------------

def rate_limit_ok(bucket, limit):
    """Increment the counter for `bucket` and return True while count <= limit.
    Read-then-upsert; racy under heavy concurrency but fine at this scale."""
    url, headers = _conf()
    r = httpx.get(f"{url}/rest/v1/{RL_TABLE}", headers=headers,
                  params={"bucket": f"eq.{bucket}", "select": "count"}, timeout=15)
    r.raise_for_status()
    rows = r.json()
    count = (rows[0]["count"] if rows else 0) + 1
    up = {**headers, "Prefer": "resolution=merge-duplicates"}
    httpx.post(f"{url}/rest/v1/{RL_TABLE}", headers=up,
               json={"bucket": bucket, "count": count, "window_start": _now()},
               timeout=15).raise_for_status()
    return count <= limit


# --- digest idempotency guard -----------------------------------------------

def digest_already_sent(key):
    url, headers = _conf()
    r = httpx.get(f"{url}/rest/v1/{SENT_TABLE}", headers=headers,
                  params={"digest_key": f"eq.{key}", "select": "digest_key"}, timeout=15)
    r.raise_for_status()
    return bool(r.json())


def mark_digest_sent(key):
    url, headers = _conf()
    h = {**headers, "Prefer": "resolution=ignore-duplicates"}
    httpx.post(f"{url}/rest/v1/{SENT_TABLE}", headers=h,
               json={"digest_key": key, "sent_at": _now()}, timeout=15).raise_for_status()
