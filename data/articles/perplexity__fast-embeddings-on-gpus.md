---
url: https://www.perplexity.ai/hub/blog/fast-embeddings-on-gpus
title: Fast Embeddings on GPUs
site: perplexity
date: 2026-09-04
scraped_at: 2026-09-04T21:16:07+00:00
---

This article presents an under-the-hood view of Perplexity's serving infrastructure for this special class of models.

Contents

Fast and accurate search is vital to all of Perplexity, from Search and Computer to our API Platform. Behind the scenes, the heavy lifting is done by embedding and ranking models, which help our systems identify the most relevant results for a given query. We achieve state-of-the-art quality and latency by training and serving our own models, such as

.

This article presents an under-the-hood view of Perplexity's serving infrastructure for this special class of models. We discuss our techniques to efficiently address the inference needs of AI-native search, enabling quick prototyping and evaluation of models while powering our

. These techniques collectively expand the Pareto frontier of search quality and efficiency, enabling us to serve agents and users with the best possible results at the lowest cost and latency.

In a typical search setup, indexed documents are mapped to a high-dimensional vector space using an embedding model and stored in a vector database. By embedding a query using the same model, similar documents can be located by finding the vectors closest to that of the query. This gives rise to two different traffic patterns for an inference engine to serve:

Following vector search, large batches of documents must be scored, striking a balance between throughput and latency.

We built out our inference infrastructure to leverage as many common components as possible across use cases. Since we typically use small Transformer models to produce embeddings, we share the bulk of the implementation with our LLM inference code: batch embeddings are similar to compute-bound prefill, whereas online embeddings, which often run on a few tokens, are computationally similar to memory-bound decode. We thus reuse our

to serve embedding models. As a result, we can achieve massive batch inference throughput with minimal additional engineering work, while preserving low latency for online embeddings workloads.

We expose inference through standardized APIs, both internally and externally through our API Platform. Under the hood, multiple services are involved in the processing of an embedding request:

It handles the CPU-side work for requests such as JSON parsing,

, input templating and batch splitting, translating requests to a custom gRPC protocol for downstream servers. This separation allows us to configure certain parameters around tokenization and input formatting without having to touch the heavier inference instances.

It is a gRPC server implemented with Rust,

, and

. Tulip receives gRPC inference requests, handling scheduling and batching. It then sends the batches to the ROSE engine, returning completed responses to clients.

It is primarily defined in Python, providing

, layers and definitions for a wide variety of models. ROSE implements the forward passes through models, also providing CUDA graph management specialized for embeddings. It is bridged to Tulip via a

function, which takes a batch and returns a reference to the computation it performs on the accelerator.

Both Transformer-based models and the underlying Hopper/Blackwell architectures are mature technologies, so embedding inference on the GPU side has converged to a largely optimal implementation across various inference engines. Even so, we discovered additional opportunities for improvement in runtimes and harnesses that expose the models end-to-end to a client. In particular, we found that we can improve latencies by carefully managing CUDA graphs and by building a

abstraction to asynchronously track a GPU-side result in the native Rust engine. We implemented these features in Tulip, so it could effectively interface with the model implementations of ROSE.

We designed Tulip to be as lightweight of an interface over our model serving as possible. It handles incoming requests in Tokio async tasks, maintaining a pool of requests it tracks and schedules batches from to dispatch to the accelerator. The scheduling mechanism in Tulip is very simple: requests accumulate while Tulip is dispatching work or waiting for results. From the accumulated requests, sequences are picked on a first-come, first-served basis to be run through the model.

The simple scheduling mechanism is motivated by an observation on model performance. For small embedding models, at the sequence lengths we serve for, we noticed that the linear cost of dense layers is dominant over the quadratic cost of attention. Thus, latency is mostly proportional to the number of tokens, not the number of sequences. Consequently, once a batch is large enough to saturate the GPU, which is around 512 tokens on a model under one billion parameters, packing more sequences into it does not improve efficiency.

To effectively interface with the model, Tulip relies on CUDA graphs and lazy result tracking to overlap GPU and CPU work and fully utilize the available resources.

Running the forward pass of a model involves both CPU-side and GPU-side work. The CPU is responsible for scheduling batches and launching kernels with the appropriate parameters, while the GPU executes the relevant matrix multiplication, attention, norm or activation kernels. For high-throughput workloads such as training and reindexing, CPU-side overheads are negligible because batch sizes and GPU-side latency are both large. However, on smaller batch sizes, CPU-side work can outweigh GPU-side work.

To mitigate overheads, instead of launching independent kernels, a CUDA graph can be built to capture the metadata required to launch all the kernels of a forward pass with a single call to the CUDA driver. This eliminates the need to re-run expensive Python and PyTorch code for the configurations CUDA graphs can be captured for.

Across each model, we track an inflection point, determining the minimum number of tokens at which GPU execution is more expensive than CPU-side kernel launch. Because embedding models are small, we observe that this inflection point comes at batches of thousands of tokens and tens of sequences. Some attention implementations rely on dynamic host-side inputs to configure kernel launches, preventing full-model prefill/dense CUDA graphs. We

changes to relevant kernels to enable them in our inference engine.

To address overheads, we build whole-model CUDA graphs for all embedding models and overlap CPU work with GPU work. Since CUDA graphs minimize the CPU-side overheads, once a graph is launched, we have free time to kick off and enqueue the execution of the next batch whenever it is available. The results of the pending batch are tracked with a

