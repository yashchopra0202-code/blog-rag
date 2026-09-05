---
url: https://huggingface.co/blog/funes
title: https://huggingface.co/blog/funes
site: huggingface
date: 2026-09-03
scraped_at: 2026-09-05T05:08:07+00:00
---

Earlier this year,

made the case
that coding agents already produce the record we keep losing. As they search a
codebase, try approaches, hit errors, read documentation, and change direction, they
leave behind a dense account of not just

changed, but

While the diagnosis is correct, traces are only potential memory. The session logs of
an agent are still just an archive. You cannot

your way to

across ten thousand turns. For an agent to use those traces
while it works, they need indexing, retrieval, ranking, and exact provenance.

That is what

provides. It is a durable
memory layer for your agents (Claude Code, Codex, pi, and Hermes). It is built from the
sessions already on your machine. It works locally and becomes part of your agent's
normal workflow with one command. When you want it to, it can also travel to a Hugging
Face dataset you own, private by default.

funes is a single binary. Its default inference backend has no ML runtime dependency,
and embedding and reranking happen

. Install it:

Then add it to an agent:

That one

command builds the first index, gives the agent

and

tools, and installs the automation that indexes each completed turn. Indexing is
incremental, with new runs adding new turns rather than embedding the whole history
 again. The older and deeper content can backfill in bounded steps.

From there, you just work. When a task touches a past decision, rationale, or finding,
the agent can reach for

itself. You do not need to remember the old session or
paste its context into the new one.

With funes added, recall happens inside the conversation. The agent reaches for its
memory on its own and names the session behind its answer.

returns the original text, not a summary, and shows exactly where it came from
(the agent, timestamp, session, and turn). Each result includes a

command that
opens the full turn and its surrounding context.

Underneath, one deterministic pipeline parses every supported trace into the same
turn-and-block shape, chunks it, embeds it with a pinned local model, and writes it to
a local

dataset. A query combines vector and BM25 search, fuses their
rankings, reranks the candidates with a cross-encoder, reweights them by recency, and
attaches neighboring chunks.

That design gives funes three important properties:

The

problem is already solved on one machine. But memory gets
more useful when the next agent is running somewhere else.

To make a memory follow your work, bind one when you add funes to an agent:

The bind publishes your current memory there. funes then keeps it current, indexing
each turn locally and publishing at session boundaries. The agent recalls from it
throughout. Run the same command on another machine and the memory follows you there.

Underneath, the local memory is a Lance dataset, and the shared memory is a Hugging
Face dataset (private by default) you own.

Before anything reaches the Hub, credentials have already been redacted during
indexing. Publishing then scans every chunk again and withholds anything that still
looks like a secret. The scanner behind this is documented in

, including
what it does and doesn't cover.

When an agent reads a remote memory, funes caches the dataset files locally, so warm
queries return to local speed. The Hub supplies the ownership, access control,
versioning, and distribution it already supplies for other datasets. Your memory does
not become an account in a separate memory service, and you do not rent it back
through an API.

is shaped for agents. When you want to put a question to a memory yourself,
use

. It reads your local memory by default:

Or point it at a shared memory. We published a

of funes development,
so you can ask why funes works the way it does without creating a memory of your own:

is the read-only, one-question sibling of

. It recalls the
passages, hands them to a coding agent, and returns a grounded answer that names its
sources. It does not install an integration or change the agent's persistent setup.

A retrieval miss is not papered over. If the passages do not support an answer, the
agent says so. You can rephrase the question or add funes to the agent so it can search
the memory iteratively during normal work.

A shared memory is not tied to the agent or model that created it. Start a task in
Claude Code, continue it in Codex next week, and the second agent can recall the first
agent's reasoning. Use pi with a local model or one served through the Hugging Face
router, then return to Claude.

This matters in a few different scopes:

Published memories carry a dataset card and the funes tag, making them recognizable
and

. The Hub
already hosts open weights and datasets. funes adds open working memory. It holds
the decisions, failed approaches, and rationale behind a project, queryable by another
agent and traceable to the sessions that produced them.

A long investigation bloats a session until each turn costs more to carry the context
than to do the work. The usual answers are to let the agent compact and carry on, or to
write a handoff and start fresh. Recall is a third, so we measured them against each
other on the

:
two tasks whose answer cannot be reconstructed without the session prior knowledge.

Compaction is what most agents do by default, and it was the only one of the three whose
result divided: it arrived on one task and never arrived on the other. Where it failed,
its summary had flattened the findings that mattered. Recall returns the passages
themselves, so a finding does not have to survive summarization.

Recall was the cheapest of the three on both tasks, 8x cheaper than a written handoff on
one and 4x on the other.

— Jorge Luis Borges,

Your agents already wrote the record. funes lives at

, one command away
from turning that record into a memory the next agent can read, on whichever machine you
happen to be on.

funes invents little of this. It leans on open-source embedding models good enough to
run locally, on

's append-only datasets with
cheap incremental writes, and on the Hub's caching and content-dedup for datasets. The
work is in fitting them into a memory an agent can actually use.

funes is open source too.

for anything from an install snag to a recall that missed, or an agent you'd like
supported.

More Articles from our Blog

or

to comment
