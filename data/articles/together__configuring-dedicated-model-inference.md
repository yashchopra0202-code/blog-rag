---
url: https://www.together.ai/blog/configuring-dedicated-model-inference
title: Configuring Dedicated Model Inference
site: together
date: 
scraped_at: 2026-09-04T21:14:12+00:00
---

Summary

Dedicated Model Inference on the Together AI platform consists of three parts: the

(a stable name you or your clients call),

(specific model + hardware combinations running replicas behind it), and

(recipes for how a model runs). A capacity-aware traffic split ties these three entities together. This architecture enables various other features such as rollouts, A/B tests, shadow experiments, zero-downtime changes possible. Below we'll show how capacity-aware routing works against a live endpoint with measured traffic.

One easy way to understand this is by referring to the ID, every ID in the system tells you what it is by prefix, which makes logs and scripts self-documenting:

(project),

(model),

(config revision),

,

(deployment),

(rollout).

An

is deployments with cohort assignments. A

is a deployment at weight zero receiving mirrored traffic. Stopping a deployment is bounding min and max replicas to 0/0.

The traffic split is a list of

entries where a weight is per

**.** The router computes each deployment's effective capacity as

and routes proportionally to this capacity.

Walk through the diagram above: both deployments have weight 1 but deployment A has 1 ready replica (capacity 1), deployment B has 3 (capacity 3), so traffic follows a

. Equal weights mean

, not equal traffic share.

We designed it this way because it makes routing and scaling the same conversation:

Weights are positive numbers with no sum constraint so

and

describe identical routing. If you

fixed traffic shares regardless of replica count you can setup A/B experiment cohorts which allow for integer percents that sum to 100%.

Setting a split is one PATCH with a field mask:

You don't need to write configs from scratch. Every model in the supported-models catalog ships with

which are certified model + config pairs we benchmark and continuously improve:

From there you can copy the model and config resource names into a deployment create:

When you're choosing

configs, the selectors tell you what each recipe optimizes:

The optimization axis is the one you'll spend the most time choosing between.

Configs are immutable because cr_ revisions never change, i.e. a deployment's behavior can't drift because someone "just tweaked a flag" on a shared config. A change is a new revision; the old one remains a valid, tested rollback target. Speculative decoding can be triggered from here too because a draft model is a property of the

Because capacity = weight × 0 = 0 it receives no traffic; other deployments will absorb its share. When replicas recover, traffic flows back automatically and proportionally.

You should remove it from the split first, then delete. The teardown sequence consists of drain traffic → stop → delete, and the API will push you towards that order.

(capacity-relative, steady-state routing),

(integer cohort shares, sum to 100 and are fixed regardless of replica counts), and

(a rollout's transition schedule). These are three different tools for three different jobs and they compose in a fixed order: routing first resolves the

(a candidate deployment sampled by capacity), then an

re-samples if the candidate is its control (subdividing the control's share among the arms), then an

re-samples if the candidate is its source (splitting between source and target by the current step percentage) and finally a cluster is chosen inside the winning deployment. A rollout manipulates its stage on your behalf.

The endpoint which looks something like:

can be passed as a

string in the standard inference API. This will stay the same even if you choose to perform a rollout, swap hardware, run A/B tests.

We ran this against a live endpoint with two single-H100 deployments to show the weight model traffic split in action. Two deployments each with weight 1 and each starting with 1 ready replica. We sent 599 tagged requests and attributed each to its serving deployment, then scaled A from 1 → 2 replicas and sent 599 more requests and the following routing was captured as seen by the deployments:

Because routing follows capacity which in turn followed the replicas. Within deployment A, its two pods each carried ~30–40% of total traffic (39.6% and 29.9%), the router balances across pods, too.

To make the profile tradeoff concrete, we swept the two certified profiles from our demo endpoint with one replica each, 60-second closed-loop levels at concurrency 4 / 8 / 16, 200-token generations, token counts taken from the API's own

field:

This table is the whole argument for measuring:

A batches well with 4× the throughput from c4 to c16 with TTFT p95 rising only ~17%. B is

than A at concurrency 4, then saturates: past c≈4 its effective request rate stops growing, aggregate throughput halves, and a few requests per minute begin to stall outright. If you'd only load-tested at concurrency 4, you'd have picked B for a high-concurrency workload and only found out about this behavior in production.

Neither profile is "wrong" they're just different points on the serving frontier, and profiles for

model will have their own curves. The starting configs give you a way to test starting points; a one-hour sweep like this one tells you which one fits your traffic.

The whole model, in five commands:

From here, everything else in this series is one more deployment away.

📚

Dedicated Model Inference →

·

·
