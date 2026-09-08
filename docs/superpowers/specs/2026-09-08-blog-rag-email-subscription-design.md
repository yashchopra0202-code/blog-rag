# Email Subscription (Phase 2) — Design Spec

**Date:** 2026-09-08
**Status:** Approved design, pending spec review → implementation plan
**Repo:** `~/blog-rag` (FastAPI + RAG on Render, daily pipeline via GitHub Actions, Telegram bot + email digest)
**Parent:** `docs/superpowers/specs/2026-09-08-blog-rag-production-roadmap-design.md` (Phase 2)

## Goal

Turn the single-recipient email digest into a **public, double-opt-in email subscription**: anyone can subscribe from the landing page, confirm via email, receive the daily digest, and one-click unsubscribe — with bounce/complaint handling and basic abuse control. Build and harden the whole flow now; **public launch is gated on a verified sending domain (deferred)**, so until then the flow is exercised end-to-end only against the owner's own verified address.

## Decisions (locked with the user)

| Decision | Choice | Rationale |
|---|---|---|
| Sending domain | **Test-only for now** | Resend's sandbox sender (`onboarding@resend.dev`) can email only the account's own verified address. Build + test fully now; flip to a verified domain at go-live (a config change, no code change). |
| Idempotency | **Per-digest guard + global watermark** | A durable `sent_digests[<utc-date>]` record in Supabase makes a retried CI run non-double-send; the existing `last_sent` watermark still drives content selection. Right-sized for 100–200 users. |
| Bounce/complaint | **Resend webhook now** | A signature-verified `POST /resend/webhook` auto-suppresses bad addresses — protecting sender reputation from day one. |
| `/subscribe` abuse | **Light per-IP rate limit now** | `/subscribe` is the first public write endpoint; a fixed-window per-IP limit stops it being used to blast confirmation emails at strangers. Pulls a small slice of Phase 5's rate-limit system forward. |

## Non-goals (v1 / YAGNI)

- **No verified sending domain / DNS this phase** (deferred to go-live per "test-only").
- **No user accounts / login.** Subscription is by email address + tokens only; anonymous per the parent spec.
- **No per-subscriber send ledger.** A single per-digest guard is enough; we do not track per-recipient last-sent.
- **No preferences** (topic/lab/cadence per subscriber). One digest, everyone gets the same — matches the existing digest.
- **No migration of `manifest.json`/nuggets/`last_sent` off git.** Only the new subscription + guard + rate-limit state lives in Postgres.
- **No admin UI** for the subscriber list (query Supabase directly if needed).

## Key constraints (surfaced, not assumed)

1. **Resend sandbox can only email the account owner.** Sending to arbitrary public addresses REQUIRES a verified domain. Therefore public launch is blocked on DNS; the code must work unchanged whether `DIGEST_FROM` is the sandbox sender or a domain sender.
2. **`/subscribe` is the first public unauthenticated write endpoint.** Double opt-in prevents unwanted digests, but a POST with a stranger's address still sends *them* a confirmation email — so (a) the confirmation copy must be gentle ("someone subscribed this address; ignore if it wasn't you"), and (b) `/subscribe` is rate-limited per IP.
3. **The digest send runs in CI (single writer), but must be idempotent across retries.** Git-committed state only persists at end-of-run, so the "already sent today" guard must be written **synchronously at send time** → Supabase, not `digest_state.json`.
4. **Supabase `service_role` needs explicit table grants.** New keys don't auto-grant; every new table needs `grant select,insert,update,delete on public.<table> to service_role;` (the 403 trap the Telegram table hit).
5. **CAN-SPAM:** the public digest needs a physical postal address in the footer + a working unsubscribe. Address is env-configurable and **required before public launch** (deferred with the domain).
6. **Existing pattern to follow:** `store.py` reaches Supabase via PostgREST over `httpx` (service-role key, server-side only, no `supabase-py`); `telegram_digest.py` already does best-effort per-recipient broadcast — the email send mirrors it.

## Architecture

