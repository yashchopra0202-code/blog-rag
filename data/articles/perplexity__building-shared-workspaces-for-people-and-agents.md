---
url: https://www.perplexity.ai/hub/blog/building-shared-workspaces-for-people-and-agents
title: Building shared workspaces for people and agents
site: perplexity
date: 2026-10-12
scraped_at: 2026-10-14T09:11:10+00:00
---

How Perplexity Projects keep long-running work persistent, concurrent, and traceable.

We recently launched

, where people and agents work together on long-running tasks in Perplexity Computer. Each project sits on a shared workspace with a filesystem that accumulates context across sessions, agents, and users. Multiplayer collaboration that spans months requires persistence, concurrency, and traceability:

These challenges look familiar to software engineers. Git forges emerged decades ago to meet these requirements: a hosted service that wraps version control with collaborative features so that many contributors can converge on a single source of truth. The filesystem that powers Projects is one such Git forge built for human-agent and agent-agent collaborations.

Git already handles persistence, concurrency, and traceability. It identifies each file by its contents, so unchanged files are stored once and saved copies never go stale. Each commit saves every updated file at once, so collaborators never see a half-finished state. When two writers collide, the one who lost can re-apply its changes on the new version and try again. The chain of commits shows who changed what and makes it easy to restore earlier versions. What agents don't need is the rest of a forge built for humans, such as review screens, branch management, and notifications.

Our architecture runs the entire process on the cloud and supports all forms of knowledge work beyond coding. Every Computer project is backed by a Git repository served by 5 components:

Each agent has its own isolated sandbox. Inside that sandbox, it works with a local copy of the repository, managed by a small CLI. The CLI asks the control plane to locate the repository, then fetches and submits changes through the Git service. An agent proxy checks access for sandbox requests before they reach the Git service. The Git service reads and writes repositories on a shared filesystem, and decides whether each submission becomes the latest accepted commit. That filesystem is provided by AWS S3Files, which makes S3-backed storage accessible as ordinary files and directories. Storage is divided into isolated cells, each with its own filesystem and Git service replicas. After a commit is accepted, background workers extract text and other useful information from changed documents, storing the results separately from repository history and making them available when agents load or refresh the project.

Next, we walk through the components one at a time.

Agents run in

, our in-house sandbox platform. Each sandbox has a small CLI that materializes the repository and keeps it in sync. For each unit of meaningful work done by the agent, it submits the changes as a commit.

Agents typically only touch a small fraction of the project files, so it’s not necessary to materialize the entire repository upfront. As a result, the CLI materializes lazily: large and binary files stored through Git Large File Storage (LFS) arrive as small pointer files storing the object's real size, so the agent can use the name and size to decide whether or not a download is worth it. For documents such as PDFs, the agent reads parsed text first and only downloads the source files when necessary.

Another natural option would be to use a virtual filesystem. We tested a

-backed implementation, but it was roughly 400 times slower on filesystem-heavy workloads compared to local files, since every request requires a network roundtrip. It also typically requires privileged capabilities from the host, so every agent would need to run in a privileged sandbox.

The control plane locates where each repository is stored and issues access to it. When a repository is created, the control plane assigns it to a storage cell, an isolated unit of storage with its own Git service replicas. When an agent starts work on a project, the CLI asks the control plane where the repository is stored. The control plane returns the location and temporary credentials for the Git service. The control plane never reads or writes repository data. The Git service decides what enters a repository.

The Git service executes Git operations and transfers repository contents and version history between sandboxes and storage. It is a thin wrapper around Git’s own serving commands. It supports ref discovery for telling the client where the repository's head is,

for cloning and fetching, and

for receiving new objects and a request to advance the repository’s head. It also serves the Git LFS API: for large and binary files, it issues short-lived links so sandboxes can upload and download those files directly from S3.

We started with an off-the-shelf forge server, so we could prototype the agent and user interfaces in parallel with building our own lightweight forge, focused only on the Git operations we need.

The service consists of a fleet of replicas, each a running instance of the same server. A cell groups shared storage with a set of replicas and their supporting services. Replicas within a cell can then access the same shared filesystem, rather than maintaining independent copies of every repository.

This shared storage lets the replicas remain stateless. Any replica in the cell can serve any of its repositories, so replacing or adding replicas does not require moving repository data between servers. Requests for a repository normally go to the same replica to keep its caches useful, but the repository does not depend on that particular instance remaining available.

The acceptance step checks repository invariants to ensure an accepted commit is a valid repository state. We define an explicit contract for every repository, so mechanical checks can keep it from growing too large. Large and binary files such as PDFs and images are stored through Git LFS rather than as raw Git blobs. Compaction keeps recent history available while limiting the size of the repository. After a successful submit, the CLI asks the Git service whether the repository needs compaction. If the number of retained commits exceeds a threshold, the Git service keeps only a smaller set of the most recent commits. Older history is replaced with a single starting snapshot, and the recent commits are replayed to update the commit identifiers.

