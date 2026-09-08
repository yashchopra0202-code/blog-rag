# blog-rag → Production-Grade Public Product — Roadmap Design Spec

**Date:** 2026-09-08
**Status:** Approved design, pending spec review → implementation plan
**Repo:** `~/blog-rag` (FastAPI + RAG, hosted on Render, daily pipeline via GitHub Actions, Telegram bot + email digest)

## Goal

Take blog-rag from a working personal tool to a **production-grade public product** that safely serves the **first 100–200 users** on the **current architecture** (Python / FastAPI / Render / GitHub-Actions-cron), without a premature rewrite. The two surfaces people actually return through — **email digest and Telegram** — are the heroes and get hardened to production quality; the web feed and `/ask` stay live but secondary.

## Decisions (locked with the user)

| Decision | Choice | Rationale |
|---|---|---|
| Audience | Public, real users; **start at 100–200** | Current architecture is sufficient at that scale; defer scale infra (YAGNI). |
| Hero surfaces (v1) | **Email digest + Telegram** | Push channels reach people where they are; web has low return-visit pull. |
| Migration strategy | **Harden the current Python/Render stack** (strangler deferred) | Avoid building production hardening twice; keep the live site working throughout. |
| Writable state | Move **subscribers + pipeline state + rate-limit counters** to **Supabase Postgres**; everything else stays JSON-in-git | Only *concurrently-written* data breaks git-as-db. |
| Cold storage | **Cheap durable article archive in Supabase Storage**; git stops carrying `.md` files | Durability + stop repo bloat; one vendor (already using Supabase). |
| Cost / access | Free + **hard rate limits** (per-IP `/ask` quota + global daily spend cap) | `/ask` is the only unbounded-cost surface and it is now secondary. |
| Auth (v1) | **Anonymous**; accounts later | Simplest safe launch; IP limits + global cap contain abuse at this scale. |

## Scope correction (2026-09-08, after reading the code)

Before writing the Phase 0/1 implementation plan, the actual code was traced and two spec assumptions were corrected (kept here for traceability):

1. **Pipeline-failure alerting already exists.** `alert.py` (`check_health` + `send_alert`) runs in `daily.yml`'s `if: always()` "Health check & alert" step. Phase 0's real, missing work is a **CI `pytest` gate on push/PR** (none exists today) plus **wiring the Telegram broadcast outcome** into `alert.py` (currently only `scrape`/`nuggetize`/`digest` outcomes are checked, so a broadcast failure is silent).
2. **Original Phase 1 dissolved.** Every `*_state.json` file (`digest_state`, `telegram_state`, `scrape_status`) is written **only by CI pipeline scripts** — never by a live HTTP request — so there is no concurrent-write race to fix. The only genuinely live-written state not already in Postgres is the **email subscriber list, which does not exist yet**; it is built in Phase 2 with the subscribe box. `rate_limits` moves to Phase 5 with `/ask`. This keeps to the spec's own principle: *migrate by write-concurrency, not importance.*

## Non-goals (v1 / YAGNI)

- **No Next.js + Supabase-app rewrite.** The hybrid migration (Next.js frontend, Supabase-served data, user accounts) is a *later growth phase*, triggered when usage exceeds the current architecture (~>200 users, or when web/`/ask`/accounts become a priority).
- **No user accounts, login, billing, or paid tier.** Anonymous v1.
- **No moving `manifest.json` / nuggets / the vector index off git-as-db.** They are single-writer (the daily pipeline) and read-only at runtime — safe as-is. Moving the manifest is explicitly deferred.
- **No autoscaling / queues / multi-instance serving.** Not needed at 100–200 users.
- **No `/ask` feature work.** It is hardened for cost/abuse only, not improved.

## Key constraints (surfaced, not assumed)

1. **Concurrency is the dividing line, not importance.** Data written *only* by the once-a-day single-writer pipeline (manifest, nuggets, vector index) is safe as JSON-in-git. Data a *public HTTP request* can write (subscribe, unsubscribe, rate-limit counters) must be in Postgres — git-as-db silently clobbers concurrent writes and the CI commit-back can race a live write.
2. **Supabase Postgres is already in use.** `store.py` reads/writes `telegram_subscribers` via **PostgREST over `httpx`** (service-role key, server-side only, no ORM, no new dependency). New tables follow this same pattern. This is an *extension*, not a new integration.
3. **Render free tier sleeps after ~15 min idle** (~50s cold start). Telegram retries webhooks so nothing is lost; email/broadcast run from CI, unaffected. Acceptable for v1; the Starter plan removes it if cold starts hurt.
4. **Public email collection is legally regulated.** Double opt-in, one-click unsubscribe, a compliant footer (physical postal address), and consent capture are requirements (CAN-SPAM / GDPR), not enhancements.
5. **CI-as-cron is the pipeline runtime.** `scrape → nuggetize → ingest(skipped in CI) → digest → telegram broadcast` runs on the daily GitHub Action. Robustness work lands there.

