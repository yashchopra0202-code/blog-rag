import observability


def test_init_sentry_noop_without_dsn(monkeypatch):
    monkeypatch.delenv("SENTRY_DSN", raising=False)
    calls = []
    monkeypatch.setattr(observability.sentry_sdk, "init", lambda **kw: calls.append(kw))
    result = observability.init_sentry("api")
    assert result is False        # not initialized
    assert calls == []            # sentry_sdk.init never called


def test_init_sentry_initializes_with_dsn(monkeypatch):
    monkeypatch.setenv("SENTRY_DSN", "https://abc@o1.ingest.sentry.io/2")
    calls = []
    monkeypatch.setattr(observability.sentry_sdk, "init", lambda **kw: calls.append(kw))
    result = observability.init_sentry("digest")
    assert result is True
    assert len(calls) == 1
    assert calls[0]["dsn"] == "https://abc@o1.ingest.sentry.io/2"
    assert calls[0]["traces_sample_rate"] == 0   # errors only, free-tier friendly


def test_init_sentry_noop_when_sdk_unavailable(monkeypatch):
    # The scrapling venv doesn't install sentry-sdk; init must degrade to a no-op.
    monkeypatch.setenv("SENTRY_DSN", "https://abc@o1.ingest.sentry.io/2")
    monkeypatch.setattr(observability, "sentry_sdk", None)
    assert observability.init_sentry("scraper") is False
