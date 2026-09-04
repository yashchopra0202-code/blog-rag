---
url: https://cohere.com/blog/automating-fork-maintenance-with-ai-agents
title: Automating fork maintenance with AI agents
site: cohere
date: 
scraped_at: 2026-09-04T13:25:24+00:00
---

You maintain a fork. Upstream moves. You sync, things break, you fix them, you verify, you ship. A few weeks later, upstream moves again. The cycle repeats.

This post describes a general method for automating that cycle using AI coding agents. We apply it to our fork of vLLM, walking through a concrete case where a routine upstream release silently broke Cohere's

ASR model on our fork, with the fix flowing back upstream as a vLLM PR.

In practice, this approach has compressed the time to absorb a new upstream release from

, with humans only reviewing the outcome. The skills powering this workflow are open-sourced at

.

Maintaining a long-lived fork of an actively developed project is a recurring cost. But upstream releases also carry features, performance improvements, and bug fixes that you want. Staying in sync is not just maintenance, it's how the fork keeps getting better. The problem is that every upstream release also introduces a

: merge conflicts, changed APIs, removed functions, new dependencies, or broken tests. The fork maintainer's job is to absorb that disturbance and restore a working state.

The structure of this work is always the same:

This is a feedback loop. It already exists in every team that maintains a fork; it's just slow and manual. For our vLLM fork, absorbing a typical upstream release used to take weeks of intermittent developer attention, and the goal of the work described below is to bring that down to days of mostly unattended agent time.

In control theory, a

continuously compares its output to a reference and adjusts to close the gap. But real systems also face

: external inputs that push the system away from its desired state.

The controller uses the error to adjust the system; the feedback brings output closer to the target. A well-designed feedback loop doesn't just track the reference; it

by detecting their effect on the output and driving the error back toward zero without manual intervention.

Cruise control is the textbook example. You set a desired speed (reference), the car maintains it (system), but a hill or headwind appears (disturbance). A good controller notices the speed drop and adjusts throttle automatically.

Fork maintenance has exactly the same structure.

The goal is to automate the entire loop —

— so we can absorb upstream improvements with minimal human intervention.

There are several ways to sync a fork with upstream:

,

, and

are the most common. Merge preserves both histories, but produces a tangled commit graph that makes it hard to tell custom changes from upstream. Cherry-pick gives precise control, but doesn't scale when upstream moves hundreds of commits per release; you end up maintaining a growing list of picks that drifts out of sync. Rebase replays your custom commits on top of the new upstream tag, producing a clean, linear history where your patches sit clearly on top. The tradeoff is that rebase rewrites history and forces a force-push, but for a fork with a small number of custom commits on top of a fast-moving upstream, the clarity is worth it.

At Cohere, we settled on rebase early on. Before the agent-based workflow described below, our pipeline already mixed scripted automation with manual work.

This process already combines several kinds of automation:

replays known resolutions, GitHub Actions runs the rebase attempt and CI, and LLMs assist with individual coding and debugging tasks. But the human is still part of the controller, stitching the pieces together, choosing which fixes to apply, and deciding when to re-run. The feedback loop works; it just turns slowly. The agent-based workflow described below keeps the same structure, but lets an agent play the controller role, so iterations happen at machine speed and humans only intervene at the edges.

This method decomposes the loop into three, agent-automatable components. Each maps to a piece of the control diagram.

An agent skill detects and applies new upstream releases. It rebases the fork onto the new tag and resolves merge conflicts automatically. This is the disturbance entering the system: a deliberate, automated action that we know will temporarily break things, but that we want to absorb as quickly as possible.

The skill needs to:

After a rebase, the fork is in an unknown state. Measurement tells you how far you are from the goal: a working fork with all custom behavior intact. Without it, the agent is flying blind.

The measurements themselves (tests, benchmarks, evals) are defined by the project and already exist before any automation. What the agent automates is

them: a test-runner skill that knows how to set up the environment, execute the verification suite, and report results.

The output is the error signal: which tests fail, which benchmarks regress, which evals degrade. The richer and more reliable the measurements, the faster the controller can converge. A fork with a thin test suite gives a weak signal; the agent won't know what's broken or how close it is to done.