## Target architecture (v1)

The shape stays Python. Three things change *where they live*; the edges get hardened.

```
                    ┌─────────────────────────────────────┐
  GitHub Actions    │  Python pipeline (core unchanged)    │
  daily cron  ────► │  scrape → nuggetize → digest →        │
                    │           telegram broadcast          │
                    └──────┬──────────────┬─────────────────┘
                           │              │
        raw article .md ───┘              └─── subscriber + state reads/writes
                           ▼                                 ▼
             ┌────────────────────────┐        ┌────────────────────────────┐
             │  SUPABASE STORAGE       │        │  SUPABASE POSTGRES          │
             │  durable article archive│        │  telegram_subscribers (has) │
             │  articles/{lab}/{slug}.md│       │  email_subscribers   (new)  │
             └────────────────────────┘        │  pipeline_state      (new)  │
                                                │  rate_limits         (new)  │
  manifest.json + nuggets ── stays JSON-in-git  └────────────────────────────┘
  chroma_db (vector index) ── rebuilt on deploy (read-only, /ask only)

  Render web service (FastAPI):
    GET / , /feed , /ask         (secondary; /ask rate-limited + spend-capped)
    POST /subscribe , /confirm , /unsubscribe   (email, double opt-in)
    POST /telegram/webhook       (secret-token validated)
```

## Data & storage model

### Supabase Postgres (PostgREST + httpx, same pattern as `store.py`)

- **`telegram_subscribers`** — *exists.* `chat_id` (pk), `first_name`, `username`, `subscribed_at`, `active`.
- **`email_subscribers`** *(new — built in **Phase 2**, not Phase 1)* — `email` (pk/unique), `status` (`pending` | `confirmed` | `unsubscribed` | `bounced` | `complained`), `confirm_token`, `unsub_token`, `subscribed_at`, `confirmed_at`. Double opt-in: created `pending` with a `confirm_token`; `/confirm` flips to `confirmed`. One-click unsubscribe via `unsub_token`. This is the **only genuinely live-written** state not already in Postgres, so it is the real migration — and it belongs with the subscribe box that writes it.
- **`pipeline_state`** *(deferred — see Scope correction)* — would consolidate `digest_state.json`, `telegram_state.json`, `scrape_status.json` into single-row-per-key (`key`, `value` jsonb, `updated_at`). **Not done now:** all three files are single-writer (CI-only), so there is no race to fix; migrating them is cosmetic until Phase 2's per-subscriber send ledger genuinely needs a store, at which point the digest send-state moves as part of that work.
- **`rate_limits`** *(deferred to **Phase 5**)* — `bucket` (e.g. `ask:{ip}`), `window_start`, `count`, plus a `bucket = 'ask:global:{date}'` row for the **global daily cap**. Built when `/ask` is hardened, since that is the only surface it protects.

Service-role key stays **server-side only** (FastAPI + CI); never shipped to the browser.

### Supabase Storage (cold storage)

- Raw article `.md` written **once** by the scraper to `articles/{lab}/{slug}.md` (S3-compatible; via `httpx`/PostgREST-storage or the storage REST endpoint — no new heavyweight dependency).
- `manifest.json` keeps lightweight metadata + a **pointer** (storage key) to each article object, instead of the `.md` living in git.
- **Backfill:** the existing ~291 `data/articles/*.md` are uploaded once; then removed from git tracking (repo slims; `.gitignore` updated). Git history retains them — no data loss.

### Stays JSON-in-git

`manifest.json` + nuggets (single-writer pipeline, read-only at runtime). Deferred to the later hybrid phase. Vector index (`chroma_db`) stays rebuilt-on-deploy.

## Surface hardening

### Email digest → production-grade
- Public **subscribe box** with **double opt-in** (confirmation email before any digest).
- **One-click unsubscribe** link (token) + compliant footer (physical postal address).
- **Deliverability:** custom domain with SPF / DKIM / DMARC via Resend (retire `onboarding@resend.dev`).
- **Idempotent sends:** a retried CI run cannot double-send (send-ledger keyed in `pipeline_state`).
- **Bounce / complaint handling:** Resend webhook (or poll) auto-suppresses `bounced` / `complained` addresses.
- **Consent + privacy** captured at the subscribe box (lands *with* this phase, not at the end).

