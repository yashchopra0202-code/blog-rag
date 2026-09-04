---
url: https://www.together.ai/blog/autoscaling-endpoints-for-llm-inference
title: Autoscaling endpoints for LLM inference
site: together
date: 
scraped_at: 2026-09-04T21:14:07+00:00
---

Summary

With Dedicated Model Inference on the Together AI platform

ou can get your deployments to autoscale on metrics the inference engine actually understands, such as in-flight requests, TTFT, GPU utilization, token throughput. You can set replica bounds, pick a metric and target, and then tune two windows that control how eagerly it scales up and how patiently it scales down. Understanding and choosing the right metric is important because it determines how your deployment will behave under peaky traffic and impacts the latency your users will see. Below we'll cover how to choose the right metric to autoscale on and show an experiment where the same load was replayed under three different autoscale policies.

With dedicated inference you pay per replica-minute, which makes capacity planning a balance between two failure modes:

"Just autoscale it" is the obvious answer, and for stateless web services it mostly works. But LLM serving is a different beast and it breaks the two assumptions that classic autoscaling leans on:

Due to these nuances and the varying requirements of each customer our platform gives you a catalog of inference-native metrics and allows you to choose how your deployment scales. This post helps you choose well!

Each deployment carries an autoscaling policy: replica bounds, one or more scaling metrics with targets, and timing windows.

The control loop goes as follows: observed metric → desired replicas (

) → timing windows dampen → clamp to bounds → GPU placement. Observed load feeds back and the loop evaluates continuously with the traffic split following capacity automatically.

The core loop is proportional, meaning that if you target 8 in-flight requests per replica and you're observing 16, the system will want twice the replicas(assuming the 2x replicas are within the min, max bounds). The timing windows can be used to add a de-bouncing effect so that the replica count doesn't oscillate:

This asymmetric tradeoff of an eager up and patient down autoscale window is very important to tune and requires an intuitive understanding of your particular traffic distribution. Up-window mistakes cost dollars while down-window mistakes cost latency

dollars (because you'll just want to scale right back up, paying the cold start on the way back up).

Setting it is one PATCH:

A few settings to keep in mind:

Eight metrics that you can autoscale on. Picking the right one depends on what you're trying to protect your deployment against.

Autoscaling metrics include concurrency-driven (leading; the safe default), SLO-driven (trailing; scale on the promise), efficiency-driven (cost-first). If you attach multiple metrics the first one in the list is used.

Three ways to think about picking the right metric:

This is a good table to keep in the back of your mind when selecting the metric to scale on:

is legal only together with

which is a way to explicitly

the deployment. Waking requires an explicit action and requests to a stopped deployment return an error rather than triggering a start. This means that you should plan dev and staging endpoints around auto-stop plus explicit restart windows.

The

is important to understand when using this auto-stop functionality. You can think of a cold start as consisting of the following phases: GPU placement → weight download → engine load → warmup and the deployment's event feed timestamps each of these phases (pod.startup_phase_changed):

Larger models might have proportionally longer weight downloads, engine loads and warmup periods. To get a better feel for these numbers we present what we got across runs on 1×H100 replicas on warm clusters below:

Notice that these windows are measured in minutes which means that auto-stop only pays off when the gaps between uses are long relative to the restart and when the first user after an idle period is willing to tolerate an explicit start (or an error-then-retry flow). This tradeoff is okay for Dev and staging endpoints but for anything with a p95 SLO or unattended callers you should typically keep min_replicas: 1.

‍

Requests queue on existing replicas (the

and engine queue depth will increase) and latency will degrade with TTFT increasing first followed by error/timeout risk while new replicas come up. This means that if your traffic can spike 10× in 90 seconds and your cold start is 4 minutes, the

defenses are

headroom or a higher-target policy that keeps slack capacity up. This is more of a capacity-shape question than a tuning question, and it's better answered before launch day.

No. While a

is in flight, the platform pins autoscaling bounds on both deployments; the rollout's replica counts would otherwise be undone by a scale-down decision mid-step. Your configured bounds are restored automatically when the rollout completes or aborts.

This is handled smoothly because traffic-split weights are

(capacity = weight × ready replicas), a deployment that scales up automatically absorbs proportionally more traffic with

. Autoscaling and routing work off the same capacity picture.

This is the classic symptom of a scale-down window shorter than your traffic's natural rhythm. Bursty traffic + 1-minute down-window = scale down in every trough, cold start in every crest. To resolve this you should widen

until the sawtooth flattens. This allows you to trade a few replica-minutes to eliminate repeated cold starts.

We ran this experiment on a Qwen3.5-9B deployment (1×H100 per replica, bounds 1–3), reset to exactly 1 replica before each round, then the same scripted load replayed three times: a sine wave between ~12 and ~48 RPS with two 80 rps spikes. This was repeated under three different autoscaling policies:

Three lessons from the above runs:

Start with the defaults, then tune from evidence:

📚

→
