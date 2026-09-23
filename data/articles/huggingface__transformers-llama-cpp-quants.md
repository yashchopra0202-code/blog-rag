---
url: https://huggingface.co/blog/transformers-llama-cpp-quants
title: https://huggingface.co/blog/transformers-llama-cpp-quants
site: huggingface
date: 2026-03-02
scraped_at: 2026-09-23T08:58:04+00:00
---

Running AI models on your laptop has become much easier, and

has been a big part of that. Its inference engine powers local AI tools such as Ollama, LM Studio, and Jan. Alongside projects like

, it has helped make local inference a practical option for everyday use.

This is where we are right now. And i’m not gonna lie it feels pretty magical 🧙‍♀️

Qwen3.6 27B running inside of Pi coding agent via Llama.cpp on the MacBook Pro

For non-trivial tasks on the

codebases, this feels very, very close to hitting the latest Opus in Claude…

, developed by the llama.cpp team, is a widely used format for local inference. The team also shares quantized checkpoints under

. Publishers such as

, and

also provide ready-to-use GGUF checkpoints in a range of quantizations, so users can pick the version that fits their machine. GGUF models have been downloaded millions of times.

We want to make it easier to run these models locally with transformers, too. Compatibility is only useful if the model is pleasant to run. To bring performance close to llama.cpp, we're reusing its underlying ggml kernels through the

library, and reducing overhead in

. Our initial focus is local inference on Apple Silicon, starting with the Qwen3.5 architecture.

packages model weights and metadata, including tokenizer information and an optional chat template, in one file. It supports different quantization levels, letting you trade some precision for a smaller memory footprint. Variants such as

mix tensor precisions, using mostly 4-bit weights while keeping sensitive tensors at higher precision.

Here's how quantization changes the file size of

We suggest starting with

, then trying

or

if you have more memory available. More aggressive quantization can help larger models fit, but the quality tradeoff depends on the model and the task. Evaluate it on the work you actually want the model to do. The

describes the available quantization types.

To get started, you need:

To load a GGUF model, pass its Hub

and filename as

to

No extra configuration is needed: when the weights stay packed on Metal, transformers automatically loads the compatible ggml/Metal layer kernels and uses

as the attention implementation. If that kernel cannot be fetched, the model falls back to

with a warning, and you can always force

by passing

explicitly. See the

for more loading options.

That is the only GGUF-specific step. Everything after it is the standard transformers API:

Without a compatible quantization kernel, the loader falls back to dequantizing the model and uses more memory.

You can also use the same checkpoint with

, which exposes an OpenAI-compatible API:

The model argument uses

: before the colon is the Hub repository (

), and after it is the file to load (

). This selects a specific quantization from a repository that may contain several.

For models whose chat template supports thinking, add

to skip it or

to enable it. The default,

, follows the chat template’s default. See the

for details.

You can connect a client such as

or

by adding a custom OpenAI-compatible provider with these settings:

transformers runs the model on your Mac, while the client provides the conversation interface. The same endpoint can be used by other clients that support this API.

Our reference for local inference performance is llama.cpp. The comparison below focuses on three GGUF checkpoints: a small dense model, a larger dense model, and a mixture-of-experts model.

The llama.cpp column comes from the

tool (build

, release b10200, Metal backend from ggml 0.18.0), run as

, which reports

: the token-generation rate over 128 decoded tokens, averaged across three repetitions, with prompt processing excluded. The transformers column is

producing the same 128 tokens from a 12-token prompt, best of three warmed runs, and it includes prefill.

Measured on a MacBook Pro M2 Max, 32 GB unified memory, macOS 26.6, PyTorch 2.12.1, kernels 0.17.0,
plugged in.

For the other column:

Transformers is close to llama.cpp across all three checkpoints. The chart uses the same measurements described above; it does not imply identical benchmark conditions, since the Transformers measurement includes prefill while

reports decode-only throughput.

When

, we described their complementary roles: llama.cpp provides a foundation for local inference, while transformers provides a foundation for model definition. GGUF support brings those two closer together.

Its dedicated runtime, memory management, and broad hardware support are built around that goal. This integration gives developers a convenient way to work with the same GGUF checkpoints inside transformers:

For that last case, use

transformers already provides the PyTorch implementations of these architectures. With ggml kernels and quantization schemes available in PyTorch, we can work toward accelerating their supported operations without first implementing the entire model in llama.cpp. This is especially useful for new architectures, research models, and custom variants that may never receive a dedicated llama.cpp implementation.

That opportunity extends beyond the GGUF format itself. A kernel operates on tensors; it does not require the whole model to come from a GGUF file. The same building blocks can be integrated into other transformers models and loading workflows. This also opens a path to other modalities: computer vision models, audio models, and multimodal models could reuse compatible attention, normalization, and matrix multiplication kernels without first having a full implementation in llama.cpp. Each architecture still needs integration and validation; the initial GGUF examples here cover text generation.

We also wanted to show how far we can get while keeping the model and generation loop in Python.

The kernels handle the heavy computation, while the generation loop keeps the GPU busy by avoiding unnecessary synchronization.

Our focus was to make eager execution fast without requiring

. For interactive use, we wanted a quick start and a steady stream of tokens, without compilation pauses or recompilation when input shapes change. The two main pieces of that work are the kernels and

itself.

A kernel is a small program that performs an operation on the GPU. PyTorch supplies general-purpose implementations; a specialized kernel can do less work, combine several operations, or read quantized weights directly in their stored format.

The

library lets us distribute compatible builds of ggml's Metal kernels on the Hub and call them from transformers. That brings ggml's work into the PyTorch model without replacing the model with a separate inference runtime.

The first four packages build on ggml's kernels; the top-k kernel addresses a separate bottleneck in MoE routing. Together they reduce the GPU work needed for each generated token.

To show the contribution of the layer kernels, we compare the same packed GGUF checkpoints with and without them. The quantization kernel stays enabled in both configurations: disabling it would also change how weights are represented and would measure a different tradeoff.

Faster kernels only help if the GPU has work to do. During generation, the CPU schedules GPU operations and controls the loop that produces the next token. Reading a result back from the GPU can force the CPU to wait until queued operations finish. Repeating even a small wait for every token can noticeably reduce throughput.

Two changes address this in

, which results in improvements for all transformers models (not just when running GGUF files):

These changes improve the generation loop around the model, so their usefulness extends beyond GGUF. They complement the kernel work: kernels reduce the cost of an operation, while fewer synchronization points let CPU scheduling and GPU execution overlap.

These measurements keep all layer kernels enabled; the bars isolate the changes to the generation loop.

The initial target is a single interactive conversation on Apple Silicon. There are a few boundaries to keep in mind:

If you have a GGUF model you would like to use in transformers,

with the checkpoint and your use case. That will help us prioritize support for the models people are running locally.

We would like to thank

for initiating this work and reviewing all of my PRs, and

for the

PRs. We are grateful to

, the

, and Bertrand Chevalier for their help integrating the kernels. We also thank

and

for reviewing this blog post, and

for overseeing the project.

More Articles from our Blog

or

to comment