A simple synchronization step controls for concurrent writers. It tracks the latest accepted commit, or head. When it receives a submission, it accepts only if the submit was built on that head. If not, it sends a structured stale-base response; the loser then needs to replay its change on top of the new head and resubmit. This design ensures that concurrent agents don’t silently overwrite each other, without causing significant slowdowns. In our production workflows, fewer than 2% of submits are rejected as stale. Overall, median submit latency is under 1.7 seconds, and p99 latency is under 8 seconds.

The Git service also records every accepted change. For each accepted write, it adds an entry to an outbox, a log that lists the repository, the new commit, the user who made the change, and the paths that changed. Downstream services such as the parser read this log to find new work.

Together, these pieces form a repository management layer, without the parts agents don't need. Pull requests are unnecessary, because no human reviews each change. Instead, the Git service checks the contract at submit time, the agent that loses a race re-applies its own change, and the commit history records who changed what. Deterministic checks keep each repository within its contract, instead of relying on a human operator to manage growth.

The storage layer durably saves repository data independently of the sandboxes and Git service replicas. Repositories live on AWS S3Files, which exposes S3-backed storage through a filesystem interface that stock Git can use without modification. Each is a bare Git repository on the shared filesystem, containing the repository’s objects and references rather than a working checkout.

Decoupling storage and compute lets sandboxes remain ephemeral. Each agent gets its own sandbox, and many agents can work on the same project without sharing a machine. If a sandbox crashes, only work that has not been submitted is at risk.

We could instead give each project a long-lived sandbox that all its agents share, so the project’s files would live on that machine’s disk. However, this would tie the agents’ compute to wherever the machine runs and require it to be sized for its busiest periods. It would also need to remain healthy for months, with backups and recovery managed as part of the project’s storage system.

The primary downstream component is a parser pipeline that extracts text and metadata from newly added or updated documents to make the project files easily readable by agents. A parser worker consumes updates from the change stream queue, derives the changed files from the commit metadata, and fetches the raw bytes using the content hash. It then parses the document to produce the extracted text and document metadata.

Parsed outputs live outside the repository, in a store keyed by the source document’s hash. These artifacts are never committed back to the repository, since that would unnecessarily pollute history and increase the number of concurrent writes. Instead, the parsed outputs reach a sandbox through checkout and sync. Each checkout carries a reserved directory that the CLI uses for artifact materialization. Parsing happens asynchronously, so a background parser worker doesn’t block checkouts.

Agents explore the repository version loaded into the sandbox using standard filesystem tools. Rather than following a fixed search-then-read pipeline, they list folders, search file contents with

, read relevant passages, and use what they find to decide where to look next.

Similar to Computer, Search uses the same approach through its standard file tools. A separate exploration agent searches the project within a more limited budget and returns relevant file paths and supporting excerpts. The answering model then reads the selected files and generates the answer. Reusing an existing project sandbox reduces setup time: attaching to a warm checkout takes about 2.9 seconds, compared with roughly 8 seconds for a cold start.

Parsed text makes larger documents such as PDFs and Office files searchable with the same tools. The agent first checks a manifest, a list showing which documents have extracted text available, then searches and reads that text as ordinary files. It downloads the original document only when text is insufficient, for example, to inspect figures, layout, or embedded data.

We benchmarked this approach against semantic search over an index on 150 single-document financial questions over the same corpus. The exploration agent scored 0.867 on retrieving the correct document and 0.627 on answering correctly, against roughly 0.39 and 0.37 for semantic search, about 1.7x better on answers and 2x better on retrieval, at about 25% lower latency. The exploration agent works mostly with extracted text and rarely downloads the original PDFs.

Computer’s persistent memory uses the same filesystem infrastructure. Perplexity

, Computer’s knowledge wiki, stores memory in knowledge repositories with their own history and policies. Keeping knowledge separate from project files means background memory updates do not compete with edits to those files. A session that needs both loads both repositories.

Background agents read existing knowledge, incorporate new information, and save updated pages as commits. Other agents read those pages with ordinary file tools, and people can edit them too. Writers share their work through the repository rather than coordinating directly with each reader. Commit history records who changed what, while the outbox reports accepted updates to downstream services. People and agents can build on each other’s work, with a record of how the knowledge evolved.

When people and agents share a project, the workspace does more than store files. It provides a common place to combine contributions and track what changed. Git already supplies much of that foundation. We add coordination and automated checks so agents can submit work without a person approving each update. The result is a forge stripped to its essentials, as cross-agent collaboration and multi-contributor software development are the same problem underneath.

Agents work in independent, temporary sandboxes while contributing to durable repositories. Repository limits keep growth manageable, explicit downloads let agents choose what to fetch, and ordinary files let them explore with familiar tools. Background updates, interactive edits, and scheduled tasks can build on each other’s work without coordinating directly.

As more agents work autonomously inside Projects, their shared workspace must remain reliable and understandable to people. The goal is straightforward: each change should be more durable than the agent that produced it, become available to the next collaborator, and leave a clear record of what changed.
