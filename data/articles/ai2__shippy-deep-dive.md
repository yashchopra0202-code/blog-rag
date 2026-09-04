---
url: https://allenai.org/blog/shippy-deep-dive
title: What building Shippy taught us about building agents
site: ai2
date: 
scraped_at: 2026-09-04T21:11:41+00:00
---

Shippy is a maritime AI agent built for high-stakes decisions, where the wrong answer has real impacts. Here's the architecture behind it—and the lessons we're carrying into Ai2's other environmental platforms.

July 13, 2026

Building an AI agent for a high-stakes operational domain like protecting the ocean is, above all, a problem of reliability. For a maritime analyst, a wrong answer could send a patrol vessel miles in the wrong direction, costing significant resources that are already stretched thin and potentially putting personnel in harm's way.

So when the

team set out to build

, our AI for real-time maritime domain awareness, the real work wasn't the model. It was building a system we could trust to be correct, to stay within its limits, and to hold up across a wide range of tasks. And we had to verify all of it against Skylight's live data, updated continuously as new satellite and vessel signals arrive—not a static snapshot.

We think of an agent like Shippy as three things: a

,

, and

.

The

is the system prompt that frames Shippy's persona and sets behavioral boundaries.

tell Shippy how to handle specific kinds of requests. Together, the soul and skills are baked into a Docker image—a versioned, deployable artifact that defines what Shippy

.

covers everything else: which agent harness to run (in Shippy’s case,

, an open-source agent framework), which LLM to use (currently, Shippy relies on Claude Opus 4.6), and runtime settings. Secrets like API keys are injected at runtime; swapping the model or the harness is a config change, not a rebuild.

Shippy’s skills follow the same

used by coding tools like Claude Code and Codex—plain markdown files with structured frontmatter. This keeps each skill comprehensible, versioned, and easy to revise. Shippy currently includes skills for:

For example, the Skylight API query skill encodes the full workflow for answering a question about a specific area. When an analyst or user asks, "show me fishing activity in Panama's EEZ last month," the skill's instructions direct Shippy to first resolve "Panama EEZ" to a boundary polygon through Skylight's regions API instead of guessing or hard-coding coordinates, then query Fishing Events within that geometry, format the results with deep links back to the Skylight map, and attribute any vessel metadata drawn from Skylight partners like Global Fishing Watch or TMT.

A single question posed to Shippy can hook into several skills at once. "Are there vessels operating near the Cordillera de Coiba MPA?" draws on the Skylight skill for data query, our partner ProtectedSeas’ database for MPA boundary context, and the vessel track skill for interpreting vessel behavior. All of this happens in a single dialogue turn.

The soul defines what Shippy will and won't do. It won't make legal determinations about whether a vessel is breaking the law—that is a determination for people, not an agent. It also won't speculate beyond what the data supports. These boundaries are explicit in the system prompt, not implicit in fine-tuning, which makes them auditable and easy to revise.

Agents are nondeterministic. You can't control what the model decides to do, but you can make the tools it reaches for predictable. To that end, Shippy 'talks' to Skylight through a purpose-built CLI that calls the API, rather than issuing raw calls itself.

Our API has dozens of input types, nested filter objects, pagination cursors, and complex geometry inputs. In early prototypes, we let Shippy construct API calls from scratch. It produced a steady stream of subtle bugs: malformed pagination that silently dropped results, geometry encoding errors, and correct-looking queries that returned wrong data because of a misunderstood filter type.

The Skylight CLI collapses that complexity into a predictable interface. Shippy issues a single command –

with typed filter flags – and the CLI handles authentication, pagination, and structured output. The CLI is also self-documenting: extensive

text and detailed error messages give the agent (and human developers) enough context to recover from mistakes without guessing. Its output is always written to a local JSON file rather than piped through the shell. Early on, large result sets would hit pipe buffer limits or break downstream tools like

. Writing to disk sidesteps both problems and lets the agent programmatically access query results across subsequent steps.

Underneath the CLI is a

