# Telegram Integration — Design Spec

**Date:** 2026-09-06
**Status:** Approved design, pending spec review → implementation plan
**Repo:** `~/blog-rag` (FastAPI + RAG, hosted on Render, daily digest via GitHub Actions)

## Goal

Let people use blog-rag from Telegram: (1) **ask questions and browse articles** inside a Telegram chat (a second front-end onto the existing RAG), and (2) **receive the daily digest** pushed to them on Telegram (a second delivery channel alongside email).

## Non-goals (v1 / YAGNI)

- No rich inline-keyboard menus, per-user topic preferences, or usage analytics.
- No cold-messaging: only users who have started the bot are reachable (Telegram anti-spam law — a constraint, not a choice).
- No replacement of the email digest; Telegram is additive.
- No migration of manifest/index storage; only subscribers move to a datastore.

## Key constraints (surfaced, not assumed)

1. **Telegram reachability = opt-in.** A bot can message a user only after that user has messaged the bot. Subscribers are people who send `/start`.
2. **The web app has no writable persistence today.** `manifest.json`/`digest_state.json` are written only by the daily CI job and committed to git; the Render web app's filesystem is ephemeral and wiped on redeploy. Subscriber chat IDs therefore need an external datastore.
3. **Render free tier sleeps after 15 min idle.** The first webhook after idle triggers a ~50s cold start. Telegram retries webhooks, so no message is lost, but the first reply after a quiet spell is slow. Acceptable for v1; Starter plan removes it.

## Architecture

One RAG brain, two front-ends and two delivery channels:

```
                         ┌───────────────────────────┐
  Telegram user ──msg──▶ │ FastAPI (Render)           │
                         │  POST /telegram/webhook    │──▶ rag_core (/ask logic)
                         │  GET  / , /ask , /feed …    │──▶ manifest / chroma_db
                         └────────────┬───────────────┘
                                      │ subscribe / unsubscribe
                                      ▼
                         ┌───────────────────────────┐
                         │ Supabase (Postgres)        │
                         │  telegram_subscribers      │
                         └────────────┬───────────────┘
                                      ▲ read subscribers
  GitHub Actions (daily) ─────────────┘
    scrape → nuggetize → email digest → TELEGRAM broadcast (cadence-gated)
```

## Data model (Supabase)

Table `telegram_subscribers`:

| column | type | notes |
|---|---|---|
| `chat_id` | `bigint` primary key | Telegram chat id |
| `first_name` | `text` | for a friendly greeting; nullable |
| `username` | `text` | nullable |
| `subscribed_at` | `timestamptz default now()` | |
| `active` | `boolean default true` | `/stop` sets false (soft delete, keeps history) |

Accessed from Python via **`httpx` against Supabase's PostgREST REST API** (`{SUPABASE_URL}/rest/v1/telegram_subscribers`) using the **service-role key** in an `apikey` + `Authorization: Bearer` header. No new dependency (`httpx` is already used). Upsert on `/start` (`Prefer: resolution=merge-duplicates`), patch `active=false` on `/stop`, `select` active rows for broadcast.

## Components (files)

- **`telegram.py`** — pure logic, no I/O: `parse_update(update) -> Intent` (start / stop / latest / question / ignore), and `format_answer(answer, sources) -> str` (Telegram HTML, truncated to 4096 chars, source links as `<a>`). Unit-tested with plain dicts.
- **`store.py`** — Supabase REST helpers: `add_subscriber(chat)`, `deactivate_subscriber(chat_id)`, `active_subscribers()`. `httpx` calls; unit-tested with a monkeypatched `httpx` (same pattern as `test_digest.py`).
- **`telegram_api.py`** — thin Telegram Bot API client: `send_message(token, chat_id, html)`, `set_webhook(...)`. `httpx`; unit-tested with fake post.
- **`api.py`** — add `POST /telegram/webhook`: verify the `X-Telegram-Bot-Api-Secret-Token` header against `TELEGRAM_WEBHOOK_SECRET`, parse the update, dispatch by intent (subscribe/unsubscribe via `store`, `/latest` via existing feed logic, question via the RAG), reply via `telegram_api`. Returns 200 quickly.
- **`telegram_digest.py`** — broadcast entry for CI: gate on `config.json` cadence (`digest.should_send_today`), build the digest entries (reuse `digest.select_new_entries`/`curate`), format a Telegram message (top-N nuggets + links), send to each `active_subscribers()`. Best-effort per recipient (one failure never aborts the run).
- **`scripts/set_telegram_webhook.py`** — one-time: register the webhook URL + secret with Telegram.
- **`.github/workflows/daily.yml`** — add a Telegram broadcast step after the email step (its own `continue-on-error`, same secret-gated pattern), passing the new env vars.

