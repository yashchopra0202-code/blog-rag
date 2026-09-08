"""Send transactional + digest emails via Resend (HTTP, over httpx — no SDK).
Isolated so the digest and the subscribe-confirmation flow share one sender."""
import os
import httpx

RESEND_ENDPOINT = "https://api.resend.com/emails"


def _esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def send_email(to, subject, html, attachments=None, api_key=None, sender=None):
    api_key = api_key or os.getenv("RESEND_API_KEY")
    sender = sender or os.getenv("DIGEST_FROM", "onboarding@resend.dev")
    payload = {"from": sender, "to": [to], "subject": subject, "html": html}
    if attachments:
        payload["attachments"] = attachments
    resp = httpx.post(RESEND_ENDPOINT,
                      headers={"Authorization": f"Bearer {api_key}"},
                      json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def confirmation_html(confirm_url: str) -> str:
    u = _esc(confirm_url)
    return (
        '<div style="font-family:-apple-system,Segoe UI,sans-serif;max-width:520px;'
        'color:#15201A;font-size:15px;line-height:1.6">'
        '<h2 style="color:#0A5F4E">Confirm your subscription</h2>'
        '<p>Someone (hopefully you) subscribed this address to the daily AI-labs digest. '
        'Confirm to start receiving it:</p>'
        f'<p><a href="{u}" style="background:#0E7C66;color:#fff;text-decoration:none;'
        'padding:10px 18px;border-radius:10px;font-weight:600;display:inline-block">'
        'Confirm subscription</a></p>'
        '<p style="color:#7C867E;font-size:13px">If it wasn\'t you, just ignore this email — '
        'you won\'t be subscribed.</p></div>')


def unsubscribe_footer(unsub_url: str) -> str:
    u = _esc(unsub_url)
    return (
        '<div style="margin-top:22px;padding-top:14px;border-top:1px solid #E3E5DC;'
        'color:#7C867E;font-size:12px;line-height:1.5">'
        f'You\'re receiving this because you subscribed. <a href="{u}" '
        'style="color:#0A5F4E">Unsubscribe</a>.</div>')
