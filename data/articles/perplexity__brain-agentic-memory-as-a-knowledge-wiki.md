---
url: https://www.perplexity.ai/hub/blog/brain-agentic-memory-as-a-knowledge-wiki
title: Brain: Agentic Memory as a Knowledge Wiki
site: perplexity
date: 2026-08-19
scraped_at: 2026-09-04T21:15:45+00:00
---

A structured, traceable, self-improving Markdown filesystem, compiled offline and navigated on demand.

Contents

Computer users do work that spans months and hundreds of sessions. By the tenth session, the system should be far more productive than in the first. It should accumulate context on the user, their preferences, and the work that has already been done.

For example, when asked to draw a diagram of a workflow the user previously explained, Computer should recall the details and use them to create and output a figure in the user's preferred style. The user shouldn't need to re-explain the details of the workflow or reiterate their preference for PDF over PNG artifacts; the system should be able to accurately recover that context from past sessions and apply it automatically.

Memory is the foundation of continual agent improvement. An effective memory system should be structured, traceable, and adaptable, enabling agents to search at the right breadth and depth for each task while grounding every decision in the most current information.

Imbuing agents with relevant context is a multifaceted problem. First, agents need to know what exists and how to access it. Second, when they find a helpful piece of information, they need to be certain that it's complete, accurate, and up-to-date. An isolated fact is of limited value unless the agent can find related information, verify that it comes from a trusted source, and ensure that it doesn't need to be updated with a more recent observation.

Stuffing static memory files directly into model context maximizes accessibility to agents, but presents a classic precision-recall tradeoff. Too much information will saturate the agent's context window with items of increasingly minor relevance, while too little will degrade answer quality due to a lack of relevant context. In contrast, on-demand access to external databases is more flexible, but shifts the burden of navigation onto the agent. Vector databases often store disconnected fragments, and graph databases require agents to know how to query effectively.

Recently,

, a core component of Computer's memory system that delivers the best of both worlds. Brain is a structured knowledge wiki that sits on top of static memory files and evidence. Citations link assertions to their sources, and related pieces of information are connected laterally. The organized wiki makes context navigable on demand, while detailed artifacts are retained in the layer beneath it.

Brain connects to a comprehensive memory system with three key components: durable memory storage, foreground agents that use memory to answer queries, and background agents that update and improve memory. The following figure depicts these components situated within Brain's overall system architecture.

In this article, we describe each layer in depth, explaining how Brain organizes memory, how agents use it, and how background processes keep it up to date. We also present results from internal evaluations that validate Brain's design, demonstrating that it improves agent performance at lower cost.

Memory needs a representation that scales to a user's full history without forcing every piece of context into the prompt. Computer's memory system represents persistent context as a filesystem. Brain synthesizes knowledge across raw sources, connecting related subjects and connecting claims back to the sessions and files that support them. This structure, detailed below, allows us to organize memory in a particularly well-suited form for agents.

Computer sessions already live in a sandbox with a filesystem, a shell, and I/O utilities. In designing Brain, we wanted to introduce as little new machinery as possible in the interface between the model and agent memory. This is why we built Brain atop a filesystem-native context layer. Memory is materialized as files in the sandbox under a

directory, and the agent simply uses the same tools on memory files that it already uses on everything else.

At the root of the memory tree sit three top-level directories that maintain context at varying levels of abstraction.

is the Brain itself, a synthesized knowledge wiki that links entities, concepts, active projects, and past learnings;

contains distilled snippets organized as topical folders; and

holds indexes, summaries, and full transcripts as the raw histories. The figure below shows a simplified view of the layout.

The surfaces are deliberately redundant. For simple, single-hop questions, it's often enough to search for snippets within

for a key word, while the

layer is most useful for questions that require stitching evidence across weeks or months of Computer sessions.

Brain is formatted as an

, a system of linked Markdown files. This form of lightly structured Markdown provides a holistic view of existing context, so that agents can easily understand what records are available, how they relate, and where to find them. Each page is a maintained view of one subject; it should remain useful when read alone while making further exploration easy through links.

Links come in two types.

are context edges. They connect pages laterally; a project may link to its owner, its client, or the concepts it depends on. Following them answers "what else do I need to know?"

references are evidence edges. They connect claims downward to the raw sessions or connector sources that support them. Following them answers "how do I know this is true?"

The figures below depict what a portion of Brain would look like for a synthetic persona, an accessibility researcher named Nadia. Her Brain includes a page on a sample project, a universal design sprint in Japan, synthesizing knowledge from sessions and connectors. The graph view demonstrates how the context and evidence edges present in the page link related entities and sources.

Brain is Git-backed to preserve version history, supporting its constantly evolving nature. Pages can be edited over time, while changelogs record key updates and allow agents to easily inspect past versions and diffs. This also supports agentic coordination, which is critical as multiple agents may be using and updating Brain at once.

