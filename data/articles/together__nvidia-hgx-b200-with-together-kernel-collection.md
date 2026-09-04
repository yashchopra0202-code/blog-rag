---
url: https://www.together.ai/blog/nvidia-hgx-b200-with-together-kernel-collection
title: Together AI Achieves 90% Faster BF16 Training with NVIDIA Blackwell Platform and Together Kernel Collection
site: together
date: 
scraped_at: 2026-09-04T21:12:44+00:00
---

Today we are announcing immediate access to

accelerated by the

platform, and an accompanying AI acceleration stack optimized for the latest GPU architecture.

Together GPU Clusters featuring

are turbocharged with Together Kernel Collection to deliver unprecedented performance: 90% faster training than NVIDIA HGX H100, achieving 15,200 tokens/second/node on a training run for a 70B parameter model.

Our research team has achieved these incredible speed-ups by leveraging NVIDIA Blackwell’s advanced features using the open-source ThunderKittens framework. We developed custom FP8 kernels that take full advantage of Blackwell’s 5th-generation

and dedicated on-chip memory to produce attention kernels that run 1.8x faster than FlashAttention-3.

Get your free week on a dedicated NVIDIA HGX B200 GPU Cluster starting March 1. Work with NVIDIA and Together AI Reseaarch teams to optimize performance.

‍

We are deploying tens of thousands of NVIDIA HGX B200 servers and

rack-scale solutions with NVIDIA Quantum-2 InfiniBand networking – including the

we announced previously. All Together GPU Clusters feature the highest-performance NVIDIA NVLink within a node and NVIDIA Quantum-2 InfiniBand networking across nodes, providing the scale and performance needed to build and deploy the next generation of AI reasoning models and agents.

Our team is eager to work hand in hand with yours, forging the frontier of AI, together.

- Tri Dao, Together AI Chief Scientist and FlashAttention creator

To benchmark the performance of

with NVIDIA HGX B200, we tested the training speed of a 70B parameter Llama-architecture model, using an optimized version of

combined with the Together Kernel Collection (TKC). The result?

🚀 A 90% improvement in training throughput over NVIDIA HGX H100.

Compared to optimized software running on the previous generation of accelerators, which processed 8,080 tokens/second (BF16) per NVIDIA HGX H100, we reached 15,264 tokens/second/GPU with NVIDIA HGX B200 — a 90% jump in training speed!

By leveraging state-of-the-art distributed training algorithms and hardware-aware optimizations, Together AI ensures that AI teams can train massive models faster and more efficiently. And, with additional software optimizations coming soon, performance will only get faster from here on out.

At Together AI, our goal is to accelerate AI by optimizing every layer of the AI stack – and that’s why we invest significant research and development resources towards the creation of high-performance kernels. Kernels are the core software programs that run on GPUs, performing critical AI computations such as attention mechanisms and matrix multiplications. By developing optimized kernels, we unlock faster training and inference speeds, reducing costs and improving efficiency.

With the introduction of the NVIDIA Blackwell platform, we now have access to novel hardware features that allow us to push AI performance further than ever before. These include:

To take advantage of Blackwell’s hardware features, Together AI leverages open-source frameworks such as

,

, and

. These frameworks simplify the development of high-performance kernels by using a tile-based abstraction, which efficiently maps key matrix operations onto Tensor Cores — specialized matrix multiplication units that account for over 98% of available FLOPs on NVIDIA GPUs.

In this section, to showcase kernel development velocity on NVIDIA Blackwell platform, we use ThunderKittens, an open-source kernel framework that is a joint-effort between Stanford researchers and Together AI. This framework ensures compatibility with new hardware generations, making it easy to utilize NVIDIA Blackwell. Through our ongoing collaboration with NVIDIA and Stanford researchers, ThunderKittens now supports the Blackwell architecture.

Using ThunderKittens, we have been able to rapidly develop a

for NVIDIA HGX B200 in under two weeks, writing fewer than 200 lines of code. This kernel already matches the performance of

GEMM kernels while achieving more than 2x speedup over H100 FP8 GEMMs.

At Together AI, we are committed to pushing AI performance to new heights through optimized software and hardware integration. If you’d like to read more in-depth technical details regarding how we used all the new Blackwell Platform hardware features to build new kernels, including new attention kernels 1.8x faster than FlashAttention-3, FP4 GEMMs, and more, stay tuned for a blog post regarding our collaboration with our research partners at Stanford. Together AI will continue to push the frontier of generative AI training and inference performance, extracting the highest performance from the platform.

Together GPU Clusters follow the latest NVIDIA Blackwell platform reference architectures including 1.8TB/s NVLink and NVLink Switch, 3.2TB/s Quantum-2 InfiniBand networking, NVIDIA ConnectX-7 HCAs, GPU direct fast storage, and an optimized software stack that accelerates training workloads.

NVIDIA Blackwell is a big step up in GPU architecture, purpose-built for the era of trillion-parameter reasoning models and massive-scale AI workloads. With innovations like 5th-generation Tensor Cores, advanced memory hierarchies, and improved energy efficiency, the Blackwell platform delivers massive performance gains over previous architectures.

NVIDIA HGX B200 represents a major leap in AI compute power, featuring:

The NVIDIA GB200 NVL72 rack-scale platform extends this even further, featuring:

To celebrate NVIDIA Blackwell's arrival, and to help customers understand the performance gains from these new GPUs and Together Kernel Collection, we’re inviting AI teams to apply for a

of

powered by NVIDIA HGX B200 and NVIDIA GB200 NVL72.

🏎️ How the Together AI test drive of NVIDIA Blackwell platform works:

📢

to be among the first to harness the Together Kernel Collection with NVIDIA Blackwell – and take your AI training and inference to a whole new gear.

Request a free test drive of Together GPU Clusters, accelerated by NVIDIA Blackwell GPUs.
