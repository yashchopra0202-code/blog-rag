---
url: https://cohere.com/blog/megakernels
title: Inside the megakernel serving engine for North Mini Code
site: cohere
date: 
scraped_at: 2026-09-08T17:08:44+00:00
---

Today, Cohere presents a serving engine for

built around a decode megakernel: BF16 on a single H100, 1.25× - 1.41× faster than vLLM end-to-end. Explore the code behind the serving engine on

Most LLM serving stacks still treat each forward pass as a sequence of kernels: launch QKV, wait; launch attention, wait; launch the MoE, wait. Each launch is fine on its own. The problem is the waiting in between. At small batch sizes, the GPU spends a surprising fraction of every decode step waiting rather than computing.

Autoregressive decoding, especially at lower batch sizes is fundamentally memory-bound. For every decode step, we move a large fraction of memory from HBM while relatively doing less compute. This means the correct question to ask is, how effectively can we use memory bandwidth and not the flops. Take North Mini Code which is a 30B model with 3.3B parameters active per token, which in BF16 means streaming 6.6 GB of weights during every decode step, plus roughly 0.5 GB of KV cache at 8K context. An H100 delivers 3.35 TB/s of bandwidth through HBM, putting the Speed-of-Light (SoL) at about 470 tok/s. vLLM serves this model at 185 tok/s, merely 39% of SoL.

Megakernels have been getting attention lately as the way to close that gap: instead of a hundred small kernels, run the entire forward pass as one persistent kernel. Starting from the pioneering work by

, whose design we recap below, numerous follow-up works have been released, achieving various levels of speedup. Existing work has gone mainly in two directions: compilers that generate megakernels automatically, and standalone demos that measure decode speed at batch size 1.

We take one step further. This post presents what we believe is the first fully fledged serving system built around a decode megakernel. It supports everything a real server needs: continuous batching, paged attention, and ragged sequence lengths, all behind an OpenAI-compatible endpoint with tool calling. Point OpenCode at it and you can code with it.

On batch size 1, our megakernel reaches 292 tok/s, or 62% of SoL — 1.58× faster than vLLM. That margin holds across batch sizes and out to 256K of context, with no measurable loss of accuracy.

We also found that megakernels are much easier to write than their reputation suggests, so we include a recipe for porting kernels you already have into one. Ours is a single CUDA file: no compiler, no new programming paradigm, no exotic abstractions — just ordinary tiled GEMMs and ordinary paged attention, restructured to fit a single calling convention.

A GPU is roughly 100–150 independent processors, called SMs (streaming multiprocessors), that all run the same program — a

— on different pieces of data. A megakernel is a single persistent kernel that runs an entire forward pass: we launch exactly one threadblock per SM, and it stays resident for the entire decode step. Instead of receiving work from the driver, each block reads a

— a list of small pieces of work it should execute, prepared on the host and sitting in global memory. Instead of kernel boundaries encoding the data dependencies, dependencies are expressed as explicit counters in global memory that tasks increment when they finish and spin on when they need an input.

The result is that the unit of scheduling shrinks from an entire operation to one tile of one operation, and the unit of synchronization shrinks from the whole GPU to the specific producers a task depends on.

Inference engines typically launch one kernel per operation — RMSNorm, QKV, attention, MoE, and so on — and most optimization effort goes into making each of those kernels as fast as it can be. That works well for training and prefill, where the workload is large compute-bound GEMMs and every kernel has enough work to saturate the SMs.

Decode is the opposite regime: it is bound by memory bandwidth and by latency. A decode step is mostly GEMVs with low arithmetic intensity, so its speed is determined by how fast weights can be streamed from HBM into shared memory. Anything that keeps weights from moving is lost time, and a kernel-per-operation approach has several places where they stop moving. Together those stalls account for most of the 61% of bandwidth that a typical inference engine leaves unused.

The simplest benefit comes from

. Between two consecutive kernels, every SM must finish before any SM can start the next one, and the driver has to dispatch the next grid. For a decode step made of dozens of small kernels per layer, those gaps add up. A megakernel pays that cost once per step rather than once per operation. We list three more benefits that matter more for this model, in rough order of impact:

Suppose a kernel has 200 tiles of work to do and the GPU has 132 SMs. The first 132 tiles run in parallel; the remaining 68 run in a second wave while 64 SMs sit idle. The kernel takes two waves' worth of time to do 1.5 waves' worth of work, and the smaller the kernel, the worse that rounding gets. This is not something we can fix by dividing the work more evenly. GEMM tile shapes are constrained by the matrix dimensions and the kernel design, so the total tile count rarely lands on an exact multiple of the SM count.