```
  Visitor → static/index.html [subscribe box] ──POST /subscribe──┐
                                                                  ▼
  api.py:  POST /subscribe        validate email + per-IP rate limit → upsert pending + token
                                  → emailer.send_email(confirmation) → generic 200
           GET  /confirm?token    pending → confirmed
           GET  /unsubscribe?token → unsubscribed
           POST /resend/webhook   Svix-signature verify (fail-closed) → mark bounced/complained
                    │                         │
                    ▼                         ▼
             emailer.py (Resend)         store.py ──PostgREST/httpx──► SUPABASE
        confirmation + welcome +           email_subscribers · rate_limits · sent_digests
        the daily digest send              (telegram_subscribers already exists)

  GitHub Actions (daily) → digest.py:
     if not sent_digests[<utc-date>]:                       # durable guard (Supabase)
         entries = curate(select_new_entries(...))          # unchanged selection, last_sent watermark (git)
         for sub in store.confirmed_email_subscribers():    # best-effort per recipient
             emailer.send_email(sub.email, subject, html + unsubscribe_footer(sub.unsub_token))
         store.mark_digest_sent(<utc-date>)                 # write guard AFTER a successful send pass
     # DIGEST_TO owner-fallback when there are no confirmed subscribers yet
```

## Data model (Supabase — `store.py` helpers)

**`email_subscribers`**

| column | type | notes |
|---|---|---|
| `email` | `text` primary key | lowercased/normalized |
| `status` | `text` | `pending` \| `confirmed` \| `unsubscribed` \| `bounced` \| `complained` |
| `confirm_token` | `text` | `secrets.token_urlsafe(32)`; used by `/confirm` |
| `unsub_token` | `text` | stable; used by `/unsubscribe` and the footer link |
| `subscribed_at` | `timestamptz default now()` | |
| `confirmed_at` | `timestamptz` | set on confirm; nullable |

**`rate_limits`** — `bucket` (text pk, e.g. `subscribe:<ip>:<YYYY-MM-DD-HH>`), `count` (int), `window_start` (timestamptz). Fixed-window counter; a helper increments and returns whether the limit is exceeded.

**`sent_digests`** — `digest_key` (text pk = UTC date `YYYY-MM-DD`), `sent_at` (timestamptz). Presence = "already sent today".

All reached via PostgREST + `httpx` with the service-role key. Each table needs the `service_role` grant (constraint 4).

## Components (files)

- **`emailer.py`** (new) — `send_email(to, subject, html, attachments=None, api_key=None, sender=None) -> dict`: the Resend HTTP call (moved out of `digest.send_digest`), plus `confirmation_email(confirm_url)` and `welcome`/footer HTML builders kept small and pure where possible. Unit-tested with monkeypatched `httpx` (same pattern as `test_digest.py`).
- **`store.py`** (extend) — new helpers, grouped by table:
  - Email: `add_email_subscriber(email) -> {status, confirm_token}` (upsert `pending`, `merge-duplicates`), `confirm_email(token) -> bool`, `unsubscribe_email(token) -> bool`, `confirmed_email_subscribers() -> [{email, unsub_token}]`, `mark_email_status(email, status)`.
  - Rate limit: `rate_limit_ok(bucket, limit) -> bool` (increment fixed-window counter, return allowed?).
  - Digest guard: `digest_already_sent(key) -> bool`, `mark_digest_sent(key)`.
  - Grouped with clear section comments; if the file grows unwieldy, flag a split (e.g. `email_store.py`) rather than doing it silently.
