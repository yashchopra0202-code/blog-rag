---
url: https://cohere.com/blog/cohere-security-ai-agent-north-wiz
title: Creating a security agent with Cohere North and Wiz
site: cohere
date: 
scraped_at: 2026-09-04T13:25:27+00:00
---

At Cohere, we build secure, sovereign AI for mission-critical environments across regulated industries and governments. Our security posture has to scale with a codebase that moves fast, a cloud footprint that grows constantly, and a threat landscape that is constantly evolving.

Using

, our enterprise AI agent platform, we found a way to automate our incident response workflows. This post details how we connected our cloud security platform

to North, through a custom Model Context Protocol (MCP) server.

The result? A security agent that handles the entire incident response workflow, from triaging critical findings to drafting IR reports, creating tickets, and updating Wiz status — all from a single prompt.

Wiz surfaces the toxic combinations of risk factors that create critical attack paths, such as an internet-facing VM with a critical vulnerability and high-privilege IAM access. The signal is high-fidelity. The harder problem is what comes next.

Translating a finding into coordinated action still requires a human in the loop — and that workflow looks different for every team. For ours, a single critical finding meant:

That process could take

. Not because the signal was unclear, but because the path from insight to action wasn’t yet built for our exact environment, tools, and team rhythm. And as our cloud footprint expanded, so did the volume of findings that needed that same careful handling. We needed a way to close that gap without adding headcount.

We transformed North into a security agent by connecting it to Wiz through a custom MCP server. This integration turned North into an incident response agent that handles the triage-to-resolution workflow, assisting security engineers to respond faster.

North natively speaks MCP, enabling a clean, extensible architecture:

North authenticates to the MCP server via a shared secret header, while the server uses OAuth2 client credentials for Wiz, keeping service account tokens secure and server-side.

“Toxic combinations” are Wiz's term for multi-factor attack paths: findings where individually manageable risks chain together into a critical exposure. An internet-facing VM is a problem. A VM with a critical CVE is a problem. A VM that is internet-facing, has a critical CVE,

carries an IAM role with access to sensitive data is an entirely different category of problem.

North analyzes critical Wiz findings, evaluates attack chains, and ranks them by real-world blast radius, factoring internet exposure, privilege level, and data sensitivity. This 20-second analysis replaces what previously consumed half of a security engineer’s morning.

, reads the

field on each finding (which contains Wiz's narrative of the multi-hop attack path), then uses Reasoning to rank them. The output is a risk table sorted by an agent's assessment of real-world risk, weighing internet exposure, privilege level, and data sensitivity.

This is the workflow that required the most engineering. Here is the prompt we wrote:

What happens:

The report format is strict, encoded in the system prompt to prevent the hallucination problems we hit in early iterations (more on that below). It includes severity, status, report date, ticket link, a two-sentence summary, an affected asset table with exact field values from Wiz, root cause based on the rule description, exploitability and blast radius assessment, and a prioritized remediation table.

We built a North automation — a scheduled graph-based workflow — that runs every Monday at 3:00 a.m. and produces a security posture document without anyone asking for it.

The automation calls three tools in sequence:

for aggregated metrics,

for the active toxic combo spotlight, and

for actively exploited CVEs in our environment. It then generates a Document Mode report covering:

The brief lands in the security team's inbox every Monday morning. No analyst has to remember to pull it, no one has to decide what format it should be in, and the data is current as of the moment it runs.

The integration removed the first-pass triage loop entirely. Security engineers now begin with pre-populated incident response reports and tracked tickets rather than raw alerts. For critical findings, the first human touchpoint shifted from

to

— a smarter, more strategic use of human expertise.

Previously, triage could take anywhere from 30 minutes to two hours per finding, with no way to accelerate the process without adding headcount. For our team, that pace was unsustainable given the rapid growth of our cloud environment.

The automated weekly posture brief now delivers consistent visibility without manual effort, ensuring that the team always operates with up-to-date situational awareness.

North's MCP-native architecture provided the leverage we needed: build the Wiz integration once and expose it across all workflows. The platform's reasoning capabilities handle complex security analysis while maintaining strict data fidelity, using exact Wiz field values rather than inferring names. This combination of integration flexibility and analytical precision makes North uniquely positioned as the central nervous system for modern security operations.

The full implementation is available

, enabling your organization to replicate this pattern and transform your security response capabilities.

Here's the path from zero to a working North agent. The full source is in our

.

A Wiz tenant with a service account you control, access to North, and either Docker or a Cloud Run project to host the server.

Save the client ID and secret. You'll need them in the next step.

Fill in .env with your Wiz credentials and generate a random value for MCP_SERVER_SECRET (this is the shared secret North will use to authenticate to your server):

Expose it with ngrok, so North can reach it:

North will discover the eight tools automatically.

Open north-system-prompt.md from the repo and paste the full contents into the agent's system prompt field. This encodes the IR report format, tool routing rules, enrichment strategy by finding type, and the naming rules that prevent the agent from hallucinating asset names.

If the tools are wired correctly, the agent calls wiz_get_security_posture and returns a metrics summary with a link to your Wiz dashboard. From there, try the Toxic Combination analysis and the end-to-end IR workflow described above.

North's MCP-native architecture provided the leverage we needed: build the Wiz integration once and expose it across all workflows. The platform's reasoning capabilities handle complex security analysis while maintaining strict data fidelity, using exact Wiz field values rather than inferring names. This combination of integration flexibility and analytical precision makes North uniquely positioned as the central nervous system for modern security operations.

The full implementation is available

, enabling your organization to replicate this pattern and transform your security response capabilities.

Written By

Bolaji Agunbiade

Member of Technical Staff, Security

Tags

Share

AI isn’t a shortcut.

It’s how business gets ahead.
