---
url: https://huggingface.co/blog/webgpu-kernels
title: https://huggingface.co/blog/webgpu-kernels
site: huggingface
date: 2026-09-01
scraped_at: 2026-09-04T13:20:19+00:00
---

Today, we are releasing the first layer of that effort:

, a minimal library for loading and running optimized WebGPU kernels from the Hugging Face Hub, together with an initial collection of

at

.

The collection covers operations used across a wide variety of machine learning architectures and workloads. More importantly, each kernel is published as a complete, versioned package: its interface, shader templates, correctness cases, benchmark cases, and usage instructions all live together on the Hub.

We are also launching

, an in-browser GPU benchmarking and testing suite that runs and scores the kernels on your hardware. Beyond the results for your own machine, Fleet gives the community a way to contribute performance and correctness evidence from devices we could never cover in a conventional test lab. With your consent, every run adds private evidence that can help us find failures (incorrect results, pathologically slow cases, etc.), improve kernel variants, and make better optimization decisions across real-world hardware.

A model running in the browser eventually becomes a sequence of GPU operations: matrix multiplications, normalizations, convolutions, attention primitives, quantization operations, data-layout transformations, and many more. WebGPU makes these operations available across modern browsers through a portable API, while WGSL provides a common language for the shaders that execute them.

Portability, however, does not automatically mean performance. Two shaders can implement the same operation and produce the same output while behaving completely differently across different accelerators. Workgroup sizes, memory access patterns, vectorization, data types, and fusion strategies can all affect performance. The best choice can also change with the input shape, device, browser, and available WebGPU features.

This is why kernels form a foundational layer of fast browser inference. Higher-level runtimes can only be as efficient as the operations they dispatch. By making those operations individually discoverable, testable, benchmarkable, and versioned, we can improve the foundation independently while keeping a stable contract for the layers above it.

Each kernel in the collection has its own repository and kernel card. The card documents the operation's semantics, inputs, outputs, attributes, supported data types, source files, and a ready-to-run

example.

For example,

implements elementwise addition with multidirectional broadcasting. It is one of the simplest operations in a neural network, used everywhere from residual connections to adding a bias. Its card documents the two inputs, the broadcasted output shape, supported data types, and the variants available for different shapes and devices.

Behind the card, the repository contains the artifacts needed to understand and evaluate the implementation:

This structure turns a shader into a reusable software artifact. The interface is inspectable without reading WGSL, correctness and performance cases travel with the implementation, and published versions can be loaded explicitly rather than depending on an unversioned file URL. Our kernels can also serve as reference implementations for developers building custom WebGPU kernels or integrating these operations into their own runtimes.

Install the package from npm:

Running these kernels requires a browser with

. WebGPU availability depends on the browser, operating system, GPU, and driver. You can check for it in JavaScript with

.

provides the bridge between a kernel repository and your application. Call

with a Hub repository ID and a contract version, then invoke the returned function with typed input data and tensor shapes. Here is a small bias-add example:

The second input is broadcast across the first dimension, producing an output with shape

. The loader derives that output shape and logical data type from the manifest contract and the inputs, then allocates

automatically.

Addition on six floats is deliberately the smallest possible demo. At this size, the GPU round trip costs far more than the math. The point is the call pattern: it stays exactly the same for the heavyweight operations where optimized kernels actually pay off, such as matrix multiplication (

). Only the repository ID and the inputs change.

Even this elementary operation illustrates why kernels need variants. Equal-shape addition can use a direct vectorized path, while broadcasted inputs need different indexing logic. The published Add kernel includes variants for equal shapes, vectorized broadcasting, scalar processing, and general broadcasting. The runtime can select an implementation that fits the current call and device without changing the application-facing API.

The

option selects version 1 of the published

. It is separate from an ONNX opset, an operator's

, or a model revision. Keeping those concepts separate lets applications depend on a stable JavaScript-facing contract while kernel implementations evolve behind it.

So, how much of a difference do optimized kernels actually make? We put our collection head-to-head with ORT WebGPU on an Apple M4 GPU, using ONNX Runtime Web

. We started with 1,756 test cases across all 207 operations and kept the 809 cases where both sides produced matching outputs and reliable timings.

Across those comparisons, our kernels were

and

, with 629 wins, 176 losses, and 4 ties. Here is a closer look at four familiar operations:

Some individual wins were much bigger. A particularly difficult bilinear Einsum case (

with size 4096) ran in 0.136 ms with our kernel versus 1,396 ms with ORT WebGPU: more than

. A row-wise CumSum over

was

, at 0.016 ms versus 4.784 ms. These are unusual cases rather than the speedups you should expect everywhere, but they show how much a specialized kernel can help when a general implementation hits a slow path.

We timed the work done on the GPU itself, leaving out setup such as loading kernels, creating sessions, uploading inputs, compiling shaders, and reading outputs back. Very short workloads are naturally harder to measure, and small cases can benefit from the GPU cache, so these numbers are best read as a useful comparison rather than a promise for every application.

They are also results for individual operations, not complete models. Exact performance will change across GPUs and browsers, which is why Fleet is so important for building a broader picture.

We are also working with the ONNX Runtime team to upstream these improvements so they can benefit the broader ONNX Runtime Web ecosystem.

WebGPU performance varies across GPUs, browsers, and drivers, so results from one machine only tell part of the story.

lets anyone run correctness and performance checks in the browser and see how the kernels behave on their hardware.

With consent, each run privately contributes evidence that helps us spot device-specific failures, compare variants, and improve selection rules. The goal is simple: use broad, real-world coverage to make the kernels faster and more reliable for everyone.

The initial 207 kernels are a starting point, not the end state. Publishing kernels independently on the Hub gives us a common place to inspect contracts, compare implementations, reproduce correctness checks, and improve performance without embedding every shader directly into every runtime.

The collection is also part of the Hub's broader kernel ecosystem: on the

, the WebGPU kernels sit alongside kernels for CUDA, ROCm, Metal, and other platforms, and can be filtered, sorted, and explored like any other artifact on the Hub.

The pieces reinforce one another:

This is the low-level foundation for the next steps in our browser inference stack. We are excited to connect these kernels to higher-level model tooling, continue expanding operation coverage, and make fast local inference easier to use across the WebAI ecosystem.

Explore the

, try

, and

to contribute evidence from your device and help us make the kernels better for everyone.

More Articles from our Blog

1

The Fleet part may matter as much as the kernels. The 809 comparable cases on an M4 are useful, but browser, driver and device variance is where WebGPU tends to get painful. Will Fleet eventually expose per-device distributions, or is the plan to use the runs only for aggregate selection rules?

or

to comment