- **`api.py`** (extend) — `POST /subscribe`, `GET /confirm`, `GET /unsubscribe`, `POST /resend/webhook`. Endpoints thin: validate → call `store`/`emailer` → return. `/confirm` and `/unsubscribe` return small styled HTML pages (reuse the site's palette).
- **`digest.py`** (change) — `send_digest` delegates the Resend call to `emailer.send_email`; `main()` iterates `confirmed_email_subscribers()` (best-effort per recipient), guarded by `sent_digests`, appends a per-subscriber unsubscribe footer (unsub link built from `FEED_URL` + `unsub_token`), and falls back to `DIGEST_TO` when there are no confirmed subscribers. `telegram_digest.py`'s reuse of `digest.load_state` is unaffected.
- **`static/index.html`** (extend) — a subscribe box (email field + button → `POST /subscribe`) matching the Bricolage/Hanken + green system, with inline success/error text. Built with the impeccable skill's conventions (no restyle of the page).

## Email validation

Format validation only (a well-formed address per a conservative regex / `email.utils.parseaddr` sanity check), normalized to lowercase. No MX/deliverability probing (that's what double opt-in + bounce handling are for).

## Security

- **Webhook:** verify the Resend/Svix signature (`svix-id` + `svix-timestamp` + `svix-signature`, HMAC-SHA256 over `{id}.{timestamp}.{body}` with `RESEND_WEBHOOK_SECRET`), **fail-closed** (missing/invalid secret → 401), constant-time compare — same discipline as the Telegram webhook.
- **No enumeration:** `/subscribe` returns the same 200 whether the address is new, pending, or already confirmed.
- **Tokens:** `secrets.token_urlsafe(32)`, unguessable; `/confirm` and `/unsubscribe` act only on an exact token match.
- **Service-role key** stays server-side (API + CI); never shipped to the browser. New-table grants required.
- **Rate limit** on `/subscribe` (per IP) caps confirmation-email abuse.

## Testing (TDD)

Everything buildable green without live credentials, via monkeypatched `httpx`/`store`/`emailer` and FastAPI `TestClient`:

- `emailer.send_email`: builds the right Resend request; confirmation/footer HTML escapes correctly.
- `store` helpers: add/confirm/unsubscribe/list/mark build the right PostgREST requests and parse responses; `rate_limit_ok` allows under the limit and blocks over it within a window; digest-guard get/set.
- `POST /subscribe`: valid email → pending + confirmation send + generic 200; invalid email → 400/generic; over rate limit → limited; **no enumeration** (same response for new vs existing).
- `GET /confirm` / `GET /unsubscribe`: valid token flips status + returns 200 page; unknown token → benign page, no error leak.
- `POST /resend/webhook`: valid signature + bounce event → status marked; **missing/invalid signature → 401** (fail-closed); unknown event type ignored.
- `digest.main` send model: iterates confirmed subscribers, one failing recipient doesn't abort the rest, the `sent_digests` guard prevents a second send for the same day, unsubscribe footer present, `DIGEST_TO` fallback when no subscribers.

Real delivery is verifiable only to the owner's verified address until the domain lands.

## Rollout / phasing

1. **Build + unit/integration-test** the whole flow (store, emailer, endpoints, digest change, subscribe box) — all green with no live domain.
2. **Owner-only live test:** create the Supabase tables + grants; the owner subscribes with their own verified address → confirmation email → confirm → forced digest run delivers with a working unsubscribe → unsubscribe works; trigger a test bounce/complaint to verify the webhook marks status.
3. **Public go-live (later, gated):** verify a sending domain + DNS in Resend, set `DIGEST_FROM` to it, register the Resend webhook → `RESEND_WEBHOOK_SECRET`, set the postal-address env for the footer. No code change — configuration only.

## Hard dependencies on the user

- **Supabase:** create `email_subscribers`, `rate_limits`, `sent_digests` + run the `grant … to service_role` for each.
- **Go-live (deferred):** a verified Resend **sending domain** + DNS (SPF/DKIM/DMARC); a **Resend webhook** registered at `/resend/webhook` → provides `RESEND_WEBHOOK_SECRET`; a **physical postal address** for the footer (`DIGEST_POSTAL_ADDRESS` env).
- Set the new env vars on **Render** (runtime: webhook secret, postal address, base URL) and **GitHub Actions** (digest send already has Resend + Supabase secrets).

## Open questions (defaults chosen; flag to change)

- **Unsubscribe method:** `GET /unsubscribe?token=` (chosen — one-click from the email footer). A confirmation-click page could be added if one-click accidental unsubscribes become a problem; not expected at this scale.
- **Rate-limit window/limit:** default **5 subscribe attempts / IP / hour** (fixed window). Tunable; revisit at go-live.
- **Confirm-page UX:** a minimal styled HTML page (chosen) vs. redirect to `/?confirmed=1`. Page is simpler and needs no landing-page state handling.
