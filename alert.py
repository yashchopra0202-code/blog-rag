import json
import os
import sys

import httpx
from dotenv import load_dotenv
import observability

RESEND_ENDPOINT = "https://api.resend.com/emails"
STATUS_PATH = "data/scrape_status.json"


def load_status(path=STATUS_PATH):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def check_health(status, outcomes):
    """Return human-readable problems; [] means healthy.

    `outcomes` maps step name -> GitHub step outcome ('success'|'failure'|'').
    A run can be 'green' yet broken, so we also inspect the scrape status file.
    """
    problems = []
    for step in ("nuggetize", "digest", "telegram"):
        if outcomes.get(step) == "failure":
            problems.append(f"the {step} step failed")
    if status is None:
        if outcomes.get("scrape") == "failure":
            problems.append("the scrape step crashed before writing a status file")
    elif status.get("sites_ok", 0) == 0:
        problems.append(f"scraping failed on all {status.get('sites_total', '?')} sites")
    return problems


def send_alert(problems, api_key, sender, to, run_url=""):
    items = "".join(f"<li>{p}</li>" for p in problems)
    link = f'<p><a href="{run_url}">View the workflow run &rarr;</a></p>' if run_url else ""
    html = ('<div style="font-family:-apple-system,Segoe UI,sans-serif;max-width:560px">'
            '<h2 style="color:#9A3324">&#9888;&#65039; Daily nuggets — run needs attention</h2>'
            f'<ul style="color:#15201A;font-size:15px;line-height:1.6">{items}</ul>{link}</div>')
    resp = httpx.post(RESEND_ENDPOINT,
                      headers={"Authorization": f"Bearer {api_key}"},
                      json={"from": sender, "to": [to],
                            "subject": "⚠️ Daily nuggets needs attention", "html": html},
                      timeout=30)
    resp.raise_for_status()
    return resp.json()


def main():
    load_dotenv()
    observability.init_sentry("alert")
    outcomes = {k: os.getenv(f"{k.upper()}_OUTCOME", "")
                for k in ("scrape", "nuggetize", "digest", "telegram")}
    problems = check_health(load_status(), outcomes)
    if not problems:
        print("Health check: healthy.")
        return
    print("Health check FAILED:", "; ".join(problems))
    api_key, to = os.getenv("RESEND_API_KEY"), os.getenv("DIGEST_TO")
    sender = os.getenv("DIGEST_FROM", "onboarding@resend.dev")
    if api_key and to:
        try:
            send_alert(problems, api_key, sender, to, os.getenv("RUN_URL", ""))
            print("Alert email sent.")
        except Exception as e:  # noqa: BLE001 - best effort; the red run still notifies
            print(f"[warn] alert email failed to send: {e}")
    sys.exit(1)  # mark the run red so GitHub's native notification also fires


if __name__ == "__main__":
    main()