: multiple resource types – Skylight Events, vessels, regions, satellite imagery, vessel tracks, and more – accessible through a common pair of operations, search and aggregate. The APIs' inputs and outputs are defined as typed schemas with field-level descriptions.

This layering – typed API, deterministic CLI, and agent skills that reference the CLI's commands – means that each of Shippy's components can be tested independently. The API has its own test suite. The CLI can be exercised by a human or an agent. And the agent skills reference CLI commands that handle the plumbing so that Shippy doesn't have to reinvent the wheel every time it hits the Skylight API. Each layer narrows what the next layer can get wrong.

Skylight serves hundreds of government agencies and NGOs across over 70 countries. A fisheries officer in the Philippines has Areas of Interest, vessel watchlists, and alert configurations that are scoped to their Skylight account. When they ask Shippy a question, the agent's API calls need to return their data, and their conversation history must never be visible to anyone else.

Every user talks to Shippy inside their own ephemeral, isolated session, and making that work reliably at scale was one of the most significant engineering efforts behind the project. We built

, an agent hosting platform that provisions a dedicated Kubernetes deployment for each user session. When a user opens a conversation, the system spins up a set of pods packaging the agent runtime, its skills, and the Skylight CLI. The user's Skylight JWT is injected at provision time so the agent's API calls are scoped to that user's data.

Files the agent writes during a multi-step analysis exist only within that session and are never shared across users. Inside the sandbox, the agent can write and run code, install dependencies, pull in datasets, and work through multi-step analyses. At the network level, the sandbox is restricted to only the services it needs.

Most benchmarks rank general-purpose AI on static questions. They don't capture how an agent behaves once it's wired into a real workflow: how it selects tools, queries live data, acts on results, and knows where to stop. So we built our own eval system around how Shippy works, scoring the whole agent – model, skills, and sandbox together – against live data.

In our eval framework, subject-matter experts write scenarios and rubrics, choosing which criteria apply to each task and setting the weights, so every task is graded on what actually matters for it. A fishing-events query, for instance, weights data accuracy most heavily, with boundary resolution and timeframe next, and source attribution and response style carrying less. They also annotate individual responses as correct or incorrect, giving the judge ground truth to score against. Subject-matter experts additionally annotate individual responses as correct or incorrect, giving the judge ground truth to score against.

The pipeline is straightforward: a natural-language prompt runs through the sandbox, an LLM judge grades each criterion from 0 to 1 and explains in writing why the response did or didn't meet it, and the weighted aggregate is checked against a fixed pass threshold, as the diagram below shows.

Tasks are executed through

, an open evaluation framework. We wrote a Harbor plugin that spins up a real Shippy session on the exact version being tested, against the same real data a user would encounter. The suite runs in parallel against a specific versioned Shippy build, producing a timestamped results file and a report of score changes against the previous run. We rerun the suite whenever the skills, model, or underlying data change, and a version of Shippy that regresses on our eval criteria doesn't reach end users.

Shippy scores consistently across data retrieval and guardrail tasks, correctly refusing military intelligence requests, maintaining user data isolation, and attributing sources accurately. In our latest run, the clearest patterns were patrol-planning tasks where Shippy overstepped into tactical recommendations rather than decision support, geometry-sensitive queries where boundary simplification caused missed Events, and one case where the agent invented a CLI command that didn't exist. Each of these directly informs our next round of skill improvements.

We're opening Shippy to early adopters on a rolling basis and inviting them to stress-test it—to find the questions the agent answers poorly and guardrails that may need tightening. Here’s what we're building next:

Our work on Shippy is already shaping how we think about agents elsewhere at Ai2—most immediately EarthRanger, our wildlife-conservation platform, and OlmoEarth, our open suite of Earth observation tools. Mothership was built to be general and to host other agents, so while maritime is the first domain we're applying it to, we don't expect it to be the last.

At Ai2 we’re building the future of transparent, open-source AI — built in the open to empower scientific progress and fundamental understanding of this world changing technology. We’re not here to make profits, we’re here to make sure benefits of AI are shared widely and for the benefit of humanity. If this appeals to you, please take a look at our open roles.