When answering a user query, agents need to be able to find the right context at the right level of detail. Brain's structure makes it easy for agents to explore memory. Agents can choose between actionable steps such as following context links to find related information, following evidence links to verify claims, or calling a subagent to obtain and synthesize additional context. We steer the agentic exploration process in a number of ways aimed at maximizing agents' ease of access to relevant information.

We include a compact index of Brain within the initial user message, so the agent starts with working knowledge of what already exists. The agent then interacts with Brain using familiar operations: reading specific items referenced by the index, using

to search across pages, following links and inspecting citations, comparing Git revisions, and descending into sessions or raw trajectories. The code block below depicts sample commands for a synthetic persona.

Agents explore this context through a self-directed loop, rather than a fixed pipeline. Therefore, the agent can continue searching until it is satisfied with the context found. The agent can also choose when to inspect citations and evidence to find or verify details. A minor matter of preference may be adopted directly from a single Brain page, while a consequential decision or a conflict between sources may justify following the citation and reading the original record. The graph-based structure lets the agent choose between concrete next steps, rather than searching aimlessly for related information.

For agentic exploration to work, the agent needs to have access to the whole

tree through the sandbox filesystem. Copying the whole tree locally every time a sandbox is booted is expensive and unnecessary, as the agent won't touch the vast majority of those files. Another option would be to use a remote filesystem, so agents can access any file without copying them locally. However, agents often perform thousands of filesystem operations in a single command; if each becomes a network request, the round-trip cost begins to dominate the exploration loop. In internal testing, simple

workloads over a remote FUSE-backed path were roughly 400 to 500 times slower than the equivalent operations over local files.

Instead, we build a local working set of materialized files, while the larger corpus remains behind a memory retrieval system. Computer preloads an initial map (taken from recent memories, sessions, summaries, and available knowledge) onto the sandbox when it boots. Computer agents have access to a Memory Agent, a subagent that can perform semantic search and load a new set of files. When needed context is absent, Computer can call the Memory Agent with a description of the required information. The Memory Agent searches across files, returning an immediate text synthesis and materializing the supporting records as files under the memory tree. In this way, the working set expands naturally and gradually over time, preserving stable paths and source relationships for evidence already present.

This design cleanly solves for the latency bottleneck. Storing relevant files locally ensures that the filesystem operations required for exploration remain fast, and batched retrieval allows the pool of materialized files to grow without requiring separate calls for each file or loading a large number of irrelevant files. The nested-agent design also gives Computer the benefits of agentic retrieval without requiring the main agent to search the full backend corpus directly every time, preserving its own context window for the highest value information.

Users are constantly learning from the work they do and conversations they have, so agentic memory needs to do the same. For Brain to remain useful, it should be a concise representation of the most important knowledge. New pages should be created for important new entities, new information should be added to the relevant Brain pages, and outdated context should be seasonably removed. For example, if a user's job changes, Brain should reflect that change; it should contain the user's new job and prioritize information related to their new responsibilities and projects.

Brain is maintained by background agents we call Dream. Dream agents run offline over file-based memory, synthesizing new information into Brain updates. We carefully defined the scope and behavior of Dream agents to efficiently carry out this task, along with Dream-specific guardrails to ensure Brain updates are consistent and accurate.

Dream agents run in sandboxes with access to the same filesystem and read-only tools that an interactive Computer session would have, but their sole goal is to improve context for future sessions. Each run begins from the Brain produced by earlier runs rather than rebuilding the user's context from scratch. It then uses that current Brain to orient itself and produces an updated Brain for future runs to use.

A Dream agent receives an environment and decides how to explore it, rather than receiving a fixed input flattened into one prompt. It can navigate file-based memory, use approved read-only connector tools to verify a piece of knowledge, and delegate bounded parts of the work to subagents, including the Memory Agent. The scope and responsibilities of the Dream agent are specified as a

.

Broadly, a Dream run consists of 4 phases:

To ensure that any updates to Brain are complete and consistent, agents write proposed state into a staged output tree. No permanent changes are made until the agent has made all of the updates it deems necessary. Coordinating those decisions in one agentic process makes it possible to update the graph as a whole rather than as unrelated pages.

Any changes must pass two types of verification checks. Deterministic validation checks ensure that pages are well-formed and meet objective criteria, such as required frontmatter and citation format. Semantic verification checks ensure that a proposed synthesis is supported by the gathered evidence and remains consistent with the rest of the graph. After the agent finishes successfully, a controlled synchronization step compares the staged output against the prior state and applies the changes to the repository. When a synchronization step completes, the final set of edits is inspectable through Git version history.

