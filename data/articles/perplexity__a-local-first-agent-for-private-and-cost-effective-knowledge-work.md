---
url: https://www.perplexity.ai/hub/blog/a-local-first-agent-for-private-and-cost-effective-knowledge-work
title: A Local-First Agent for Private and Cost-Effective Knowledge Work
site: perplexity
date: 2026-08-25
scraped_at: 2026-09-04T21:17:00+00:00
---

A harness and model co-designed for local knowledge work, running on device and accessing remote capabilities on demand.

Contents

Perplexity

is a local-first agent.

The entire stack runs locally by default. The model, harness, conversation, and trajectory all live on the user's machine. Work that needs the outside world, such as web search, connectors, or escalation to a stronger advisor model on the cloud, is invoked only when necessary and always gated by the user. Sensitive data therefore never leaves the device without permission, and local models carry no inference fee: the system is private and cost-effective by construction.

An effective local-first agent requires the model and harness to be designed together. General-purpose harnesses assume a frontier model that can absorb long contexts, navigate a broad tool surface, and plan over long horizons. Local models are less reliable under those demands. Rather than asking a small model to manage a harness built for a large one, we shaped the two around each other: a harness tailored to the model's capability profile, and a model post-trained to use that harness effectively.

Agentic capabilities in recent months have advanced rapidly across a wide range of knowledge-work tasks. While these advances bring

, they also pose two challenges.

Token consumption is rising quickly, and with it overall spend. When intelligence is accessed through the APIs of closed-source models running on remote clusters, private information and intellectual property leave the user's device with every request. As agents scale across individual workflows and entire organizations, token expenditure and data movement become increasingly difficult to govern.

At the same time, open-source models have improved at an even faster rate. Progress is most visible in very small and efficient models such as NVIDIA

(30B total parameters),

(35B), and

(27B). These small models punch above their weight and are now capable of complex agentic workflows. Local-inference hardware is advancing in parallel: systems such as the

can now run these models locally. Together, these trends make fully on-device operation practical while allowing users to opt into external capabilities when needed, such as web search, connectors, or cloud-model escalation.

This local-first approach enables significant cost savings, since local inference avoids per-token API fees. It also naturally resolves the privacy and intellectual-property concerns: private tokens never need to be transmitted to remote clusters and remain safely within the boundary of the local device.

In June, we introduced the first

that decides what work should run on-device and what work should go to agents in the cloud. Here we explain how we built such a local-first agent, including the harness and the models co-optimized for one another.

We give an overview of the key design choices, evaluate Computer against popular open-source general-purpose harnesses (

and

) across three public benchmarks and our internal Local Knowledge Work Bench. On our benchmark, with the Qwen 3.8 27B model running on an NVIDIA DGX Spark, Computer achieves the highest score, 82.6% versus 77.6% for Pi and 74.0% for Hermes. PPLX 27B, our model post-trained on top of Qwen 3.8 27B, raises the score further to 85.4%.

Although compact on-device models are already quite capable, they still trail larger frontier models in performance. A carefully designed harness is needed to steer these models effectively and to address their limitations.

Popular open-source harnesses such as Pi and Hermes have proven to be general: they work well with a wide variety of models across sizes and classes. But they are not optimized for the capabilities of on-device models. We designed the local harness specifically for this setting, around a few key principles.

The main focus in designing our harness was to make the best use of the model's context.

Although on-device models such as Qwen 3.8 27B offer context windows of 260K tokens, we found empirically that they begin to struggle beyond 100K tokens. We therefore keep the core harness succinct: a minimal system prompt and a small set of core tools.

All other capabilities are modularized into on-demand skills that load and unload throughout the trajectory. We designed these skills for common knowledge-work tasks: research, data science, data visualization, document creation, software engineering, and more.

The harness also supports context compaction, summarizing stale context when a trajectory grows long so the model stays within its effective window.

Day-to-day knowledge work often requires connectors such as Gmail, GitHub, Outlook, and Google Calendar. These are usually exposed to a harness as

, whose large tool definitions consume a substantial share of the context. Instead, we converted the most-used MCPs into compact, easy-to-use command-line tools, supplemented with custom skills that make far better use of the limited effective context.

Performance also improves when the agent verifies its own work. Verification adds extra steps, but it greatly improves final results and substantially narrows the gap to frontier models. It can be triggered by the model itself or by a set of hooks that monitor the health of the trajectory and request self-verification when something goes wrong.

The harness executes tools in an OS-level sandbox on the user’s device. The boundary restricts processes, filesystem paths, and network access according to policy. This limits the blast radius of an erroneous command. If the sandbox is unavailable, the harness disables itself before any tool calls rather than degrading to unsandboxed execution.

