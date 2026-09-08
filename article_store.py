"""Supabase Storage REST client for the article archive (over httpx — no SDK).
Service-role key: server/build-side only. Bucket holds one object per article,
keyed by the file basename."""
import os
import httpx

BUCKET = "article-archive"
_LIST_PAGE = 100


def _conf():
    url = os.environ["SUPABASE_URL"].rstrip("/")
    key = os.environ["SUPABASE_SERVICE_KEY"]
    return url, {"Authorization": f"Bearer {key}", "apikey": key}


def _creds_present() -> bool:
    return bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_KEY"))


def ensure_bucket() -> None:
    url, headers = _conf()
    r = httpx.post(f"{url}/storage/v1/bucket",
                   headers={**headers, "Content-Type": "application/json"},
                   json={"id": BUCKET, "name": BUCKET, "public": False}, timeout=30)
    if r.status_code in (400, 409):   # already exists — fine
        return
    r.raise_for_status()


def upload_article(local_path: str) -> None:
    url, headers = _conf()
    name = os.path.basename(local_path)
    with open(local_path, "rb") as f:
        body = f.read()
    r = httpx.post(f"{url}/storage/v1/object/{BUCKET}/{name}",
                   headers={**headers, "Content-Type": "text/markdown", "x-upsert": "true"},
                   content=body, timeout=60)
    r.raise_for_status()


def download_all(dest_dir: str) -> int:
    url, headers = _conf()
    os.makedirs(dest_dir, exist_ok=True)
    names, offset = [], 0
    while True:
        r = httpx.post(f"{url}/storage/v1/object/list/{BUCKET}",
                       headers={**headers, "Content-Type": "application/json"},
                       json={"prefix": "", "limit": _LIST_PAGE, "offset": offset}, timeout=30)
        r.raise_for_status()
        page = r.json()
        names += [o["name"] for o in page if o.get("name")]
        if len(page) < _LIST_PAGE:
            break
        offset += _LIST_PAGE
    for name in names:
        g = httpx.get(f"{url}/storage/v1/object/{BUCKET}/{name}", headers=headers, timeout=60)
        g.raise_for_status()
        with open(os.path.join(dest_dir, name), "wb") as f:
            f.write(g.content)
    return len(names)