, which allows an async task in Rust to block until the previous batch finishes execution. CUDA graphs help low-latency serving by ensuring we are not held back by the cost of kernel launches and facilitate improved scheduling in the high-throughput case as they free up the CPU to do work on the next batch sooner.

CUDA graphs must be captured for each distinct configuration, which for embeddings means a graph per sequence count and token count combination. Since this grid is expansive, we pad token counts to buckets that are multiples of 64 or 256. This still results in thousands of graphs that might take multiple minutes to capture for a typical model. The cost of capture comes from two sources: an eager forward pass that must be executed to compile kernels and set up buffers for various kernels that need them, followed by the capture run which re-executes Python code.

We mitigate startup costs by capturing CUDA graphs lazily as the engine serves. We keep track of each configuration and ensure that it goes through an eager warmup run before triggering graph capture and replay on the second hit. All subsequent executions of the same graph configuration then go through CUDA graph replay. Lazy graph capture has an impact on p99 latencies during startup; however, it is valuable in spreading multiple minutes of eager work across multiple hours. Quicker startup times allow us to better scale and manage embedding deployments.

Through CUDA, GPU work is asynchronous. Since launching a kernel asynchronously enqueues it on a stream, host code must explicitly synchronize to read out the resulting vectors. To facilitate a higher degree of parallelism and to be able to kick off future batches while waiting for the previous one to complete on the device, we rely on a

abstraction to track values.

The

tracks a host buffer in page-locked memory and a

operation via an event copying data from the device. It is kicked off after the launch of the forward pass on the same stream. Since the copy operation must wait for all prior kernels on the stream to execute, the associated event tracks both the completion of the forward pass and the availability of the result on the CPU.

We leverage

s in our ROSE encoder engine to overlap GPU and CPU work. Instead of each

call running the CUDA graph and waiting for it to finish,

returns a

to asynchronously track its result. Coupled with CUDA graphs, this helps us achieve low latencies and better throughput.

We adapted our ROSE engine, which we originally built for LLM serving, to also handle the execution of embedding models. To minimize the effort needed to support embedding models, ROSE aggressively reuses code between LLMs and embeddings. For instance, pplx-embed serving and

LLM decoding all go through the same kernels. This sharing allows us to easily serve an embedding model that was originally fine-tuned from an LLM for prototyping, evaluation, and production inference.

For dense layers, embedding and LLM inference are identical since token vectors are processed independently. In attention layers, differences are handled by adding support for ragged inputs, alongside the paged prefill and decode setups required by LLMs. When serving an embedding model, we do not instantiate a KV cache and dispatch to variations of attention kernels which support the ragged format to avoid padding. The supporting conversion and calibration routines are also shared with the LLMs.

Ivy, our inference HTTP proxy layer, also plays an important role in performance. Because request payloads vary in production, routing individual requests to individual replicas can cause load imbalance. Ivy splits large-batch requests into chunks and load-balances them between replicas, improving utilization and smoothing latency. Our recent work on

, fully rolled out in Ivy, drastically improves latencies over off-the-shelf tokenizers.

ROSE supports a variety of attention backends. Different kernels may be suited to specific problem sizes. Over time, we integrated FlashInfer 2, FlashInfer 3 and FlashAttention 4 kernels to implement ragged attention.

In general, we observe that FlashAttention 4 is faster. However, FlashInfer 3 outperforms it on

models at very long sequence lengths. Since performance and tuning can vary with the number and dimension of attention heads, we maintain support for multiple configurations and make a case-by-case decision when serving.

We benchmark against vLLM v0.22.0, running inference on BF16 precision on actual model weights and inputs derived from evaluation datasets. All timing runs were preceded by warmup runs which verified that the divergence in cosine similarity is within 0.1%.

We report runtimes for pre-tokenized request batch size 1, fully sequential requests, sequence lengths of 128, 512, and 4096 tokens.

Pre-tokenized request batch sizes 5, 25, and 50, sequence length of 512 tokens.

Request batch size 100, four concurrent processes submitting requests, sequence lengths of 512, 1024, and 4096 tokens.

Sequence length 512, batch size 1, but we send 1, 2, 4, 8, and 16 concurrent requests. This benchmark also includes tokenization costs through Ivy, alongside the networking overhead between Ivy and Tulip.

The serving infrastructure composed of Ivy, Tulip and ROSE allows us to serve embeddings for Perplexity with lower latency and better throughput, resulting in more accurate search at a reduced cost compared to off-the-shelf solutions.

By focusing on specific models and taking ownership of the entire stack, we obtain the freedom necessary to strike an effective balance between performance and flexibility, mixing highly re-usable and performant Rust primitives alongside more generic Python modeling code. Many open-source inference engines, such as

,

, and

, are integrating languages like Rust and C++ into their stack. We've invested in Rust over the past two years and have reaped great rewards in both performance and maintainability. By sharing most of the embedding implementation with our LLM serving stack, we derive gains in throughput as well, without requiring significant engineering effort to be spent on the maintenance of embedding models.

As models evolve, we will continue to improve each layer of our stack to reduce both CPU-bound and GPU-bound latencies. Our custom gRPC-based protocols within Ivy and Tulip allow us to tweak communication to reduce network latencies, while ROSE provides a foundation to improve computational throughput. Additionally, as support for free-threaded Python grows throughout the ecosystem, we will be able to further improve Python-Rust interoperability to reduce overheads.