In a megakernel there is no boundary to round up to: a tile whose inputs are ready starts on whichever SM is free. North Mini Code gains more from this than most architectures because it uses

: attention and the MoE feed-forward are computed from the same normalized input and are rejoined only by a fused residual add + RMSNorm at the end of the layer, so neither attention nor the MoE needs each other's output.

With a megakernel, we can "backfill" the idle SMs with ready work. The parallel transformer layers allow us to perform backfilling in a more aggressive way: whenever possible, we

place the tasks that are likely ready to run on the idle SMs. The detail of the placement is described in the task scheduler section. In the figure below, we compare an MoE decode layer run by a conventional serving stack and a megakernel.

SMs do not always finish work at the same time, even when workload is identical. A kernel boundary is a full-grid barrier, so the slowest SM sets the pace for all of them. For example, if attention is split across 4 key/value groups and one group finishes early, that SM idles until the other three catch up, even though the data its next operation actually needs is already in memory. Fine-grained barriers drop the false dependency: O-proj for a given KV group starts as soon as

attention output lands. Similarly, an MoE down projection task can start whenever the up projection task of the corresponding expert is completed, without the need to wait for all experts’ up projection.

Weights are immutable — they do not depend on this step's activations at all. A task can therefore start streaming its weight tiles from HBM into shared memory

its activation dependency has been satisfied, which a kernel boundary would forbid. We use this most aggressively for the router and QKV projections, which prefetch their weights during the tail of the previous layer's O-proj, before RMSNorm has even run, to harvest bandwidth that would otherwise go unused.

Our design borrows a lot of insight from the pioneering post on Hazy Research referenced earlier , which fused a Llama-3.2-1B forward pass into a single kernel and reached 78% of an H100's memory bandwidth at batch size 1, against roughly half that for vLLM and SGLang. Three of their ideas are crucial to us:

Our implementation differs from their megakernel in a few ways. Our GEMM implementation relies heavily on tensor core instruction, even for batch size 1 because we found that wgmma is slightly faster in our cases compared to CUDA core and reduces register pressure.

One other difference is that we do not use shared memory paging to implement weight prefetching. We initially experimented with shared-memory paging, which allows memory loads to begin before the previous task releases its buffers. In practice, though, the bookkeeping is complex, introduced a steady source of bugs, and had high overhead that outweighed the benefit. Every opcode instead gets its own warp-specialized pipeline with its shared memory layout statically at compile time, and we get the overlap from two cheaper places.

An MoE GEMM task walks a list of tiles, and the pipeline carries its stage phases across the whole list instead of draining and refilling the pipeline at every tile boundary. Within the MoE GEMM, the next tile's weights are already in flight while the current tile is still on the tensor cores or epilogue. Because it is the same operation with the same shared memory layout, shared memory paging reduces to a simple multi-stage pipeline. This kind of prefetch shares the same spirit as persistent grouped GEMM kernels.

Weights are immutable, so the producer warp issues its weight-tile loads

the cross-SM wait for activations; in the pseudocode (Listings 1) shown later in the post,

sits above

. MoE down projection is one such example case: its expert weights start streaming from HBM while up/gate is still computing the hidden state that down will consume. Therefore a task blocked on its inputs is still moving bytes. The other example is QKV and router prefetching before RMS norm completion.

We also put substantial effort into scheduling. Most tasks follow a host-built static schedule that we can tune precisely; attention and MoE use local work stealing to balance the runtime-dependent work from continuous batching and routing. We return to this below.

The entire megakernel can be seen as various smaller kernels stitched together by a common calling convention—each smaller kernel must be implemented with exactly 3 warp groups (each warp group has 4 warps) containing 8 consumer warps, 1 controller warp, 1 producer and 1 storer warps, where each warp is subjected to its own register requirement. Additionally, each smaller kernel must read its “parameters” from a fixed sized task descriptor. We feel this kind of convention is analogous to application binary interfaces (ABI) as in compilers and operating systems. We would use the term

to describe the convention throughout the post.

Let's take a GEMM as an example to understand how the ABI works.

What keeps this writable by hand is that every operation, not just GEMM, obeys that ABI: what a task is, what shape it runs in, and how it signals that it is done. Once all operations follows the same ABI, assembling them into a megakernel becomes very manageable. The rest of this section unpacks those three things.

