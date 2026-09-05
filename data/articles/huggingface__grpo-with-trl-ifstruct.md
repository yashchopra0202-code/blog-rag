---
url: https://huggingface.co/blog/grpo-with-trl-ifstruct
title: Fine-tuning a 350M Model for Better Structured Outputs in 100 GRPO Steps
site: huggingface
date: 2026-08-05
scraped_at: 2026-09-05T05:08:05+00:00
---

Structured output is one of the most common real-world tasks for LLMs, yet most benchmarks fold it into broader reasoning or extraction scores rather than measuring it on its own. Whether a model reliably returns valid, parseable output in the requested format and shape — schema compliance — is often what decides whether it can be wired into a downstream system at all.

This guide has two halves that run in different places:

We will need

for the Python tooling and

for serving. Following the

, install

with Homebrew and verify that

is available:

Before we begin, let's evaluate LFM2.5-350M on the

and see whether we can

is a benchmark for testing the validity of LLM outputs and schema adherence. The benchmark is open-source in

, with the public benchmark dataset available on Hugging Face at

For the eval comparison, we serve the model locally on the MacBook with

. We will use the

GGUF (

).

Then we start the base-model server with the following command:

Once the server is running, we can run the full benchmark with 2000 samples:

The

. Our local llama.cpp/BF16 setup measures 22.6%, close to the 21.1% reported in the IFStruct blog. We use this local result as the baseline for the same serving stack comparison.

The full, runnable pipeline lives in the

. We will cover only the relevant pieces in this section.

We use

, which pairs each prompt with a target JSON Schema and an expected field count. We use about 500 samples for training.

Because the Nemotron data distribution differs from the IFStruct evaluation, we augment the prompts to close two gaps between them:

We load

and attach a LoRA adapter. Because LFM2.5 uses a hybrid attention/convolution architecture, we target the LFM-specific module names:

This trains ~6M parameters, about 1.66% of the model.

Then we define three reward functions, each on a

scale, which score every completion on whether the extracted

is correct:

We combine the three as a weighted sum with

We train for 100 steps with 8 generations per prompt group, sized for a free-tier 16 GB GPU:

As you can see in the notebook, over the run, all three reward components climb, the KL from the reference model lifts off zero after warmup, and the truncated-completion fraction stays near zero.

Finally, we merge the LoRA adapter back into the base weights and save it as a single self-contained checkpoint, ready to convert to GGUF for serving:

After GRPO fine-tuning, we rerun the IFStruct evaluation. For this, we need to convert the merged model checkpoint into a BF16 GGUF. The converter script ships with the llama.cpp source, so we clone the repo once and install the converter's

package.

Then we serve the merged model with the following command:

Then, we will run the full IFStruct evaluation again with the fine-tuned model:

Comparing the two runs on the identical serving stack:

The gains land exactly where the training aimed: the JSON pass rate rises by nearly 14 points (18.0% → 31.9%), while YAML stays mostly the same. While this is still below the

, it shows that even light task-specific fine-tuning can bring a small model close to a larger one.

A short GRPO run with about 500 samples and 100 steps can lift a small 350M parameter model from 22.6% to 29.7% on IFStruct. The takeaway is that a cheap, task-specific reward signal can make a small model substantially more reliable about

, closing much of the gap to models several times its size.

To reproduce or extend this work, see the original

, the

benchmark repo, and the

dataset.

More Articles from our Blog

or

to comment