### Telegram → production-grade
- **Webhook secret-token validation** already specified in the Telegram spec — confirm it is enforced (`X-Telegram-Bot-Api-Secret-Token` vs `TELEGRAM_WEBHOOK_SECRET`; unauth → 401 ignored).
- `/subscribe` (`/start`) + `/stop` writing to Postgres (exists).
- **Broadcast throttling with backoff** (Telegram ~30 msg/s cap) and **block/kick handling** (mark `active=false` on 403 so dead chats aren't retried forever).
- Best-effort per recipient: one failure never aborts the run (exists) — extend with structured per-recipient outcome logging.

## Reliability, cost & abuse

- **Pipeline robustness:** each stage idempotent and independently retryable; one lab's scrape failure does not abort the run; a **failed run alerts the operator** (pulled forward — see Phase 0). Partial-progress is recorded in `pipeline_state`.
- **`/ask` guardrails (secondary surface, but spends money):** per-IP fixed-window rate limit + a **global daily cap**; over the cap, degrade gracefully ("try again tomorrow") instead of billing. Prompt-injection exposure from scraped text remains a **known, accepted risk** (trusted lab sources only; documented in README Security).
- **Scraper politeness:** per-host rate/backoff so a CI runner IP is not banned.

## Observability & ops

- **Structured logging** across the web app and pipeline.
- **Sentry** (or equivalent) for error tracking on FastAPI + the CI pipeline.
- **Health check** endpoint + external uptime monitor.
- **Minimal dashboard:** last pipeline run status, per-surface counts (subscribers, sends), `/ask` volume, and daily spend vs cap.
- **Alerting:** pipeline failure, spend-cap hit, deliverability spike (bounces/complaints). Pipeline-failure alerting is a **launch prerequisite** (Phase 0).

## Security & legal

- Service-role key server-side only; no Supabase access from the browser.
- Webhook authenticated; `/ask` and subscribe endpoints rate-limited.
- **Privacy policy** + consent at the point of email capture (Phase 2).
- **ToS** + **GDPR data export/delete** for subscribers before public launch (Phase 7).
- Secrets in Render + GitHub Actions; none in git.

## Roadmap (phased — each phase independently shippable & revertible)

| Phase | Ships | Why here |
|---|---|---|
| **0 — Safety net** | **CI test gate** (`pytest` on every push/PR — currently missing) + wire the **Telegram broadcast outcome** into the existing `alert.py` health check | Cannot go public blind to breakage. NB: `alert.py` pipeline-failure alerting **already exists** and runs in `daily.yml`; the test gate does not. |
| ~~**1 — Postgres for all writable state**~~ **— dissolved (see Scope correction)** | `email_subscribers` folded into **Phase 2** (built with the subscribe box); `rate_limits` folded into **Phase 5** (built with `/ask` guardrails); `pipeline_state` migration **deferred** | Code review showed all three `*_state.json` files are **single-writer (CI-only) — no race**. Only the email list is genuinely live-written, and it doesn't exist yet, so it belongs with the surface that creates it. |
| **2 — Email digest hardened** | Double opt-in subscribe/confirm/unsubscribe, deliverability (domain + SPF/DKIM/DMARC), idempotent sends, bounce/complaint suppression, **+ privacy/consent** | First hero surface |
| **3 — Telegram hardened** | Enforce webhook auth, broadcast throttle + backoff, 403/block handling, per-recipient outcome logging | Second hero surface |
| **4 — Cold storage** | Article archive in Supabase Storage; manifest stores pointers; git slims; backfill ~291 articles | User's explicit early priority |
| **5 — `/ask` guardrails** | Per-IP rate limit + global daily spend cap, graceful degradation | Secondary surface, but it spends money |
| **6 — Observability** | Sentry, structured logs, health check, cost/run dashboard, alerts | Operate it for real |
| **7 — Launch readiness** | ToS, GDPR export/delete, final polish → **public launch** | Gate to open the doors |
| **Later — Hybrid migration** | Next.js + Supabase-served app + user accounts | **Deferred** until growth (>~200 users) demands it |

## Hard dependencies on the user

- Provide/confirm **Supabase** project details (URL + service key already in use for Telegram); run the new-table SQL (or approve me generating a migration).
- Provide a **sending domain** for Resend and complete DNS (SPF/DKIM/DMARC) for email deliverability.
- Confirm **Resend / Render / GitHub Actions** secrets as new env vars are introduced.
- Approve wording of **privacy policy / ToS** (I draft, user reviews — not legal advice).

## Open questions (defaults chosen; flag to change)

- **Rate-limit store:** Postgres `rate_limits` table (chosen) vs a hosted KV (Upstash Redis). Postgres avoids a new vendor at this scale; revisit if `/ask` volume grows.
- **Global `/ask` cap unit:** cap on **request count/day** (simple, chosen) vs estimated **dollar spend/day** (accurate, more work). Start with request-count; upgrade to spend-based in Phase 6 when the dashboard exists.
- **Bounce handling:** Resend **webhook** (real-time, chosen) vs periodic poll. Webhook if Resend plan supports it; poll fallback.
