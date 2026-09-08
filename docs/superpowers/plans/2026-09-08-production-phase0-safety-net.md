# Production Roadmap — Phase 0: Safety Net — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make blog-rag safe to iterate on publicly by adding a CI `pytest` gate on every push/PR and closing the one hole in the existing pipeline-failure alerting (Telegram broadcast failures are currently silent).

**Architecture:** Two small, independent changes. (1) A new GitHub Actions workflow `ci.yml` runs the test suite on push/PR as a merge gate, separate from the existing `daily.yml` cron pipeline. (2) The existing `alert.py` health check is extended to inspect the `telegram` step outcome, and `daily.yml` passes that outcome in. No new dependencies, no runtime/serving changes.

**Tech Stack:** Python 3.12, pytest 9.1.1, GitHub Actions, existing `alert.py` (Resend email alerts).

**Spec:** `docs/superpowers/specs/2026-09-08-blog-rag-production-roadmap-design.md` (see "Scope correction (2026-09-08)" — pipeline alerting already exists; the CI gate does not).

## Global Constraints

- **Python 3.12** (matches `daily.yml` and `render.yaml` `PYTHON_VERSION=3.12.14`).
- **No new dependencies.** Everything uses `requirements.txt` as-is.
- **RAG test suite command (the CI gate):** `.venv/bin/python -m pytest -q --ignore=tests/test_extraction.py` — verified locally: **88 passed, 0 failed with no secrets set**. `tests/test_extraction.py` is excluded because it imports `scrapling`, which lives only in the separate `~/.venvs/scrapling` venv (not in `requirements.txt`).
- **Do not require secrets for the gate.** The suite passes with all API-key env vars unset; the CI gate must not depend on any secret.
- **Commit trailer:** end every commit body with:
  `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`
  `Claude-Session: https://claude.ai/code/session_01TQ1fNc6CoWAnrjCSMC2fNn`
- **Branch:** this work happens on a feature branch (e.g. `feat/phase0-safety-net`), not directly on `main`.

---

### Task 1: CI test-gate workflow

**Files:**
- Create: `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: the RAG test suite command from Global Constraints.
- Produces: a GitHub Actions workflow named `ci` with a required `tests` job (blocking) and an optional `scraper-tests` job (non-blocking). No code symbols; later tasks don't import anything from this.

- [ ] **Step 1: Create the workflow file**

Create `.github/workflows/ci.yml` with exactly this content:

```yaml
# .github/workflows/ci.yml
# Test gate: runs on every push and PR, separate from the daily.yml cron pipeline.
name: ci
on:
  push:
  pull_request:
permissions:
  contents: read
jobs:
  tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install RAG deps
        run: |
          python -m venv .venv
          .venv/bin/pip install -r requirements.txt
      # test_extraction.py imports scrapling (separate venv, not in requirements.txt),
      # so it is covered by the non-blocking scraper-tests job below, not here.
      - name: Run test suite
        run: .venv/bin/python -m pytest -q --ignore=tests/test_extraction.py
  scraper-tests:
    runs-on: ubuntu-latest
    continue-on-error: true   # scrapling's stealth stack is fiddly on CI; visible but never blocks
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install scraper (scrapling) deps
        run: |
          python -m venv .venv-scrapling
          .venv-scrapling/bin/pip install "scrapling[fetchers]" click pytest
      - name: Run extraction tests
        run: .venv-scrapling/bin/python -m pytest -q tests/test_extraction.py
```

- [ ] **Step 2: Verify the gate command passes locally (the exact command CI runs)**

Run: `.venv/bin/python -m pytest -q --ignore=tests/test_extraction.py`
Expected: `88 passed` (or `89 passed` if a `.env` is present), `0 failed`.

- [ ] **Step 3: Validate the workflow YAML syntax**

Run: `.venv/bin/python -c "import yaml,sys; yaml.safe_load(open('.github/workflows/ci.yml')); print('yaml ok')"`
Expected: `yaml ok` (no exception). Note: `pyyaml` ships transitively; if the import fails, instead run `python3 -c "import json; print('skip')"` and rely on the Actions run in Step 5 to validate.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "$(cat <<'EOF'
ci: add pytest gate on push/PR

New ci.yml runs the RAG test suite (88 tests, no secrets needed) as a
blocking gate, plus a non-blocking scrapling job for extraction tests.
Separate from the daily.yml cron pipeline.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01TQ1fNc6CoWAnrjCSMC2fNn
EOF
)"
```

- [ ] **Step 5: Push and confirm the Action runs green**

Run: `git push -u origin feat/phase0-safety-net` then `gh run list --workflow=ci.yml --limit 1` and `gh run watch` (or check the Actions tab).
Expected: the `tests` job is **green**. The `scraper-tests` job may be red — that is acceptable (it is `continue-on-error`); the workflow run itself must not be failed by it.

---

