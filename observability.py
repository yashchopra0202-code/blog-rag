"""Sentry error tracking.

`init_sentry()` is a NO-OP when `SENTRY_DSN` is unset, so importing or running
any entry point with no DSN configured is safe — nothing is sent. Set the
`SENTRY_DSN` env var (Render + GitHub Actions) to switch on error capture across
the app and the daily pipeline; `SENTRY_ENVIRONMENT` optionally labels events.
"""
import os

try:
    import sentry_sdk
except ImportError:   # the scrapling venv is kept sentry-free by design
    sentry_sdk = None


def init_sentry(component: str = "app") -> bool:
    """Initialize Sentry when `SENTRY_DSN` is set and the SDK is importable.
    Returns True when initialized, False (no-op) when the DSN is absent or the
    SDK is unavailable. `component` tags events (api/digest/…) for easy triage."""
    dsn = os.getenv("SENTRY_DSN")
    if not dsn or sentry_sdk is None:
        return False
    sentry_sdk.init(
        dsn=dsn,
        environment=os.getenv("SENTRY_ENVIRONMENT", "production"),
        traces_sample_rate=0,   # errors only — no performance tracing
    )
    sentry_sdk.set_tag("component", component)
    return True