This differs from open-source harnesses such as Pi and Hermes, which run commands directly with the user’s permissions by default. In Computer, isolation is always on, requires no configuration, and tools cannot run without it.

The diagram below shows how these principles fit together in the execution loop. The orchestrator is deterministic harness code, not an LLM: it maintains the loop, assembles context, and enforces policy. The local model proposes the next action; the orchestrator executes approved tool calls in the sandbox and returns their results to the model. Web search, connectors, and advisor calls cross the device boundary only when enabled and approved.

Using the same on-device base model, we compare our local harness with general-purpose alternatives on web research and multimodal document understanding. All harnesses use the Qwen 3.8 27B model with medium reasoning, running on an NVIDIA DGX Spark. This comparison isolates the capabilities contributed by the harness itself, before any model post-training.

We focus on these two capabilities because knowledge work often combines private documents on the user’s device with public information from the web to produce a grounded artifact. Web search requires connectivity, but model inference and private-document processing remain local. Local files serve as the authoritative source, public sources add context, and users can disable web search entirely for fully offline work.

We build our local harness alongside Perplexity's search engine, which has achieved top rankings in

. The harness accesses it through the

interface.

We evaluate research quality on 1,266

tasks. Computer uses Perplexity's search infrastructure along with our local harness, while Pi and Hermes rely on Brave, their recommended search provider. Computer reaches 66.7% accuracy, compared with 50.2% for Pi and 43.9% for Hermes.

Computer also has the lowest mean recorded wall time and token use: 402.1 seconds and 852k tokens per task, compared with 1,020.9 seconds and 1.01 million tokens for Hermes, and 826.0 seconds and 2.82 million tokens for Pi. Computer therefore uses 61% less wall time and 16% fewer tokens than Hermes, and 51% less wall time and 70% fewer tokens than Pi.

Many documents carry information visually and are difficult to parse as plain text: PDFs, scanned pages, screenshots, charts, and presentations. These workflows depend on OCR and image understanding, and benefit most from a natively multimodal model.

The harness passes document pages and images directly to the model, which understands them and combines visual evidence with the extracted text. Processing these files on device keeps sensitive documents and their extracted content private.

We evaluate multimodal document understanding on ParseBench-100, a 100-task subset of the

benchmark, with 20 tasks each for charts, layout, tables, text content, and formatting.

Computer reaches a mean score of 65.1%, compared with 34.6% for Hermes and 13.9% for Pi. It also completes tasks with the least time and the fewest tokens: on average 60.6 seconds and 20.1k tokens per task, compared with 108.3 seconds and 32.1k tokens for Hermes, and 410.5 seconds and 829.1k tokens for Pi. Computer leads in all five document categories, with its largest advantage on charts. Layout remains difficult for all three harnesses.

Harness

Chart

Layout

Table

Text content

Formatting

Computer

76.5%

16.2%

72.7%

87.9%

72.4%

Hermes

29.3%

2.9%

44.1%

61.5%

35.2%

Pi

2.5%

0.1%

11.0%

29.7%

26.1%

Even with a carefully designed harness, the hardest tasks still exceed the capabilities of a compact on-device model. For such tasks, the harness exposes an advisor tool: the local model can consult a stronger frontier model when it needs help with planning, resolving ambiguity, recovering from repeated failures, or verifying the final result.

The local model decides when to request advice, while the harness orchestrator retains tool authority and controls what context is sent. Escalation is optional. The user decides whether to enable it and whether to approve each advisor call manually or automatically.

Before an advisor call, the harness selects the relevant context, applies a PII classifier to flag sensitive information, and shows the user what would leave the device. The advisor receives only the approved context and returns text guidance; it has no direct access to the device's files, tools, or conversations. This improves both cost and privacy, and we plan to explore this direction further in future work.

We test this approach on challenging software engineering tasks, which demand strong reasoning and are where a local model most often falls short. For this we use

, a popular 89-task benchmark for coding agents.

We want to answer two questions: how much of the gap to a frontier model can advisor escalation close, and at what cost. Fully local models cost virtually nothing to run, since inference happens on the user's hardware. Once the model starts calling the advisor, however, it begins to incur API costs.

As the baseline for frontier performance, we use Claude Opus 5 operating in the local harness; the local model is Qwen 3.8 27B. Finally, we pair the two: Qwen 3.8 27B executes the task and escalates to a Claude Opus 5 advisor when it needs help. We do not evaluate advisor escalation with Pi or Hermes because neither provides an equivalent advisor tool; adding one would require modifying its tool surface and orchestration logic, so the result would no longer represent the off-the-shelf harness.

