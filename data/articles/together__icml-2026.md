---
url: https://www.together.ai/blog/icml-2026
title: Together AI at ICML 2026: frontier research across the full stack
site: together
date: 
scraped_at: 2026-09-04T21:13:48+00:00
---

Nine papers is a lot to take in as a list. The better way to read them is by where they sit in the stack. Frontier AI is not built at a single layer. It is the product of research that runs from the agent down to the GPU kernel, and a gain at any one layer is wasted if the layers around it cannot keep up.

This is at the core of how we work. From frontier agents at the top to kernels at the bottom, our research touches each one, and each layer feeds the next. The research becomes part of the Together platform, and the production workloads running on that platform point us to the next research problem. Aurora, our ICML paper on adaptive speculative decoding, is a clear example: the same line of work ships today as our ATLAS speculator in production.

Here is this year's work, layer by layer, top down.

The top of the stack: building agents that do real work, and measuring them honestly.

Data-science agents have been hard to measure fairly, every benchmark has its own interface and many of their tasks can be solved without ever opening the data. DSGym standardizes the measurement and closes that loophole.

It puts diverse evaluation suites behind one API with shared abstractions for datasets, agents, and metrics, and runs each task in a self-contained execution environment where the agent has to work with the data rather than recall an answer. On top of the refined existing suites, it adds 90 expert bioinformatics tasks grounded in academic literature and 92 end-to-end Kaggle-style modeling competitions. The same environment then runs in reverse as a training engine: trajectory generation and synthetic query pipelines produce execution-verified data, which we used to train a 4B model into a state-of-the-art open-source data-science agent, with no human labeling. Evaluate honestly, synthesize from the same harness, fine-tune, re-evaluate, all in one framework.

Paper:

Parallel agent workloads stop collapsing under load, and the fix is not a faster model.

The problem is the inference engine has no idea it is running an agent. It treats each step of a multi-turn workflow as an isolated request, inflating latency by up to 7.14x under load. ThunderAgent makes the workflow itself a first-class object the scheduler can reason about end to end. Alongside the throughput gain, it delivers 1.8 to 3.9x faster RL rollouts and up to 4.2x disk savings over state-of-the-art systems.

Paper:

Every prior result at this level relied on closed frontier models behind an API you cannot inspect or run. TTT-Discover reaches it with an open 120B model and one unchanged method, for a few hundred dollars per problem.

The usual recipe for AI discovery is search: prompt a frozen model thousands of times and keep the best sample. TTT-Discover instead runs reinforcement learning at test time on the single problem in front of it, so every attempt becomes training data for the next one and the model improves as it works, and with the same sampling budget plain best-of-N never catches up. The same setup, unchanged, set a tighter bound on a 60-year-old Erdős problem in mathematics (past the previous AI record, which used closed models), discovered a GPU kernel faster than the best prior submission on the GPUMode leaderboard, produced a first-place-level finish on a competitive-programming contest, and set a new high on a single-cell denoising benchmark in biology, all on the open gpt-oss-120b. The code and the record-setting kernels are public.

Paper:

How you train and shape a model: reasoning, fine-tuning, and reinforcement learning.

You can get RL-grade reasoning on tasks that have no checker, like poetry writing or financial analysis, not just math and code.

RL-based reasoning normally assumes a verifier that can score correctness. RARO (Relativistic Adversarial Reasoning Optimization) replaces it with an adversarial game: one model acts both as a policy that produces expert-quality answers and as a relativistic critic, which learns to pick a better response of the two. Pairwise comparison with a tie option is key for training stability. On Countdown, RARO reaches 54.4% accuracy versus 57.7% for RL with a ground-truth verifier despite not using one; by contrast, SFT or iterative DPO do not go beyond 40.7%. The learned critic can double as a test-time reranker that lifts DeepMath from 57.5% to 68.4% at 7B.

Paper:

The win is better answer selection, not more compute.

When you sample many answers with no oracle, scoring each one independently fails, the judge hands almost everything a 10 out of 10 and loses the ability to discriminate. V1 reframes selection as comparison through a near-linear Swiss-tournament verifier. The training recipe, V1-PairRL, teaches a single model to generate and to pairwise-verify its own outputs at the same time, which lifts base accuracy even with no test-time verification at all.

Paper:

Making the math of inference cheaper: speculative decoding, quantization, RL inference.

Speculative decoding that is fast on day 0 and keeps getting faster the longer it runs.

Most deployments train the speculator offline and freeze it, so it is slow to deploy and goes stale as traffic and target models change. Aurora reframes online speculator learning as an asynchronous reinforcement-learning problem running in production: accepted and rejected tokens are the reward signal, the training server updates the speculator continuously, and new weights hot-swap into the server with zero downtime.

Paper:

The systems that train and serve models: disaggregation, batching, scheduling, context parallelism.

You can train at a very long context without a bigger cluster.

Activation memory inside the attention layer caps long-context training, and adding GPUs does not move that ceiling. UPipe processes a few attention heads at a time and reuses the same buffers across stages, cutting peak attention memory by up to 87.5% on a 32B Transformer. The result is 5M tokens on one node, about 25% beyond prior methods, and 8M tokens on two nodes, while matching their throughput. It is a drop-in replacement for DeepSpeed-Ulysses on the same FlashAttention-3 kernels, and the code is open.

Paper:

You reclaim the sparsity that batching quietly destroys, for free.

A Mixture-of-Experts model is supposed to be cheap because each token touches only a few experts, but the moment you batch, that sparsity collapses: At batch size 16, a model where each token wants eight experts ends up loading around 82 of them. OEA's batch-aware routing recovers the sparsity at inference time in two phases, the second of which lets tokens share experts the batch has already loaded, buying back quality at zero latency cost. Accuracy holds flat across AIME24, GPQA, LiveCodeBench, and MATH 500, and there is a single hyperparameter to tune.

Paper:

The bedrock of the stack: where raw hardware becomes usable speed. Built by the teams behind FlashAttention, ThunderKittens, and Megakernel.

We built the first benchmark for multi-GPU kernel generation. It has 87 real distributed workloads, and today's best frontier model solves fewer than a third.

ParallelKernelBench takes 87 problems from production codebases like Megatron-LM, DeepSpeed, NeMo-RL, and TensorRT-LLM, spanning 12 forms of parallelism. Each one asks a model to replace a PyTorch and NCCL reference with a CUDA kernel that uses symmetric memory for direct NVLink communication. Zero-shot, the best model clears 28 of 87. In an agentic loop with compile, correctness, and performance feedback, Gemini 3 Pro climbs from 24 to 35 correct and beats the PyTorch baseline on 26. A handful run faster than anything publicly available. Single-GPU code generation is getting solved. Multi-GPU is where it breaks, because communication, not compute, sets the ceiling.

Paper: https://www.alphaxiv.org/abs/2606.parallel-kernel-bench

All nine papers are at ICML 2026, July 6 to 11, in Seoul. Stop by booth B714 to dive deeper into the work.

We will also be at our booth all week. Stop by to:

1/ Talk through any of the nine papers with the people who wrote them

2/ See the research in production, from agents to production inference

3/ Meet the team and hear what we are working on next

We are hiring researchers and research engineers who want to work across the whole stack, not just one layer of it. See open roles at

, or come find us at the booth.

For everyone else:

, browse the full

, and follow along on X at [@togethercompute] as the deep dives land across the conference.

‍