The megakernel does not invent new operations. It takes the usual decode graph — QKV, attention, O-proj, router, MoE, residual/RMSNorm, LM head — and lowers it into a list of small tiled

. Sixteen opcodes cover the whole decode step:

O-proj, the router, the dense FFN, the LM head, and both MoE expert GEMMs run the same warp-specialized body: the producer streams weight and activation tiles into a shared-memory stage ring, the consumers accumulate on tensor cores, the storer writes the output tile and arrives on a barrier. What changes per opcode is a short list of per-op details — which tensors, which barrier to wait on and which to signal, whether the epilogue fuses SiLU-and-multiply, whether the store is a split-K reduction. QKV is that same pipeline with RoPE applied in-register before writing back to HBM. The MoE drains are that same pipeline with a different way of picking the next tile: they claim work from a queue instead of reading the coordinates off the descriptor.

As a result, adding new GEMM task is a small edit rather than a new kernel. We do not rewrite the load/math/store loop, but only fill in those details.

Each task descriptor is 32 int32 fields, written by the host encoder into a per-SM buffer. Field 0 is the opcode; the rest are op-specific: which layer, which output tile, which split-K slice, how many K-tiles to walk, and — the important part —

The device side is straightforward. One warp per block acts as a

: it prefetches upcoming descriptors into a small shared-memory ring, so an SM never stalls on waiting for task descriptors. The other warps pop tasks off that ring and execute them.

Every task, regardless of opcode, runs under the same threadblock shape. 12 warps, organized as 3 warpgroups:

Most of it follows the standard producer/consumer warp-specialization pattern from a standalone Hopper GEMM. The megakernel's contribution is that every opcode — attention and RMSNorm included — uses this same shape, so an SM that just finished a QKV tile can run an attention slice next without changing how many warps it has or the role of each warp.

The roles are compile-time tags, not runtime branches. Each operation body is templated on the role so

deletes the unreachable code at compile time. That lets us write producer, consumer, and storer in one function, the way a normal GEMM is written, while each warp only keeps the path it actually runs.

The controller never enters that function. It has its own loop, whose only jobs are to prefetch the next descriptor into a small shared-memory ring and to tell the workers when a slot is ready. One small caveat is that workers cannot use

for synchronization between themselves— that would wait for the controller warp that runs independently of workers — so they join among themselves on a named barrier (

) that excludes the controller.

Here is an overview of a GEMM task implemented in the megakernel. If you have written a warp-specialized Hopper kernel, you would probably find the structure familiar. The MoE drain is that same task, called in a loop over tiles claimed from a queue.

Listings 1: We demonstrate how to implement a GEMM task in megakernel. The overall structure follows a standard warp specialized GEMM on Hopper.

The

branches are the compile-time tags from above, not a runtime switch. The two lines that would not appear in a standalone kernel are

and

— the cross-SM counters carried in the descriptor.

sitting above the wait is the other optional megakernel-only move.

The controller stays one descriptor ahead of the workers without ever joining their barrier. Attention, routing, and the MoE drains fill in the same producer / consumer / storer slots; only the

in

changes. The friction of putting a kernel you already have into the megakernel is those two barrier calls plus this wrapping loop instead of a new programming model.

As inspired by Hazy Research, our barriers are implemented as counters in global memory.

Listings 2: We implement barriers as counters in global memory. Waiting threads do a spin wait until dependency is satisfied.

That is the entire dependency mechanism. A task waits on a single

, not on a specific upstream task, which makes both signalling and waiting for dependencies cost O(1) time, regardless of fan-in and fan-out. The fences are crucial to ensure there is no data race across SMs that silently leads to data corruption.

A megakernel sounds like a full rewrite. In practice, the ABI keeps the work contained: once an operation follows the common threadblock shape and descriptor format, it plugs into the megakernel as every other task. The performance-critical logic can be reused from existing kernels.

The recipe we would give someone starting from an existing kernel library:

The hard part is step 3. A counting barrier releases when

threads arrive without checking

threads those were, so one opcode that arrives the wrong number of times can let warps drift onto different tasks and deadlock much later. Barrier accounting needs explicit invariants and careful testing.

A descriptor format, a block shape, and a counter protocol form the whole integration contract. That makes adding a new operation an engineering task with a clear boundary, rather than a new kernel architecture project.

After we implemented the megakernel itself, we need to determine how to assign tasks to each SM and in which order those tasks should be executed. This assignment is referred to as the

. A task scheduler takes in the task graph and outputs the exact list of tasks for each SM to execute sequentially. In fact, we have a lot of freedom in designing the schedule. Fine grained barriers only ensure correctness of the megakernel by making sure a task begins only after its inputs are ready. We can shuffle tasks around as long as the schedule does not result in circular waits. While different schedules produce the same output, they change the throughput in a considerable way.

Our scheduler is mostly static, with dynamic work stealing for a few operations.

The host builds named waves for each layer (

, …), chooses an order, flattens them into one task list, and deals task

to SM

. The current order puts the router and route setup ahead of attention:

That ordering gives the MoE branch a head start, so it can schedule the computationally non-intensive routing with the heavier QKV GEMM to better utilize SMs. Beyond that simple picture, the effect of a schedule is hard to isolate. Changing one wave changes when its dependents become ready, which tasks share an SM, and how HBM bandwidth is allocated between tasks. Those choices interact across the whole layer.

Our experiments show that schedule matters. We ran two 8K input length, uniform-routing ablations that change only wave order.

After attention begins, MoE up/down runs before attention combine. The rationale is to keep ready work from both branches available, so SMs spend less time waiting:

Launch attention combine and O-proj before any MoE GEMM, while still allowing router to start early

All of these schedules produce correct outputs. We also tried dependency-affinity placement: put a task on the same SM as a producer it depends on, hoping to reuse cache and reduce cross-SM handoffs. It slowed the kernel by 1–2%, so the released version uses naive round-robin placement. The table shows measured effects; a complete causal model for why one ordering or placement wins remains open.

Full attention reads vastly different lengths of KV for each live request, and the router decides how many tokens each MoE expert receives. Those tile counts only become known during the step.

The split is deliberate. The static schedule fixes most of the task order and placement, giving us the control needed to tune performance — as the wave-order ablation above shows. Local work stealing handles only the load imbalance that the host cannot know ahead of time. The static task list reserves a fixed number of small

tasks; an

or

claimer atomically steals the next item from its stage's shared queue and executes it until the queue is empty. Attention claimers steal attention tiles, and MoE claimers steal MoE tiles. The number of claimers controls parallelism, while the current attention queue reflects the live requests in the batch. This keeps the static schedule stable and balances the variable work without rebuilding the whole list on every batch change.

The following task graph below puts the static waves, fine-grained dependencies, and locally claimed stages in one view:

Early in the project, while targeting a dense model, we built several more sophisticated schedulers. One was a greedy, topology-aware scheduler that estimated each task's cost from its memory reads. We also tried a brute-force search that selected the best schedule from hundreds of random candidates. Both delivered about 10% more throughput than plain round-robin on that workload. MoE changed the problem: routing makes the amount and placement of its work dynamic, so those dense-model schedules did not transfer cleanly. We ultimately settled on the simpler round-robin with a tuned wave order, plus the local work stealing described above. Nevertheless, we plan to revisit those more complicated schedulers should the simple round-robin proven insufficient for megakernels running on Blackwell GPUs or narrower quantization types such as NVFP4 or FP8.

The server has two long-lived host-side threads. A Python thread serves as the control plane: it accepts requests, runs prefill, and manages KV capacity and batches. A native C++ thread owns decode for maximum performance. These two threads operate in an interleaved manner: Python pauses C++ to prefill or change active batch size.

This handoff exists because the megakernel runs a task list built ahead of time: tile counts, barrier indices, and which slot a tile belongs to are already baked in. Python therefore parks decode before it admits, retires, or reshapes a batch, then C++ resumes with a schedule that matches the new batch size and context. The figure shows the state each side owns and how the schedule changes:

C++ owns the continuous decode loop: it updates KV positions, clears per-step state, selects the schedule, launches the megakernel, samples, and streams the resulting token. It repeats that loop while there are active requests. Python owns everything that changes the batch: accepting a request, running its prefill, assigning or evicting a slot, and switching to a smaller batch size.

The

arrow is the handoff between those two owners:

Parking is the ownership boundary for mutable batch state. Python changes per-request metadata, token buffers, KV page tables, and possibly the pointers for a new batch size while C++ waits. C++ snapshots that state only after resume, then owns it for the next decode step. This keeps the megakernel from observing a half-updated batch. The current trade-off is simple: prefill pauses decode, so the engine does not mix prefill and decode on the GPU yet. When no requests are active, C++ parks on its own and Python wakes it after an admission.