Advisor escalation raises Computer's score from 59.6% to 73.0%, a gain of 13.5 percentage points, at an estimated API cost of $0.415 per rollout. Running Claude Opus 5 alone reaches 82.4% at $0.65 per rollout. Escalation thus recovers roughly three-fifths of the gap to the frontier at about two-thirds of the frontier's cost, and the user decides when that trade is worth making.

So far, we have kept the local model unchanged to isolate what the harness contributes. With the harness design in place, the biggest remaining gains come from adapting the model itself. Perplexity Computer usage data shows us what people actually do for knowledge work, which we use to synthesize training data. We post-train the local model inside the Computer harness, guided by the real distribution of tasks that users perform.

Concretely, we identify a diverse set of use cases that exercise different model capabilities, tools, and connectors. From these use cases we synthesize realistic reinforcement learning environments and define challenging but verifiable tasks: each task consists of an instruction, an environment, and a verifier that scores the final result, where the environment is a Docker container in which the harness operates. Importantly, because the tasks are synthetic, they contain no real documents or user information.

We use these environments for two-stage training: rejection fine-tuning followed by reinforcement learning. In the first stage, we roll out the model against each task multiple times, select the best trajectories by verifier score, and train on them with supervised learning. This stage initializes the model for the specific harness and task distribution. In the second stage, reinforcement learning further fine-tunes the model, making it more robust.

A subset of tasks is held out from training and used for final evaluation; we call this held-out set the Local Knowledge Work Bench: 53 tasks spanning seven categories of day-to-day knowledge work, from deep research to document creation. We will soon publish a technical report describing the model training in detail, and we plan to open-source this evaluation benchmark.

We post-trained Qwen 3.8 27B with this approach, producing a model we call PPLX 27B, and evaluated it on the Local Knowledge Work Bench. With the base Qwen 3.8 27B model, Computer achieves the highest score (82.6%, compared with 77.6% for Pi and 74.0% for Hermes) and uses the fewest tokens (520k, versus 681k for Pi and 634k for Hermes). Pi completes tasks fastest at 176 seconds per task, compared with 218 seconds for Computer and 292 seconds for Hermes. PPLX 27B lifts Computer's score to 85.4%, at the cost of more tokens (678k versus 520k). Its estimated wall time is 250 seconds.

Category

Tasks

Share

Description

Deep research

20

37.7%

Answer complex questions requiring multi-hop web research, public datasets, statistics, and source verification.

Data, finance, and procurement

9

17.0%

Clean datasets, reconcile records, audit expenses, analyze investments, evaluate suppliers, and calculate financial metrics.

Documents, presentations, and design

7

13.2%

Produce polished PDFs, invoices, onboarding materials, event collateral, and business presentations.

Engineering, IT, and incidents

5

9.4%

Investigate incidents, analyze logs, write recovery plans, assess release readiness, and synthesize technical documentation.

Contracts, evidence, and compliance

5

9.4%

Review contracts, screen evidence, investigate recalls, redact sensitive documents, and verify compliance requirements.

Dashboards, software, and visualization

4

7.5%

Build interactive dashboards, educational microsites, charts, and project visualizations.

People, projects, and meetings

3

5.7%

Screen résumés, consolidate meeting decisions, and maintain project action trackers.

Our research shows that a strong open-source model, with capable local hardware and a harness built for them can handle real knowledge work at near-zero inference cost without requiring sensitive data to leave the device.

Across the various benchmarks, Computer matched or exceeded Hermes and Pi in accuracy while running Qwen 3.8 27B on an NVIDIA DGX Spark. Among the three benchmarks that report latency and token use, Computer was fastest on BrowseComp and ParseBench-100 and used the fewest tokens on all three; Pi was fastest on the Local Knowledge Work Bench.

The gains came from choices we made. We built a succinct local harness with skills that load on demand. We converted connectors into compact CLI tools instead of MCP servers. Execution was sandboxed for security.

The results also show where compact models have room for improvement. For example, on the challenging coding tasks of Terminal Bench 2.1, the local model trails the frontier model across all three harnesses. Advisor escalation narrows but does not fully close the gap; continued improvements in model capabilities and local hardware are still needed to push performance further.

The purpose of building the harness and model for local constraints is to give users explicit control over what information leaves their machines. There are also cost benefits to the user. We see these as part of a broader shift in which increasingly capable agents move from remote infrastructure to individual and local devices. We expect that advances in chips, models, and devices will continually expand the range and quality of knowledge work that Portable Computer handles locally.
