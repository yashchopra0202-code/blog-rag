---
url: https://x.ai/news/grok-build-memory
title: Memory in Grok Build
site: xai
date: 2026-09-16
scraped_at: 2026-09-17T09:02:47+00:00
---

Grok Build now carries conventions, decisions, and project facts from one session to the next. Notes are written in the background as you work and read back when you return to the project.

Grok Build now has memory. As you work, it keeps notes on the conventions, decisions, and project facts that come up, and later sessions read those notes before touching related code. Grok Build gets better the more you use it.

After a turn completes, Grok reviews it in the background and records anything durable: conventions, decisions, and project facts. Capture runs on every completed turn and does not interrupt the session.

Notes are markdown files, one topic per subject. Each project has its own workspace scope, and a global scope holds preferences that apply everywhere.

merges new observations into the topic they belong to, and

shows the files as they are on disk.

Before starting related work, Grok reads the topics that cover the area and applies them, including in sessions where the subject never comes up. Instructions in the current conversation take precedence over anything in a note.

After a turn completes, Grok reviews it in the background and records anything durable: conventions, decisions, and project facts. Capture runs on every completed turn and does not interrupt the session.

Memory holds the details most likely to matter in a later session: how the team writes and reviews code, decisions and the reasoning behind them, and durable facts about the project, from where a subsystem lives to which command runs the suite. Task state, tentative conclusions, secrets, and anything the repository or its docs already cover are left out.

Notes are kept per project, plus a global set for preferences that apply everywhere.

Capture runs after a turn completes and never blocks the session. Grok reviews the finished turn, writes anything worth keeping as a markdown note, and continues. Over time,

folds those notes into topic files, one per subject, so each project ends up with a small set of organized references.

When you return to a project, Grok reads the topics that cover the area it is about to work in. Instructions in the current conversation take precedence over anything in a note.

opens a read-only browser of every memory file, grouped by scope, with a preview of the selected file. It is the fastest way to see what a session produced, and to find the file to edit when a note is wrong.

Memory is available in Grok Build now. It applies to new sessions: run

or start a fresh

, and notes begin after the first completed turn.
