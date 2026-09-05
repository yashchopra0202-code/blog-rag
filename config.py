"""Runtime controls for the daily/weekly digest: which labs are active and how
often the email is sent. Values live in config.json at the repo root (git-tracked
so changes show up in the daily refresh commit); a missing or broken file falls
back to DEFAULTS so a config typo can never take the pipeline down."""
import json

DEFAULTS = {
    "cadence": "daily",     # "daily" | "weekly"
    "weekly_day": "mon",    # weekday the weekly "best of" is sent
    "weekly_limit": 40,     # nugget pool size in weekly mode (daily uses DIGEST_LIMIT)
    "enabled_labs": None,   # None/[] = all labs on; a list of slugs = allowlist
}


def load_config(path="config.json"):
    cfg = dict(DEFAULTS)
    try:
        with open(path, encoding="utf-8") as f:
            cfg.update(json.load(f))
    except (OSError, ValueError):
        pass
    return cfg


def enabled_sites(sites, cfg):
    """Filter SITES-shaped dicts (keyed by "name") to the enabled allowlist.
    An empty or absent allowlist means "all on" — never "scrape nothing"."""
    labs = cfg.get("enabled_labs")
    if not labs:
        return sites
    return [s for s in sites if s["name"] in labs]
