---
url: https://www.together.ai/blog/adaptive-learning-speculator-system-atlas
title: AdapTive-LeArning Speculator System (ATLAS): A New Paradigm in LLM Inference via Runtime-Learning Accelerators
site: together
date: 
scraped_at: 2026-09-04T21:12:39+00:00
---

At Together AI, the AI Native Cloud, we’re obsessed with performance. Making large language models faster, cheaper, and more efficient is not a one-trick problem — it requires optimizing along multiple axes. That is the philosophy behind

, our suite of inference innovations that draw from research in algorithms, architectures, and modeling recipes. We’re excited to introduce the AdapTive-LeArning Speculator System (ATLAS), the first speculator of its kind that gives automatic performance improvements without any manual tuning.

ATLAS offers a new way of doing speculative decoding — one that dynamically improves at runtime — and it fits seamlessly alongside our other Turbo techniques like the proprietary

or

. But why create an adaptive-learning speculator system?

Standard speculators are trained for general workloads. Custom speculators are trained on your specific data, but only for a specific snapshot in time. However, as the workload evolves (codebase grows, traffic patterns shift, request distributions change), even highly customized speculators can fall behind. In contrast, ATLAS evolves automatically with usage, learning from both historical patterns and live traffic to continuously align with the target model’s behaviors in real time. This means the more you use our inference service, the better ATLAS will perform!

Built on top of Together Turbo Speculator, ATLAS reaches up to 500 TPS on

and up to 460 TPS on

in a fully adapted scenario — 2.65x faster than standard decoding, outperforming even specialized hardware like Groq (Figure 1).

Speculative decoding is one of the most powerful levers for accelerating inference.

Instead of having the target model generate every token step by step, a faster

(also known as the

)

proposes multiple tokens ahead, and the target model

them in parallel in a single forward pass. The verification process ensures that the quality of the output matches the distribution of non-speculative decoding, while achieving speedups by accepting many tokens at a time.

The overall speed is influenced by the acceptance rate

(i.e., how often the target model agrees with the drafted tokens from the speculator) and the relative latency

of the draft versus the target. Typically, larger speculators with more parameters yield higher acceptance rates due to their higher capacity but are slower to generate draft tokens. Progress therefore comes from both sides: aligning draft and target models to increase

(training objectives, data, and algorithms) and designing draft models/kernels that keep

low while maintaining

(sparsity, quantization, lightweight & kernel-efficient architectures). The sweet spot is where a high

meets a low

, minimizing end-to-end latency.

‍

At Together AI, the Turbo team has developed high-performance speculators that have achieved

by drawing on advances across architecture, sparsity, algorithms, post-training recipes, and data [1-9]. We’ve built a

that determines the optimal speculator architecture (width/depth, lookahead, sparsity/quantization, KV reuse) and a

that brings up speculators for the largest and most challenging open-source targets quickly and reproducibly (e.g., DeepSeek-V3.1 and Kimi-K2). For instance, while Kimi ships without a ready-to-use speculator, we can train and deploy one rapidly and take Kimi from ~150 TPS out of the box to 270+ TPS on the same hardware and batch settings, while preserving target-model quality (see Figure 1, yellow bars).

This pipeline powers Turbo Speculators that deliver state-of-the-art decoding latency, and it sets the stage for what comes next:

that adjusts token drafting to the workload in real time.

At Together AI, we power a broad range of inference workloads. But today’s speculative decoding methods are constrained to using a

speculator, trained on a fixed dataset. Once deployed, the speculator cannot adapt, leading to degrading performance if the input distribution evolves. This problem is particularly pronounced in serverless, multi-tenant environments, where input diversity is sky-high. New users continuously arrive, and bring with them unique workloads that the fixed speculator may not have seen during training. Furthermore, these speculators typically use a

, predicting the same number of tokens regardless of the speculator’s confidence. Put simply,

.

To address these limitations, we designed the

with two cooperating speculators, as shown in Figure 3:

The static Turbo Speculator serves as an always-on speed floor: it is trained on a broad corpus and remains stable across workloads, so TPS does not collapse when traffic shifts or the adaptive path is cold. In ATLAS, we use it to jump-start speed and provide a fail-safe fallback—if confidence drops or drift is detected, the controller shortens lookahead or routes back to the static path to preserve latency while the adaptive speculator relearns.

.

We know from our previous studies that a

trained on samples from real traffic that mirror expected usage delivers an additional speed boost. The Adaptive-Learning Speculator enables us to be even more customized in real time. For instance, during a vibe-coding session, the adaptive system can specialize a lightweight speculator for the relevant code files being edited and not seen during training, further increasing the acceptance rate and decoding speed. This kind of on-the-fly specialization is hard to achieve with static speculators.

. Reinforcement learning (RL) alternates between two phases: (1) a rollout phase, where the current policy generates trajectories and receives rewards, and (2) an update phase, where we use the rewards to update the policy. In practice, rollouts are often the bottleneck, accounting for roughly 70% of total wall-clock time

. In general, because the policy distribution shifts throughout training, static speculators quickly fall out of alignment with the target policy, resulting in sub-optimal throughput.

ATLAS addresses this by adapting online to the evolving policy and the specific RL domain, maintaining alignment and reducing the overall rollout time. The domain-specific, iterative nature of RL further enables rapid adaptation, yielding sustained and growing speedups. As shown in Figure 4, applying ATLAS to the RL-MATH pipeline produces increasing speedups as training progresses.

The Adaptive-Learning Speculator System is a core component of the broader Turbo optimization suite, where each layer of optimization compounds the benefits of the others. As illustrated in Figure 5, performance progressively improves through near-lossless quantization (calibrated to preserve quality), the Turbo Speculator, and finally the Adaptive-Learning Speculator System. Additional optimizations in the suite include TurboBoost-TTFT (not shown) for reducing time-to-first-token latency, further contributing to end-to-end acceleration.

. When the input distribution is narrow and outputs closely echo previously seen tokens, the adaptive system specializes quickly. In this scenario, the controller becomes confident in utilizing more tokens from the lightweight speculator and lengthens lookahead tokens. This yields consistently higher TPS than static or one-off custom speculators can maintain. As shown in Figures 1 and 5, once fully adapted to Arena-Hard traffic, DeepSeek achieves up to 500 tokens per second for batch size 1 on 4 B200 GPUs, delivering a 400% speedup over the FP8 baseline (improvement from 105 TPS to 501 TPS).

We build on a vibrant ecosystem of research in speculative decoding—from early

methods like

and

, to structured variants including

,

, and the

series. More recent studies made speculation adaptive:
