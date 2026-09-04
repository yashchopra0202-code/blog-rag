---
url: https://x.ai/news/workflows
title: Workflows in Grok Build
site: xai
date: 
scraped_at: 2026-09-04T21:08:02+00:00
---

Grok Build can now write and run workflows: orchestration scripts that fan a task out across hundreds of parallel agents, verify the results, and report back in one background run.

Grok Build can now run

: describe a large task in plain language, and Grok plans it, fans it out across hundreds of parallel agents in the background, and reports back when everything is done. Your session stays free the whole time.

Workflows are built for complex, multi-faceted tasks a single conversation can't hold: reviewing every feature in a large PR, triaging the last 100 issues, auditing a codebase for one class of bug. If the work splits into many independent pieces and should end in one clear report, ask for a workflow.

Grok plans the task as a small script: the phases of work, the agents in each phase, and how their results roll up. Each agent starts with a clean, focused context, and the plan can build in checks a single pass can't, like independent skeptics verifying every finding before it reaches the final report.

Runs get a budget of 128 agents, and up to 1,024 for big jobs. Progress is saved as the run goes, so pausing and resuming never redoes finished work. Run

to watch it live, phase by phase, with per-agent token counts.

Grok authors the workflow from your request, smoke-checks it before launching, and improves it between runs; you never write the script yourself. When one works, keep it: workflows in

are shared with your team, and ones in

follow you everywhere. Each saved workflow becomes its own slash command that takes arguments, so once you keep the PR review from the demo above, the next review is just

.

ships built in: it fans research questions out to parallel investigators, verifies every claim against its sources, and returns a cited report.

Some examples to try:

Essential cookies keep the site working and stay on. Optional cookies help with performance and advertising — accept, reject, or manage them. Learn more in our

,

, and

.

These cookies are necessary for the website to function and cannot be switched off in our systems. They are usually only set in response to actions made by you which amount to a request for services, such as setting your privacy preferences, logging in or filling in forms. You can set your browser to block or alert you about these cookies, but some parts of the site will not then work. These cookies do not store any personally identifiable information.

These cookies may be set through our site by our advertising partners. They may be used by those companies to build a profile of your interests and show you relevant adverts on other sites. They do not store directly personal information, but are based on uniquely identifying your browser and internet device. If you do not allow these cookies, you will experience less targeted advertising.

These cookies enable the website to provide enhanced functionality and personalisation. They may be set by us or by third-party providers whose services we have added to our pages. If you do not allow these cookies then some or all of these services may not function properly.

These cookies allow us to count visits and traffic sources, so we can measure and improve the performance of our site. They help us know which pages are the most and least popular and see how visitors move around the site. All information these cookies collect is aggregated and therefore anonymous. If you do not allow these cookies, we will not know when you have visited our site.