### RAG reuse

Factor the answer logic in `api.py` into a plain function `answer_question(question) -> {answer, sources}` that does **not** raise HTTP errors (returns a structured result / sentinel when the index is missing), so both `POST /ask` and the Telegram webhook call the same core. `POST /ask` keeps its HTTP wrapper.

## Bot behaviour (v1 commands)

- `/start` → greet, subscribe (upsert), explain: "Send me any question about what the AI labs are publishing, or /latest for recent posts. /stop to unsubscribe."
- `/stop` → deactivate, confirm.
- `/latest` → recent nuggets from the manifest (reuse `feed_data`), formatted with links.
- **any other text** → treat as a question → RAG → answer + source links.
- Unknown/empty/non-text → a short hint.

## Secrets & configuration

Env vars, set in **Render** (webhook/runtime) and **GitHub Actions** (broadcast):

- `TELEGRAM_BOT_TOKEN` — from @BotFather.
- `TELEGRAM_WEBHOOK_SECRET` — random string; sent by Telegram as a header, verified on every webhook call.
- `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` — service role key is **server-side only** (never shipped to the browser; the existing `static/index.html` never sees it).

## Security

- Webhook authenticated by the secret-token header; unauthenticated calls get 401 and are ignored.
- Service-role key confined to server (FastAPI + CI). No Supabase access from the client page.
- Reuse the existing `safeMarkdown`-style escaping when composing Telegram HTML so article/model text can't inject markup; prefer `parse_mode=HTML` with escaped content.
- No PII beyond Telegram-provided chat id / name; `/stop` honored.

## Testing (TDD)

Pure/unit-testable without live credentials:
- `parse_update`: each intent from representative update payloads; ignores non-message updates.
- `format_answer`: escapes, truncates at 4096, renders source links.
- `store`: add/deactivate/list build the right requests and parse responses (monkeypatched `httpx`).
- `telegram_api.send_message` / webhook secret check.
- `telegram_digest`: cadence gate, message assembly, per-recipient best-effort (one failure doesn't stop the rest).

Everything above is buildable and green **before** any real token exists.

## Rollout / phasing

1. **Phase 1 — Q&A bot.** Build + unit-test `telegram.py`, `store.py`, `telegram_api.py`, the webhook, RAG refactor. Then (needs user) create the bot via @BotFather, create the Supabase project + table, set env vars on Render, register the webhook. Verify: message the bot → subscribed + real answer with sources.
2. **Phase 2 — Broadcast.** Build + unit-test `telegram_digest.py`, wire the CI step, add secrets to GitHub Actions. Verify: force a run → subscribers receive the digest.

## Hard dependencies on the user

- Create the bot via **@BotFather**, provide `TELEGRAM_BOT_TOKEN`.
- Create a **Supabase** project, run the `telegram_subscribers` table SQL, provide `SUPABASE_URL` + service key.
- (I set env vars / GitHub secrets and register the webhook once the values exist.)

## Open questions

- Broadcast format: one message with the top 5 nuggets + a "more on the web" link, vs. several messages. Default: **one message, top 5 + link** (respects the 4096-char limit, least noisy).
- Should `/latest` paginate? v1: first ~10, no pagination.