From the outside this is an OpenAI-compatible server with streaming, prefix caching, and tool calls.

These are limits of the current implementation, not of the design. We plan to fill them in.

All numbers are on a single H100 (132 SMs) running North Mini Code. The baseline is vLLM v0.24 with the FA3 attention backend and the Triton MoE backend, prefill disabled. Both engines decode against a synthetic KV cache so that the comparison isolates decode compute from prefill. We measure the decode throughput over 1K output tokens.

We report two benchmark settings, and the difference between them is quite informative.

At 8K context, normalized to vLLM at each batch size:

First, for uniform routing, the speedup is largest when there is most pipeline bubbles. At batch size 1, there is least work per request. As such a large fraction of GPU time is spent on pipeline bubbles and between kernel boundaries. As batch size grows, the fraction of pipeline bubbles to total time decreases, shrinking the gap.

Second, the speedup depends on the expert distribution. At batch size 8 the megakernel is 1.32× faster with the real expert distribution and 1.14× faster under uniform routing. Real requests often choose the same experts, leaving the active-expert set sparse. The MoE then does less total work, so pipeline bubbles make up a larger share of the step; those are the gaps where the megakernel can eliminate. Uniform routing spreads tokens across many experts, leaving more MoE work and fewer bubbles to recover. Synthetic uniform routing therefore understates megakernel speedup on real traffic, and we report it here as the harder case.

The advantage also holds across context lengths. We show BS=4 and BS=8 below.

The microbenchmark isolates decode. This test runs the full server at batch size 8: real prompts enter through the API, prefill runs, requests finish at different times, and the server continually filling the batch. Each engine generates a slightly different number of tokens, so total wall time alone is not a fair comparison. We report both wall time and average decode throughput.

The end-to-end gain is 1.25× - 1.41× in average decode throughput, smaller than decode-only for two reasons: prefill still uses ordinary PyTorch kernels and pauses decoding, expert routing changes from batch to batch, and the active batch size varies during serving so the megakernel's speedup is not constant.

We also checked that the serving path preserves model quality. The table compares the megakernel server with the vLLM baseline on the following benchmarks:

We report the mean score and standard deviation over 7 runs. Our megakernel produced close score compared to the vLLM counterpart, confirming our kernel is accurate.

We did not need a compiler or a new programming model. Ordinary GEMM and attention kernels already do the hard math; wrapping them in one shared calling convention — the same warp roles, task format, and barrier protocol — is enough to assemble a megakernel by hand, one operation at a time.

Real requests often hit the same experts, so MoE work is sparse and leaves more idle time for the megakernel to fill with other ready work.

Continuous batching and paged attention all work nicely with the megakernel. Decode stays on the GPU as one persistent kernel with a C++ host loop with a separate Python thread controlling the engine.

Which SM runs which tile, and in what order, is the other performance knob beyond kernel tweaks.

The first question is how far this design extends beyond decode. Prefill has a very different shape, and mixed prefill/decode batches would require the scheduler to keep both workloads moving without interrupting latency-sensitive decoding.

We are also building a megakernel for RTX Blackwell (e.g. RTX Pro 6000 and RTX 50-series), with FP8 and FP4 quantization on the roadmap. This is a useful test of how much of the ABI and scheduling design survives a different GPU architecture and lower-precision kernels. We plan to release an RTX megakernel soon.

After that, we want to bring the same approach to datacenter Blackwell and multi-GPU inference. Tensor and expert parallelism introduce cross-device collectives, which add a new synchronization boundary and, potentially, more pipeline bubbles to be recovered by the megakernel.

Learn more about

— Cohere’s first agentic coding model — and explore the code behind megakernels on

We would like to thank Bharat Venkitesh for providing technical support throughout this work. We thank Stephen Jones, Brian Pharris, Vinod Grover, Frederic Bastien, Hua Huang and Disha Mehra from Nvidia for various insightful discussions. We thank Zewen Shen for some helpful discussions on evaluation and numerical accuracy. The design builds on ideas from Hazy Research's

and uses

tile primitives. Thanks also to the authors and maintainers of FlashAttention, PyTorch, Transformers, and vLLM.

Written By

Xiaochun Tong

Intern of Technical Staff, Foundations

Conway Zhu

Member of Technical Staff, Foundations

Donglu Wang

Member of Technical Staff, Foundations

Tags

AI isn’t a shortcut.

It’s how business gets ahead.
