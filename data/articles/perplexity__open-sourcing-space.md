---
url: https://www.perplexity.ai/hub/blog/open-sourcing-space
title: Open-sourcing SPACE, the sandbox platform behind Computer
site: perplexity
date: 2026-10-15
scraped_at: 2026-10-17T08:10:28+00:00
---

Perplexity open-sources SPACE, the sandbox platform behind Computer, to help developers build safer autonomous AI agents

Contents

Since launching

in February, Perplexity has been an early pioneer in personal agents. We’re committed to the hard problems of agent governance, detecting unsafe behaviors and preventing rogue agent activity. In July, we replaced our commercially available sandbox provider with a more robust and resilient in-house solution we named

SPACE provides high security for advanced agentic systems. In fact, a recent

proved SPACE resilient against network-bypass techniques like those used in the OpenAI/Hugging Face incident.

Today, we're open-sourcing SPACE to give developers a foundation for building safer agent systems and contributing to stronger protections across the industry. Developers can access the

, and open source is essential to solving it. When developers have systems they can inspect, adapt, and build on, they find more weaknesses and develop better tools. Open-sourcing SPACE gives developers a production-tested foundation for agent runtimes, with isolation, state recovery, and credential and network controls built in.

Sandboxes keep agents secure, letting them access the tools and files they need to complete these tasks, while keeping sensitive information protected.

Open-sourcing SPACE gives developers a starting point for the environments where their agents run code and work with files. Teams can see how the SPACE sandbox platform works and build on its implementation. They can also adapt it to their needs rather than recreating the underlying infrastructure.

In Computer, SPACE supports isolated code execution, pause and resume, recovery, and session branching. Those capabilities provide the foundation for assistants that could:

These examples illustrate how developers could use SPACE's documented isolation and session controls. Platform and security engineers can also review the isolation model and security examples before integrating SPACE into their own systems.

When we give agents more room to solve problems, we need

on how they do it. We know that agents pursuing legitimate tasks can still cross security boundaries when they attempt to work around missing files, failed requests, or permission denials.

We can put model safeguards into place to reduce the likelihood of unsafe behavior. Adding independent controls in the surrounding system helps contain the damage if those safeguards fail. They limit what an agent can access regardless of what it decides to do.

SPACE puts those controls around a separate workspace for agent-generated code and files. We designed it to combine isolation, recovery, and efficient execution. This lets agents perform useful work over long sessions without relying on the model alone to respect security boundaries.

Each SPACE sandbox runs inside a small virtual machine with its own operating system, creating an isolation boundary between the agent’s work and the host system. A central control plane coordinates when these workspaces are created, paused, resumed, or removed.

SPACE treats the sandbox as untrusted and manages network access and platform-held credentials outside the sandbox. Agents can connect to authorized services without those credentials being stored in their working environment.

and checkpoints of the full running environment preserve progress across interruptions. To keep these operations efficient, SPACE stores changes rather than repeatedly copying entire environments. This reduces the work needed to create, restore, or branch a sandbox.

Since July, SPACE has powered all Computer sessions and has handled millions of sandbox creations per day.

on the same production traffic, sandbox creation was three to five times faster than with our previous provider.

We also

against agents deliberately trying to breach its boundaries. Our published security evaluation found no escape from the virtual machine to the host in 108 attempts, but some found ways around network restrictions. We fixed those weaknesses, and neither identified attack method succeeded in follow-up testing.

We also disclosed related weaknesses we found in other sandbox platforms to their vendors, extending that work beyond our own infrastructure.

SPACE is part of a broader effort to strengthen the systems people rely on as AI takes on more work. Through the

, we conduct security research and collaborate with the wider community, translating findings into practical defenses.

We believe open-sourcing security tools gives developers more ways to test defenses, find weaknesses, and build safer AI systems. We've shared tools that address different parts of that work:

Making these tools available lets other teams inspect our work, adapt it to their needs, and contribute improvements. With SPACE, we're extending that approach to the environments where agents execute code and work with files.

has tested and launched SPACE on its cloud platform and is working with Perplexity to bring it to its customers.

is also partnering with Perplexity to add SPACE to its Managed AI Services portfolio.

has published setup guidance for developers who want to deploy SPACE for evaluation on

Developers can start with the SPACE’s setup instructions and security guidance to deploy it for their own agent systems. The

and

define the supported configurations and included components.
