"""Supabase (PostgREST) helpers for the telegram_subscribers table, over httpx
so no extra dependency is needed. Service-role key — server-side only."""
import os
import httpx

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
