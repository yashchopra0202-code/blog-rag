---
url: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
title: Equipping agents for the real world with Agent Skills
site: anthropic-engineering
date: 
scraped_at: 2026-09-04T13:10:28+00:00
---

As model capabilities improve, we can now build general-purpose agents that interact with full-fledged computing environments.

, for example, can accomplish complex tasks across domains using local code execution and filesystems. But as these agents become more powerful, we need more composable, scalable, and portable ways to equip them with domain-specific expertise.

This led us to create

: organized folders of instructions, scripts, and resources that agents can discover and load dynamically to perform better at specific tasks.

Skills extend Claude’s capabilities by packaging your expertise into composable resources for Claude, transforming general-purpose agents into specialized agents that fit your needs.

Building a skill for an agent is like putting together an onboarding guide for a new hire. Instead of building fragmented, custom-designed agents for each use case, anyone can now specialize their agents with composable capabilities by capturing and sharing their procedural knowledge. In this article, we explain what Skills are, show how they work, and share best practices for building your own.

To see Skills in action, let’s walk through a real example: one of the skills that powers

. Claude already knows a lot about understanding PDFs, but is limited in its ability to manipulate them directly (e.g. to fill out a form). This

lets us give Claude these new abilities.

At its simplest, a skill is a directory that contains a

. This file must start with YAML frontmatter that contains some required metadata:

and

. At startup, the agent pre-loads the

and

of every installed skill into its system prompt.

This metadata is the

of

: it provides just enough information for Claude to know when each skill should be used without loading all of it into context. The actual body of this file is the

of detail. If Claude thinks the skill is relevant to the current task, it will load the skill by reading its full

into context.

As skills grow in complexity, they may contain too much context to fit into a single

, or context that’s relevant only in specific scenarios. In these cases, skills can bundle additional files within the skill directory and reference them by name from

. These additional linked files are the

(and beyond) of detail, which Claude can choose to navigate and discover only as needed.

In the PDF skill shown below, the

refers to two additional files (

and

) that the skill author chooses to bundle alongside the core

. By moving the form-filling instructions to a separate file (

), the skill author is able to keep the core of the skill lean, trusting that Claude will read

only when filling out a form.

Progressive disclosure is the core design principle that makes Agent Skills flexible and scalable. Like a well-organized manual that starts with a table of contents, then specific chapters, and finally a detailed appendix, skills let Claude load information only as needed:

Agents with a filesystem and code execution tools don’t need to read the entirety of a skill into their context window when working on a particular task. This means that the amount of context that can be bundled into a skill is effectively unbounded.

The following diagram shows how the context window changes when a skill is triggered by a user’s message.

The sequence of operations shown:

Skills can also include code for Claude to execute as tools at its discretion.

Large language models excel at many tasks, but certain operations are better suited for traditional code execution. For example, sorting a list via token generation is far more expensive than simply running a sorting algorithm. Beyond efficiency concerns, many applications require the deterministic reliability that only code can provide.

In our example, the PDF skill includes a pre-written Python script that reads a PDF and extracts all form fields. Claude can run this script without loading either the script or the PDF into context. And because code is deterministic, this workflow is consistent and repeatable.

Here are some helpful guidelines for getting started with authoring and testing skills:

Skills provide Claude with new capabilities through instructions and code. While this makes them powerful, it also means that malicious skills may introduce vulnerabilities in the environment where they’re used or direct Claude to exfiltrate data and take unintended actions.

We recommend installing skills only from trusted sources. When installing a skill from a less-trusted source, thoroughly audit it before use. Start by reading the contents of the files bundled in the skill to understand what it does, paying particular attention to code dependencies and bundled resources like images or scripts. Similarly, pay attention to instructions or code within the skill that instruct Claude to connect to potentially untrusted external network sources.

Agent Skills are

across

, Claude Code, the Claude Agent SDK, and the Claude Developer Platform.

In the coming weeks, we’ll continue to add features that support the full lifecycle of creating, editing, discovering, sharing, and using Skills. We’re especially excited about the opportunity for Skills to help organizations and individuals share their context and workflows with Claude. We’ll also explore how Skills can complement

(MCP) servers by teaching agents more complex workflows that involve external tools and software.

Looking further ahead, we hope to enable agents to create, edit, and evaluate Skills on their own, letting them codify their own patterns of behavior into reusable capabilities.

Skills are a simple concept with a correspondingly simple format. This simplicity makes it easier for organizations, developers, and end users to build customized agents and give them new capabilities.

We’re excited to see what people build with Skills. Get started today by checking out our Skills

and

.

Written by Barry Zhang, Keith Lazuka, and Mahesh Murag, who all really like folders. Special thanks to the many others across Anthropic who championed, supported, and built Skills.