An agent skill closes the loop. After the rebase lands and measurement results come back, the skill:

This is the controller driving the error to zero. The key insight is that the agent doesn't need to get the rebase right on the first try, it just needs to iterate — exactly like a developer would.

is an open-source LLM serving engine. At Cohere, we use it across the inference stack, from RL rollouts and evals during model development to serving user requests in production. We maintain a fork to carry custom commits — additional model support, custom kernels and optimizations, modified entrypoints, extra tests — some of which are in the process of being upstreamed, others specific to our needs. The challenge is replaying those commits onto each new upstream release without breaking anything. Upstream cuts a release roughly every few weeks, and each one is substantial: the diff between tags often touches hundreds of files.

We built five skills, open-sourced at

, that instantiate the general pattern. Each skill is a markdown document that a coding agent reads and executes interactively, with access to the terminal, file system, and the tools it needs.

Throughout this section:

/

are the old and new upstream tags, and

/

are the fork branches before and after the rebase.

A typical invocation:

As a sequence of skill interactions:

The inner loop is the controller iterating on b2: local-test-runner reports a failure, rebase-assistant applies a fix and re-runs until the tests pass.

Here is a real invocation of this loop, end to end.

Our fork sits at

, one custom commit on top of upstream

that enables a correctness test for Cohere's

ASR model. vLLM added support for this model architecture in

, but the upstream test was commented out because the weights weren't published yet. Our custom commit just un-comments one line.

The test runs the model over a filtered slice of the earnings-22 validation set and asserts WER ≤ 11.92. That single number is our measurement signal

. When the fork is healthy, the number sits near 11.92; when something is broken, it blows up.

Upstream cuts

. It's an incremental release, but not a small one: it includes a

version upgrade and related refactors. We run auto-rebase with one prompt.

The loop worked end to end: a disturbance arrived, the controller absorbed it, and the fork was back to a healthy state automatically.

Because the bug affected every downstream user of this model, we submitted

to turn the workaround into a proper upstream fix. Once merged, the next release will no longer require a fork patch for this model; the disturbance is gone for everyone.

The same closed-loop structure applies whenever a codebase absorbs an external change and needs to converge back to a working state.

Another recent example is our internal fork of HuggingFace transformers, where we maintain

ahead of its public release. When

landed with deprecated arguments removed, new required signatures, and changed tokenizer behavior, all of that was the disturbance. The same loop applied: upgrade to v5, run the model's correctness evals and generation tests, and let an agent iterate on the failures. Several issues surfaced across import paths, API calls, and tokenizer defaults; some were fixed autonomously, others required a human in the loop to resolve. The cycle continued until the model generated correctly on v5 before the public release.

The skills were different, but the structure was identical: introduce the change, measure the gap, close the loop.

The structure of fork maintenance doesn't change: sync, measure, fix, repeat. What changes is how fast the loop turns.

Before the agent-based workflow, syncing our vLLM fork with a new upstream release took

: waiting for someone to context-switch in, manually triaging conflicts, re-running CI, and debugging failures one at a time. With auto-rebase driving the controller loop, that timeline has compressed to

. And because the expected measurements are preset in the repo, the full pipeline runs without human input; a person only needs to review the outcome.

The method generalizes to any fork with a measurable definition of "working": detect the disturbance, collect measurements, and let an agent iterate on the error. The skills are composable and the control-theory framing makes it straightforward to adapt them to new codebases.

The skills described in this post are open-sourced at

. If you maintain a fork and want to try the approach, start by writing a measurement (a test, a benchmark, an eval) that captures what "healthy" means for your fork. The rest of the loop follows from there.

Thanks to Ekagra Ranjan for assisting with the Cohere Transcribe experiments, Zhoujie Zhao and Walter Beller-Morales for helping shape the agent skills, and Bharat Venkitesh for supporting this work.

Written By

Donglu Wang

Member of Technical Staff, Foundations

Tags

Share

AI isn’t a shortcut.

It’s how business gets ahead.
