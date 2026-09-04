---
url: https://www.together.ai/blog/thunderagent
title: ThunderAgent: 2x Faster Agentic Inference for Synthetic Data Generation at Scale
site: together
date: 
scraped_at: 2026-09-04T21:14:02+00:00
---

Summary

We introduce ThunderAgent, a system for high throughput agentic inference. By introducing a novel program abstraction for agentic LLM request scheduling, ThunderAgent achieves up to 2.5× higher single-node throughput in our synthetic data generation pipeline, and delivers 2.4× speedup on an 8-node cluster with near-linear throughput scaling with respect to GPU nodes.

Key Results

→ More than 2× single-node throughput, with roughly 10× lower P50 latency at high concurrency

→ 2.4× speedup on 8 nodes, near-linear scaling from 16 to 64 GPUs

→ Drop-in: one program_id field, OpenAI-compatible, works with your existing engine-level optimizations (like speculative decoding)

ThunderAgent was accepted to ICML 2026 as a Spotlight paper.

This paper was a collaboration between researchers at Georgia Institute of Technology, the University of Illinois Urbana-Champaign, Carnegie Mellon University, and Together AI.

LLMs are increasingly deployed as agents. Systems like Claude Code, Codex, and OpenClaw reason, call tools, read results, and reason again, often for dozens of turns before completing a task. Training these agents requires large scale synthetic data generation, since natural web corpora do not contain multi-turn, tool-using agent trajectories. To generate agentic datasets like our recently released

, we need to run agentic inference at high concurrency.

However, existing inference engines schedule at the request level, where each LLM call is an independent unit with no awareness that it belongs to a longer, multi-turn workflow. When an agent pauses for a tool call, its KV cache can be evicted to make room for other requests, only to be recomputed from scratch when the agent resumes. This creates fundamental inefficiencies in engines such as SGLang, vLLM, and TensorRT-LLM when serving agentic workloads at high concurrency, including KV cache thrashing, imbalanced workloads across mutli-nodes, and resource waste in tool management. In this blog, we focus on the most critical: KV cache thrashing. We refer readers to our paper for a more comprehensive discussion.

An agentic workflow alternates between two phases: the GPU-heavy

phase where the model is generating tokens and the GPU-idle

phase where the agent is waiting for a tool like a compiler to return. When hundreds of agents run concurrently, their KV caches grow at each phase, competing for limited GPU memory. Under this memory pressure, a traditional inference engine like vLLM would evict KV caches using a simple policy: least recently used, regardless of whether that cache will be needed again in seconds.

The result is a vicious cycle. Agent A pauses for a tool call. Its KV cache gets evicted to make room for Agent B's prefill. When Agent A's tool returns, the engine must recompute Agent A's entire conversation history from scratch, which in turn evicts cache for Agent C's context. At high concurrency, this cascade of evictions and recomputations can lead to severe throughput and latency degradation. We refer to this problem as

.

Simply throwing more GPU nodes at the problem doesn't fully resolve it. Existing multi-node routers such as SGLang Model Gateway pin each agent to a fixed node to preserve cache locality. But because agentic context lengths grow unpredictably, some nodes are assigned agents with long contexts that exhaust memory, while others sit idle with capacity to spare. The overloaded nodes still face thrashing.

Adopting KV cache offloading doesn't resolve the problem either. Strategies like LMCache and HiCache offload KV caches to CPU memory or disk, which expands total cache capacity but only delays thrashing. When the working set of concurrent agents exceeds all available storage tiers, evictions resume and the same vicious cycle returns.

Request-level engines cannot fix thrashing on their own, because they never see that a series of LLM calls belongs to one longer workflow. ThunderAgent adds that missing view. ThunderAgent is a lightweight scheduling layer that sits between agentic clients and inference backends. It abstracts each agentic workflow as a schedulable program, tracking its execution phase, KV cache footprint, and node placement.

ThunderAgent mitigates KV cache thrashing through program-level scheduling: it monitors the memory pressure on each node and selectively pauses low-priority workflows to reduce the number of programs competing for cache. With fewer concurrent programs, the remaining active workflows achieve significantly higher KV cache hit rates and lower latency. When paused workflows are ready to resume, ThunderAgent routes them to the node with the most available capacity through a global waiting queue, balancing load across the cluster.

For multi-node deployment, ThunderAgent replaces session-based static node-pinning with a global waiting queue. When a paused workflow is ready to resume, ThunderAgent routes its requests to the node with the most available capacity. Such routing strategy balances the tradeoff between KV cache locality and multi-node workload balance, achieving both efficient cache utilization and even load distribution across the cluster.

Beyond multi-node scalability, ThunderAgent is also compatible with KV cache offloading, treating KV cache capacity across GPU HBM, CPU RAM, and disk storage as a unified pool. While offloading alone only delays but does not eliminate thrashing, ThunderAgent's pausing and resuming strategy remains effective regardless of the underlying storage tiers.

We integrate ThunderAgent into our internal synthetic data generation pipeline, the same harness and infrastructure behind datasets like CoderForge, where hundreds of LLM coding agents interact concurrently with sandboxed environments over dozens of turns to generate trajectories.

We compare ThunderAgent against the default scheduler in SGLang on a single 8×H100 node with KV cache offloading using HiCache. At batch size 192, SGLang’s throughput drops to 390 token/s with a mean latency of 65s, while ThunderAgent achieves 803 token/s throughput with mean latency of 10.6s, expanding the Pareto frontier in throughput-latency tradeoffs.

We extend the evaluation to multi-node clusters, comparing against

on up to 8 H100 nodes. As shown in the graph, ThunderAgent’s throughput scales near-linearly with respect to the number of GPU nodes, growing from 671 to 2,248 steps/min as we scale from 16 to 64 GPUs. Meanwhile, the speedup of ThunderAgent over SGLang Gateway widens with cluster size, from 1.79× at 2 nodes to 2.39× at 8 nodes. While SGLang Gateway causes increasing memory imbalance as the cluster grows, ThunderAgent's global waiting queue routes resumed workflows to whichever node has available capacity, reducing memory imbalance across the cluster.

The core shift is treating each agent workflow as a program rather than a series of unrelated requests. That single abstraction is what lets ThunderAgent stop KV cache thrashing, balance load across nodes, and stay compatible with the offloading and decoding optimizations you already run. It is also what makes the system practical to adopt: workflows are tracked end to end without changing your inference backend.

Beyond our own synthetic data pipeline, ThunderAgent has been adopted by open-source frameworks including SkyRL and NVIDIA Dynamo. We think the program abstraction is the right foundation for the next generation of agentic inference systems, and we are excited to see what the community builds on it.

ThunderAgent is designed to drop into your existing stack. It interfaces with inference backends through OpenAI-compatible endpoints, and works alongside the inference optimizations you already use, such as quantization and speculative decoding. The only client-side change is adding a `program_id` field to identify which program each request belongs to.

ThunderAgent is open source and ready to use:

If you're running large-scale agentic workloads, ThunderAgent can help you get a free lunch speedup from the same hardware. Try it out, and let us know how it goes.
