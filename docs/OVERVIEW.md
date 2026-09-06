# blog-rag — Overview

*Written in Simplified Technical English: short sentences, plain words, one idea at a time.*

## What it is (in one line)

**blog-rag reads 18 AI-company blogs for you, writes a short summary of each new post, and lets you read and search them in three places: a web page, a daily email, and a Telegram bot.**

Live site: https://blog-rag.onrender.com
Telegram bot: **@JiGyasaaBOT**

## Words you need first

- **Article** — one blog post.
- **Nugget** — a 2–3 sentence summary of one article. Claude writes it.
- **Signal** — a score from 1 to 5. It says how important a post is.
- **Embedding** — text turned into numbers. Close numbers mean close meaning.
- **Index** — the store of all those numbers. We search it.
- **Digest** — the daily email (or Telegram message) of top nuggets.
- **Deploy** — to put the app on the internet.
- **Bot** — a program you chat with inside Telegram.
- **Webhook** — a web address the bot calls when a message arrives. It is a push, not a poll.
- **Subscriber** — a person who sent `/start` to the bot. Only they get the daily message.

## The whole flow, step by step

The system runs **once a day, on its own**. No laptop is needed.

1. A timer starts the job at 13:00 UTC. (GitHub Actions runs the timer.)
2. The scraper visits the 18 blogs. It saves each new article as a text file.
3. The nuggetizer sends each new article to Claude. Claude returns a nugget, a topic, and a signal score.
4. The digest picks the best new nuggets. It emails them to you.
5. `config.json` decides two things here: which labs to include, and daily or weekly.
6. The digest also sends a Telegram message to every subscriber. The same top nuggets, in the chat.
7. The job saves the new data back to GitHub.
8. That save wakes up Render. Render rebuilds the index and updates the live web page.
9. You read the news in any of three places: the web page, the email, or Telegram. On the web or in Telegram you can also ask a question.

**When you ask a question, three tools work together:**

1. Voyage turns your question into numbers.
2. Chroma finds the article chunks with the closest numbers.
3. Claude reads only those chunks and writes the answer.

This method is called **RAG** (Retrieval-Augmented Generation). "Retrieval" = find the right text first. "Generation" = the model writes the answer from that text. This stops the model from guessing.

**The Telegram bot uses the same brain.** When you message @JiGyasaaBOT, Telegram sends the text to the app's `/telegram/webhook` address. The app runs the same RAG steps and sends the answer back. `/start` makes you a subscriber; `/stop` removes you; `/latest` lists this week's posts. A bot can only message people who wrote to it first, so every subscriber opted in.

## The technology, and why we chose each

| Tool | What it does | Why we use it |
|---|---|---|
| **Python** | The language for all parts | One language for scraping, AI, and the web app |
| **Scrapling** | Fetches web pages; gets past bot blocks | The lab sites use JavaScript and block simple bots |
| **Voyage** (`voyage-3.5`) | Makes embeddings (text → numbers) | Good, low-cost search by meaning |
| **Chroma** | Stores the numbers; finds close matches | Simple, runs on disk, needs no separate server |
| **Claude Haiku 4.5** | Writes nuggets; answers questions | Fast and cheap for many small jobs |
| **LangChain** | Connects Voyage, Chroma, and Claude | Less code to join the three |
| **FastAPI + Uvicorn** | The web server (feed + search) | Fast and simple in Python |
| **Resend** | Sends the daily email | A simple email service |
| **Telegram Bot API** | The chat surface (Q&A + daily message) | People already use Telegram; a bot needs no app to install |
| **Supabase** (Postgres) | Stores who subscribed to the bot | A managed database; we call it over plain HTTP, no extra library |
| **GitHub Actions** | Runs the daily job on a timer | Free scheduler, tied to the code |
| **Render** | Hosts the web app on the internet | Auto-deploys from Git; has a free plan |
| **Git / GitHub** | Stores the code and the data | It is also the hand-off between the two systems |

## What we built (2026-09-06)

Two big additions after go-live: a Telegram bot and a rebuilt front page.

**Telegram bot — @JiGyasaaBOT (live)**
- Before: you could only read the news on the web page or in the email.
- Now: you chat with the bot. Ask any question and it answers with sources. Send `/latest` to see this week's posts. Send `/start` to get the daily message; `/stop` to stop.
- The bot uses the same RAG brain as the web page. No second copy of the logic.
- Who gets the daily message is stored in Supabase. Only people who sent `/start` are on the list — a bot cannot message a stranger.
- The bot talks to the app through a **webhook**, guarded by a secret so only Telegram can call it.
- We built this test-first, one small piece at a time, and reviewed every piece.

**Landing page rebuilt — search first**
- Before: the blog feed was at the top, and the "ask a question" box was hidden at the bottom. Most people never saw that the tool could answer questions.
- Now: the question box is the first thing you see, in the middle of the page. A short guided tour points out what to do the first time you visit. The blog feed sits beside the search, not on top of it.
- Same calm colours, same light/dark mode as before.

**Small fix — `/latest` was all one lab**
- The `/latest` list showed only NVIDIA, because NVIDIA had just published a block of posts and they filled the whole list.
- Fix: cap each lab at 2 posts in the list, so no single busy lab can crowd out the others.

## What we built (2026-09-05)

We finished the last two items on the plan.

**#4 — Controls (`config.json`)**
- Before: to change labs or timing, you had to edit code.
- Now: you edit one file, `config.json`. You choose the labs. You choose daily or weekly.
- The scraper skips labs you turn off. The digest sends only on the day you set.
- We wrote the code test-first. 11 new tests pass.

**#5 — Hosting (Render)**
- Before: the app ran only on your laptop. The email link pointed to your own computer. No one else could open it.
- Now: the app runs on the internet at https://blog-rag.onrender.com. Anyone with the link can use it.
- The daily job and the website share the GitHub repo. So the site updates itself every day.

## Why this matters

- **It runs by itself.** You do not open your laptop. The job runs every day.
- **Other people can use it.** The app is now public.
- **Three ways to read it.** Web page, email, and now a Telegram bot — people use whichever they already open.
- **The bot answers, not just broadcasts.** The same RAG brain works inside the chat, with sources.
- **You control it without code.** One file changes the labs and the timing.
- **The answers are trustworthy.** RAG makes Claude answer from real articles, not from memory.

## The key design idea

**Git is the glue.** GitHub Actions writes fresh data into the repo. Render reads that same repo to update the site. The two halves never talk to each other directly. This is why we need no database and no shared disk — a simpler, more reliable design.
