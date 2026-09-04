---
url: https://mistral.ai/news/shieldstral/
title: Introducing Shieldstral.
site: mistral
date: 
scraped_at: 2026-09-04T13:23:14+00:00
---

Solutions

August 4, 2026

By Mistral

5 min read

Thinking

Summary

“Does this content promote violence against a protected group? Is this image safe to show to a minor? Did the assistant refuse the request?”

Every product that ships a model needs to answer questions like these — but the right answer depends on the product, the audience, and the moment. The same content can be fine for a cybersecurity research tool and harmful on a mental-health platform. Most guardrail models bake a fixed taxonomy of harm categories into their weights, so re-targeting them to a new deployment context means retraining. And because safety definitions differ across applications and domains, there is no single "correct" set of categories to model in the first place.

Shieldstral takes a different approach: you write the policy as a plain-language question at inference time, and the model returns a calibrated safety score. No retraining, one interface for text and images, and a verdict from a single token. Please refer to our

here.

As an inaugural member of the

with NVIDIA and other organizations, today we're releasing

as open weights under Apache 2.0, available for download

.

Shieldstral frames content moderation as a

. Each request has three parts:

— the evaluation context, strictness, and (optionally) a definition of what counts as unsafe content.

— a single yes/no question, e.g.

— the content to judge: a prompt, a response, a prompt–response pair, or an image with optional text.

At inference the model reads out only the

and

logits and softmax-normalizes them into a continuous safety score. This one simple formulation does a lot of work: it unifies prompt classification, response moderation, refusal detection, and toxicity detection into a single problem; it lets policies live entirely in the prompt, so one checkpoint adapts to novel policies at deployment time.

— matches or outperforms open guard models up to 7× its size across text safety, refusal detection, policy adaptability, and multimodal benchmarks.

— a single natural-language interface covers text, image, and text+image content across prompts, responses, and prompt–response pairs. Policies are supplied as free-form queries and re-targeted at inference time, without retraining.

— a 3B model that runs on a single 16GB GPU, trained on real and synthetic data with diverse label formats and taxonomies, consolidated into one framework.

— returns a calibrated

/

probability from a single forward pass, so you can threshold or rank by confidence rather than relying on a discrete label.

— Apache 2.0 weights.

We evaluate Shieldstral against open guard models up to 7x its size across four axes. All evaluation samples are held out from training.

Text safety

Refusal detection

Policy adaptability

Multimodal safety

The core idea is that a small model can beat much larger ones if the data is right. Getting the data right meant solving four problems:

Public safety datasets disagree on taxonomies, labels, and annotation conventions — from binary safe/unsafe flags to fine-grained multi-label taxonomies. We convert every dataset into the same instruction–query–document format with a per-dataset processor, and we vary the wording of instructions, queries, and prompt–response delimiters so the model generalizes across phrasing instead of overfitting to one style. We also calibrate strictness per source — strict for adversarial jailbreaks, lenient for response-quality data — so the model learns

decision boundaries. This lets us consolidate sources that would otherwise be incompatible.

If trained on a fixed set of policy labels, a model learns only to classify those predefined policies, rather than reasoning about the precise boundaries of a given policy. This prevents generalization to novel policies. Instead, we construct sets of deliberately similar, easily confused policies and ask an LLM to rewrite safe text into contrastive pairs: each rewrite is engineered to violate one policy but not its sibling. This trains the model to

, a skill that transfers to unseen, user-defined policies at inference time.

Unsafe images can't be synthezised by an LLM the way text can, so visual safety data is scarce. We supplement limited moderation datasets with general-purpose image datasets as high-quality negatives, mutate queries to augment the dataset, and filter every image–query pair through a vision–language reranker to reduce mislabeled data and hallucinations.

We fine-tune with LoRA and merge — via SLERP — a checkpoint calibrated on public data, one that adds fine-grained policy discrimination from generated data, and the base instruct model. The merge recovers common policy calibration and policy adaptability in a single model, and instruction-following from the base model transfers to the moderation task.

. We built Shieldstral end to end on

, our platform for training, aligning, and evaluating custom models. Forge managed the infrastructure, data and model sharding, metrics, and logging on top of state-of-the-art distributed training, so the team could stay focused on the data which is what determines the safety model's quality.

Shieldstral is a step toward moderation that adapts to context instead of forcing every product through one frozen taxonomy. We're continuing to push on multilingual coverage, longer-document robustness, and broader multimodal safety — and we'd love to see what the community builds on top of it.

Shieldstral

Open

A 3B open-weights, policy-adaptive multimodal safety classifier that matches models up to 7x its size on text safety and sets a new state of the art on multimodal moderation.

Text-to-text

Image-to-Text

Read documentation

0%