### Task 2: Wire the Telegram broadcast outcome into the health check

**Files:**
- Modify: `alert.py` (`check_health` loop ~line 26; `main` outcomes dict ~line 51)
- Modify: `tests/test_alert.py` (add one test)
- Modify: `.github/workflows/daily.yml` (`Health check & alert` step `env:`)

**Interfaces:**
- Consumes: `alert.check_health(status, outcomes)` where `outcomes: dict[str, str]` maps step name → GitHub outcome (`'success'|'failure'|''`), and `daily.yml`'s existing `Telegram broadcast` step with `id: telegram`.
- Produces: `check_health` now flags `telegram` failures with the message `"the telegram step failed"` (same shape as the existing `nuggetize`/`digest` messages).

- [ ] **Step 1: Write the failing test**

Add to `tests/test_alert.py`:

```python
def test_flags_telegram_failure():
    status = {"sites_total": 18, "sites_ok": 18, "new_articles": 1}
    outcomes = {"scrape": "success", "nuggetize": "success",
                "digest": "success", "telegram": "failure"}
    problems = alert.check_health(status, outcomes)
    assert any("telegram" in p for p in problems)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_alert.py::test_flags_telegram_failure -v`
Expected: FAIL — `assert any("telegram" in p ...)` is False because `check_health` does not yet inspect `telegram`.

- [ ] **Step 3: Add `telegram` to the failure-checked steps in `alert.py`**

In `alert.py`, `check_health`, change:

```python
    for step in ("nuggetize", "digest"):
```

to:

```python
    for step in ("nuggetize", "digest", "telegram"):
```

- [ ] **Step 4: Add `telegram` to the outcomes read in `alert.py` `main()`**

In `alert.py`, `main`, change:

```python
    outcomes = {k: os.getenv(f"{k.upper()}_OUTCOME", "")
                for k in ("scrape", "nuggetize", "digest")}
```

to:

```python
    outcomes = {k: os.getenv(f"{k.upper()}_OUTCOME", "")
                for k in ("scrape", "nuggetize", "digest", "telegram")}
```

- [ ] **Step 5: Run the new test and the full alert suite to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_alert.py -v`
Expected: PASS — all existing alert tests plus `test_flags_telegram_failure` green (the existing `test_flags_step_failures` still passes because `telegram` defaults to `success` there).

- [ ] **Step 6: Pass the Telegram outcome from `daily.yml` into the alert step**

In `.github/workflows/daily.yml`, in the `Health check & alert` step's `env:` block, add this line alongside the other `*_OUTCOME` vars:

```yaml
          TELEGRAM_OUTCOME: ${{ steps.telegram.outcome }}
```

(The `Telegram broadcast` step already declares `id: telegram`, so `steps.telegram.outcome` is available.)

- [ ] **Step 7: Re-run the full gate command to confirm nothing else broke**

Run: `.venv/bin/python -m pytest -q --ignore=tests/test_extraction.py`
Expected: `89 passed` (88 previous + the 1 new test), `0 failed`.

- [ ] **Step 8: Commit**

```bash
git add alert.py tests/test_alert.py .github/workflows/daily.yml
git commit -m "$(cat <<'EOF'
fix(alert): flag telegram broadcast failures in the daily health check

check_health and main now inspect the telegram step outcome, and
daily.yml passes steps.telegram.outcome into the alert step, so a failed
broadcast marks the run red and emails an alert instead of failing silently.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01TQ1fNc6CoWAnrjCSMC2fNn
EOF
)"
```

- [ ] **Step 9: Push and confirm CI stays green**

Run: `git push` then confirm the `ci.yml` `tests` job is green for this commit.
Expected: green (includes the new `test_flags_telegram_failure`).

---

## Self-Review

**1. Spec coverage (Phase 0 rows of the roadmap):**
- "CI test gate (`pytest` on every push/PR)" → Task 1. ✓
- "wire the Telegram broadcast outcome into the existing `alert.py` health check" → Task 2. ✓
- Everything else the old Phase 0 mentioned ("commit baseline", "pipeline-failure alerting") is already in the repo (see spec Scope correction) — no task needed. ✓

**2. Placeholder scan:** No TBD/TODO/"handle edge cases". Every code step shows exact before/after text and exact commands. ✓

**3. Type consistency:** `check_health(status, outcomes)` and the `outcomes` dict shape match `alert.py` and the existing `tests/test_alert.py` fixtures exactly. The step id `telegram` matches `daily.yml`'s existing `id: telegram`. The gate command is identical in Global Constraints, `ci.yml`, and the verify steps. ✓

## Notes / follow-ups (not this plan)

- After merge, enable branch protection on `main` requiring the `ci / tests` check — a repo setting, not code.
- Phase 2 (next plan) builds the `email_subscribers` Supabase table + double-opt-in subscribe box. `pipeline_state` and `rate_limits` migrations remain deferred per the spec's Scope correction.