A useful memory system must preserve relevant evidence, surface it when needed, and help the agent convert that evidence into a correct answer. We therefore evaluate Brain at multiple levels: controlled offline ablations, continuous paired replay, and randomized production experiments.

Our primary offline evaluation uses an internal dataset of 640 questions across 44 synthetic personas. The personas reproduce production-derived patterns in session cadence, turn count, topic mix, and fact density, while containing no production query text to preserve user privacy. Each account is populated through the production memory pipeline, including memory extraction, conversation summaries, and Dream's compilation of the knowledge wiki. For each question, the correct answer is mechanically tied to specific evidence present in the account's history.

For example, for Nadia, the accessibility researcher synthetic persona introduced earlier, the dataset includes the question, "Which orgs am I meeting in Kyoto and Sendai?" The answer (Sora City Lab in Kyoto and Sapphir Mobility Coop in Sendai) appears directly on the corresponding Wiki page.

We compare the same questions and accounts with the compiled knowledge wiki enabled versus withheld. Other memory surfaces remain available in both conditions. This isolates the incremental contribution of Brain, rather than comparing memory against no memory. Overall, Brain increased answer correctness from 0.600 to 0.661, a gain of 6.1 percentage points, and evidence recall from 0.573 to 0.625, a gain of 5.2 percentage points. The effect was largest for questions about preferences (+10.2 pp), temporal reasoning (+8.6 pp), and extracting details from prior activity (+6.9 pp). On 84% of questions, the agent verifiably touched a source bound to the gold evidence.

We also ran matched Brain ablations on subsets of two public benchmarks. On LoCoMo, removing the wiki reduced answer correctness by 4.6 percentage points on average, over three runs with different models. On LongMemEval-S it produced no statistically significant change. This result is consistent with Brain's intended role. LongMemEval-S primarily tests recovery of facts from individual sessions, where the underlying transcripts provide a redundant path to the answer. LoCoMo places greater emphasis on evidence scattered across conversations, speakers, and dates, creating more opportunity for the wiki's cross-session synthesis to contribute.

Overall, with Brain enabled, the production agent achieved 0.91 answer correctness on LongMemEval-S and 0.83 on LoCoMo. Because these experiments used benchmark subsets, they are not definitive benchmark results. However, the ablations still provide strong signal that the wiki improves performance, especially when evidence must be integrated across conversations. As Brain is part of Computer, rather than an optimized, benchmark-specific retrieval system, we believe that competitiveness will only increase with tasks that more closely resemble production workflows.

Offline datasets cannot capture every feature of real user histories, so we also run a daily paired evaluation over fresh production-derived cohorts. The same fixed questions are answered against matched user state with Brain enabled and disabled, then judged for correctness, currentness, and recall.

demonstrated that Brain increases answer correctness by 25% and recall by 16%. These performance gains have continued to hold; over the past 30 days, Brain-enabled sessions outperformed the control on every run and every judged dimension. In absolute terms, Computer users enjoyed improvements of 9.3 points in correctness, 8.0 points in currentness, and 8.9 points in recall. The Brain-enabled trajectories also used approximately 15% fewer tokens, cost 10% less, and completed generation 10% faster.

We've continued to refine Brain to bring the best memory experience to users. One recent change places Brain's compact index directly in the agent's initial context rather than requiring the agent to discover and read it later. In a randomized experiment, this prefill treatment increased Brain usage and reduced memory-related dissatisfaction by 6.9%.

The offline evaluation harness also doubles as part of an autonomous improvement pipeline. Proposed changes to Brain's memory subagent, retrieval skills, and prompts are run through the matched ablations on our internal dataset and public benchmarks. Computer agents can iterate on the results autonomously, preserving each iteration's change, deltas, and cost as a durable record and keeping only the changes that move the numbers. The result is a system where Brain's evaluators are also its optimizers, driving future improvements.

Continual learning is one of the defining challenges for building agent systems that work over weeks and months. We believe memory architectures are best exposed as environments that agents can directly explore using their ordinary toolsets. Exposing memory as a filesystem, with Brain as a structured knowledge wiki on top, makes context efficiently navigable through simple and familiar tools.

Brain is designed for self-improvement, so that the memory system can keep getting better as usage grows. The Dream background agents distill fresh information into Brain updates, ensuring that the foreground agents always start a new session with an organized view of the most recent context. The evaluation harness doubles as a testing ground for autoresearch loops on the core memory architecture and agent-facing interfaces.

Already, Brain has resulted in more accurate and performant agent sessions while reducing tokens spent. Our careful co-design of Brain with Computer's production stack ensures these gains translate directly into real benefits for users.

We're continuing to build more capabilities to improve the quality of Computer's memory. In the meantime, for users with Brain enabled, memory will improve with every session.
