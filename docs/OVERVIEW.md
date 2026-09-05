# blog-rag — Overview

*Written in Simplified Technical English: short sentences, plain words, one idea at a time.*

## What it is (in one line)

**blog-rag reads 18 AI-company blogs for you, writes a short summary of each new post, emails you the best ones each day, and lets you search all of them by meaning on a web page.**

Live site: https://blog-rag.onrender.com

## Words you need first

- **Article** — one blog post.
- **Nugget** — a 2–3 sentence summary of one article. Claude writes it.
- **Signal** — a score from 1 to 5. It says how important a post is.
- **Embedding** — text turned into numbers. Close numbers mean close meaning.
- **Index** — the store of all those numbers. We search it.
- **Digest** — the daily email of top nuggets.
- **Deploy** — to put the app on the internet.

## The whole flow, step by step

The system runs **once a day, on its own**. No laptop is needed.

1. A timer starts the job at 13:00 UTC. (GitHub Actions runs the timer.)
2. The scraper visits the 18 blogs. It saves each new article as a text file.
3. The nuggetizer sends each new article to Claude. Claude returns a nugget, a topic, and a signal score.
4. The digest picks the best new nuggets. It emails them to you.
5. `config.json` decides two things here: which labs to include, and daily or weekly.
6. The job saves the new data back to GitHub.
7. That save wakes up Render. Render rebuilds the index and updates the live web page.
8. You open the web page. You read the feed, or you ask a question.

**When you ask a question, three tools work together:**

1. Voyage turns your question into numbers.
2. Chroma finds the article chunks with the closest numbers.
3. Claude reads only those chunks and writes the answer.

This method is called **RAG** (Retrieval-Augmented Generation). "Retrieval" = find the right text first. "Generation" = the model writes the answer from that text. This stops the model from guessing.

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
| **GitHub Actions** | Runs the daily job on a timer | Free scheduler, tied to the code |
| **Render** | Hosts the web app on the internet | Auto-deploys from Git; has a free plan |
| **Git / GitHub** | Stores the code and the data | It is also the hand-off between the two systems |

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
- **You control it without code.** One file changes the labs and the timing.
- **The email works for real readers.** The "open the feed" link now points to the live site.
- **The answers are trustworthy.** RAG makes Claude answer from real articles, not from memory.

## The key design idea

**Git is the glue.** GitHub Actions writes fresh data into the repo. Render reads that same repo to update the site. The two halves never talk to each other directly. This is why we need no database and no shared disk — a simpler, more reliable design.
