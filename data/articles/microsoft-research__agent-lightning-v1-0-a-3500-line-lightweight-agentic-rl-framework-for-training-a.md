---
url: https://www.microsoft.com/en-us/research/blog/agent-lightning-v1-0-a-3500-line-lightweight-agentic-rl-framework-for-training-agents-with-real-harnesses/
title: Agent Lightning v1.0: A 3,500-Line Lightweight Agentic RL Framework for Training Agents with Real Harnesses
site: microsoft-research
date: 2026-10-07
scraped_at: 2026-10-08T11:04:51+00:00
---

Published

By

Share this page

AI agents have evolved from single models to complex full-stack systems built from models, tools, and execution environments. Their capabilities increasingly depend on the agent harness that coordinates them from outside the model. Reinforcement learning (RL) is an approach where AI systems learn through trial and error, guided by rewards and penalties for their actions. RL can make those agents better, but most agent RL systems require developers to reimplement the agent inside the training framework. That is costly, and it means the agent being trained is not quite the agent that gets deployed.

To address this, researchers at Microsoft Research Asia have introduced the Harnessed Agentic RL training paradigm and open-sourced a fully rebuilt

. Compared with the original, Agent Lightning, v1.0 puts more emphasis on staying lightweight, on integrating with real harnesses, and on a complete, reproducible agent RL training pipeline.

Agent Lightning v1.0 was rebuilt around Harnessed Agentic RL, with key improvements:

Traditional agentic RL assumes the training framework owns the interaction loop with the environment. In a ReAct-style loop, the model generates an action, the environment returns an observation, the observation is appended to the context, and the model generates the next action, so the whole rollout maps onto one continuous token trajectory. Early RL systems such as verl, AReaL, and slime were built this way, which meant training an agent required rebuilding its loop inside the RL framework.

Real harnesses have outgrown that assumption. Coding agents such as mini-SWE-agent, OpenHands, OpenCode, Claude Code, and Codex each bring their own context management, tool protocols, execution logic, and dependencies, as do general-purpose agent systems. Rebuilding one for training is expensive, and the rebuilt agent may no longer behave in the same way as the deployed agent.

Agent Lightning takes a different route. It places an LLM proxy between the agent and the model. The agent continues to run as before: simply point the endpoint that previously called the model API at Agent Lightning, and the training framework can observe and record its model calls. In v1.0, the researchers go further and formally define this paradigm as Harnessed Agentic RL: whichever agent harness is used in deployment is the harness that takes part directly in reinforcement learning during training (Figure 1).

A core difference between Harnessed Agentic RL and traditional agentic RL is that the environment interaction loop is handled by the agent harness rather than the training framework. The training system can only observe a series of LLM request and response pairs, so a single rollout may be split into a variable number of training samples. This brings four key challenges:

A video series with Sinead Bovell built around the questions everyone’s asking about AI. With expert voices from across Microsoft, we break down the tension and promise of this rapidly changing technology, exploring what’s evolving and what’s possible.

In system design, Agent Lightning v1.0 treats simplicity as its first principle. The entire framework is about 3,500 lines of code, with three core components: the API Gateway, the Rollout Controller, and the Customized Trainer (Figure 2).

The API gateway stores rollouts, models, and events, and serves as an OpenAI-compatible LLM proxy. It links every model call from the harness to its rollout and records the prompts, responses, and log probabilities that training needs. The rollout controller starts and manages agent execution, either as local processes or as standard Kubernetes jobs, keeping agent execution separate from the trainer. The customized trainer, built on verl, creates rollouts, waits for them to finish, collects samples, and assembles the final training samples through a sample adapter. As a result, for an existing agent harness, simply pointing the model endpoint at the Agent Lightning proxy is usually enough to connect quickly to RL training.

Rollout times vary widely across agents. Synchronous RL waits for the slowest agent in a batch and leaves GPUs idle, while fully asynchronous RL raises utilization but needs separate GPU pools for rollout and training. In response, Agent Lightning v1.0 introduces Collocated Async RL, which lets rollout and model updates share the same set of GPUs.

Once the system has collected enough rollouts, the update begins: the API Gateway pauses accepting new requests and waits for requests already in progress to finish, and rollout resumes after the update completes. The entire state transition is transparent to the external agent harness. In experiments, this approach achieved about a 2x end-to-end speedup over synchronous RL while using fewer GPUs than conventional asynchronous RL (Figure 3).

Collecting enough rollouts means running many agents at once, which consumes substantial CPU, memory, and compute resources. Other Harnessed Agentic RL frameworks often host those agents on commercial sandbox services such as Modal Sandbox or E2B, where cost climbs quickly with scale. Instead, Agent Lightning v1.0 runs them as standard Kubernetes jobs, reusing existing self-managed clusters, cloud Kubernetes, or local infrastructure (Figure 4). Existing compute resources are used more efficiently, large rollouts cost less, and the whole pipeline stays open source and reproducible.

To test the approach, researchers built a full pipeline on SWE-smith, mini-SWE-agent, and Qwen3.5-9B, covering data cleaning, environment construction, reward-hacking safeguards, and RL training. The training set holds about 6,000 samples and needs no large-scale compute. RL training alone raised Qwen3.5-9B from 41.8% to 56.4% on SWE-bench Verified, a gain of 14.6 percentage points.

The coding agent experiments further confirm the earlier analysis of two challenges: advantage calculation and loss normalization. Compared with sample-level handling, rollout-level advantage combined with rollout-level normalization achieves a higher validation reward and keeps policy entropy more stable during training (Figure 5).

Research Software Development Engineer II

Principal Research SDE Manager
