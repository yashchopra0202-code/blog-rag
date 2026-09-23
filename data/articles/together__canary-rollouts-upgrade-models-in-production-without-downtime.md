---
url: https://www.together.ai/blog/canary-rollouts-upgrade-models-in-production-without-downtime
title: Canary rollouts: upgrade models in production without downtime
site: together
date: 
scraped_at: 2026-09-23T08:58:44+00:00
---

Summary

Rollouts move live traffic from your current model to a new checkpoint in gated steps. Health checks always run before traffic moves; on a canary you can also add metric gates (say p95 latency or error rate) that run after each step. If a gate trips, the rollout pauses at the canary share and you cancel it and run it in reverse. Below we run one for real: a Qwen2.5-7B → Qwen3.5-9B canary whose gate caught a 137% p95 regression at 10% of traffic; we canceled and reversed it with live requests served and none failed.

If you run a model in production, you already know the need to swap in a new checkpoint or a new model family: the open model ecosystem moves fast, and the candidate usually looks great in evals or promises better throughput. You want it in front of every user without hiccups, and a way to rollback if it disappoints. The usual options force a tradeoff:

Both of these options put a human in the loop as the safety mechanism. Rollouts move that mechanism into the platform: you describe the source, the target, the steps, and what "healthy" means, and the platform works against this plan at every stage.

A rollout migrates traffic between two deployments on the same endpoint: a

(what's serving today) and a

(what you want to serve tomorrow). You pick one of three strategies:

Here's what happens inside every canary step:

We chose this ordering deliberately; each item prevents a class of incidents:

Through the API or the console, a rollout is created in a

state and does nothing until you explicitly start it (the CLI's

command creates and starts in one step). This two-step create/start is intentional because you can create the rollout, review it (or have a teammate review it), and start it when you're actually watching.

Two states in the diagram above deserve a note:

There is no

end state that leaves traffic in limbo: a rollout ends

(the target serves) or

(the split is frozen where it was, and you run the rollout in reverse to go back).

The following is a breakdown of what happens in a single canary step, measured on the run at the end of this post (Qwen2.5-7B → Qwen3.5-9B on one H100 each).

The propagation wait is what keeps stale global routing caches from sending requests to a shrinking source. The wait period is grown to the metric window plus ingestion lag. The cold start dominates the first step; later steps add replicas to a target that is already serving and warm.

All three strategies run through the same engine and the same health gates; they differ in how traffic moves, how much extra capacity the overlap costs, and whether there is a wait window for a metric gate.

Here's a three-step canary from a deployment serving your current model to one serving the candidate, with a latency regression gate. The CLI ships as

in the

Python package (2.34.0 or newer). You pass the

deployment; the source is inferred when exactly one deployment is receiving traffic, otherwise pass

The source drains to zero replicas and stops when the rollout completes (

defaults to 0), and the target lands with the source's replica count as its floor (

). The CLI attaches one metric gate per rollout; for several rules use the console or the API.

The same via the REST API, where create and start are separate calls and a rollout can carry several metric rules:

A few things the API is strict about:

is an integer (95, not "p95"), enum values carry their full prefix (

), durations are protobuf strings like

, and a metric name outside the catalog is rejected with a 400 that lists the supported names. Draining the source is the default, so there is nothing to pass for it.

The regression check can be understood as:

The same rollout from Python, with the

package (2.34.0 or newer). Field names are snake_case here and camelCase on the wire; the SDK translates.

Every rollout accepts the same four controls. An endpoint has at most one active rollout, so the CLI takes the endpoint ID and you rarely need the rollout ID. Each control returns as soon as it is accepted; poll

(or the GET endpoint) until the rollout reaches the state you expect. While a rollout is active, including while paused, the endpoint's traffic split is locked and its source and target cannot be stopped or deleted.

The rollout goes

, lets any step activity in flight finish, then holds at the current traffic split and replica counts as

. Both deployments keep serving. A pause can last for days; the platform never auto-resumes an operator pause.

Continues from the same step, for both

and

. If a gate tripped, it re-evaluates against fresh data; the step is not skipped.

Skips the remaining canary steps and runs the final 100% step in full: the target scales to its landing size, traffic shifts, the propagation wait and soak run, then the source drains. Skipped steps are recorded as

. Not instantaneous: in a test run with a 10-minute step interval, a promote at step 0 still sat through the final step's full soak.

Freezes the current traffic split into the endpoint's standing weights and ends the rollout as

. Nothing scales down; both deployments keep serving their frozen shares until you edit the split or run a reverse rollout. A target canceled at 0% is left running with no traffic; scale it to zero or delete it if you no longer need it.

There is no rollback verb. To move traffic back, after a cancel or after a completion, create a new rollout with source and target swapped, then start it. Any strategy works and the same gates apply. After a cancel the default canary ladder skips the steps the new target has already passed, and the default final replica count is the pair's combined count.

Controls on a finished rollout (

or

) are refused. Delete a finished or never-started rollout from the history with

; deleting the record does not change the traffic split it left behind.

Metric gates are a canary feature: blue-green and rolling still run health gates, but the staged metric comparison needs canary's step structure to be meaningful. Gates evaluate over a

of three router-side metrics, measured identically for source and target (any other metric name is rejected at create time):

Each rule uses one of two checks:

Two recipes cover most services:

Three durations interact, so keep all of them in mind:

You must wait for a period of at least

, so that the gate's entire lookback period lands inside the current step's steady state. If you wait for a shorter period than your window, the gate would be comparing metrics that partially describe the

traffic split. The platform enforces this for you: if you request a wait period that's too short for your window, it increments it automatically. It is still better to design with it in mind: a 5m window needs a 6.5m wait period. With the default 5m window the platform grows the default 3m interval to 390s (6m 30s); if you set your own

, make it at least

By default, a tripped gate routes to

, which means the system

. The rollout holds at its current split (the blast radius stays at whatever your canary percentage was), and you decide: resume (the gate re-evaluates), promote, or cancel.

There is no automatic abort: a confirmed regression always parks the rollout for a human, because moving traffic back is itself a change someone should be watching. Recoverable causes such as a capacity shortfall or a metrics-pipeline gap are different: the platform retries those every 15 minutes for up to 3 hours before leaving the rollout paused for you. The platform also guards against false alarms: before it pauses on a regression the system re-queries several times over ~90 seconds to make sure it isn’t looking at ingestion lag or transient blips, and a gate that cannot get trustworthy data pauses with

rather than counting as a regression.

All three strategies run through the same step engine, so these hold for canary, blue-green and rolling alike.

Target replicas round up and the source drain rounds down, so a same-size swap never has fewer replicas than it started with. Rolling adds one replica mid-step; blue-green briefly runs both deployments at full size. Replicas your autoscaler added above the plan are kept.

Every step runs in one order: scale the target, check health, shift traffic, wait 30 s for routing to converge, drain the source, wait, evaluate the gate, record the step. A step that regressed during its wait is never recorded as passed.

Traffic moves only once the target has enough ready replicas for the new share, and the source is never drained below its remaining share. If a replica dies and the split can no longer be served, the rollout holds the largest split it can and pauses as

Each step writes each deployment's minimum replicas and nothing else, with one exception: the target's maximum is lifted once so it can carry the whole endpoint, and stays lifted. The source's maximum shrinks with its share during the drain. Lower a maximum below what the step needs and the rollout pauses as

instead of overriding you.

A regression check passes when the target is within your percentage budget of the source. No source data passes; a zero source against a non-zero target on a higher-is-worse metric fails; any other zero source passes. A threshold check ignores the source and compares the target with your value.

The wait period is at least the metric window plus about 90 s of ingestion lag, so a 300 s window means a 390 s wait. p95 needs 20 requests in the window and p99 needs 100; with fewer the rollout pauses as

. Error rate and in-flight requests need one.

The rollout checks feasibility for the

journey up front, before touching anything, and again at each scale-up. A shortfall pauses the rollout in

with a

category. At this point nothing has moved and your source is untouched. Resume re-checks capacity and continues if it's freed up. Capacity problems are usually transient, so pausing beats failing.

Yes. Pause is not a held connection but rather a first-class state. Rollouts are designed to survive multi-day pauses and resume exactly where they left off.

When the platform pauses a rollout,

carries a typed

plus a human-readable

. These include:

The docs list the remaining categories and what to do about each:

Everything above is easier to trust after watching it in action once, so here is a run on the current platform (September 2026). We upgraded a live endpoint from

to

, each on a single H100, while a steady 5 requests per second of chat completions flowed through the endpoint the whole time and every response code was logged. The newer model is the one we wanted; the question a rollout answers is whether it fits the latency budget the old one set. We gave it a 25% p95 budget.

The 7B was already serving. We added the 9B as a second deployment on the same endpoint with no traffic and no replicas; the rollout starts it when it needs it.

One command creates and starts the canary: 10% → 50% → 100%, with a gate that compares the target's p95 router latency against the source's over a 5-minute window after each step.

(time since the rollout started):

The regression is real, not a blip: the 9B is a reasoning model and, at the same max_tokens, generates more per request. That is a product decision rather than something to resume past, so we canceled and went back.

across the whole run, including the shift, the pause, the cancel and the reverse:

Every step above is in the endpoint's event feed, filterable by rollout ID:

An earlier run in July, with a deliberately impossible threshold gate, produced the same shape: a trip at 10% of traffic and 1,198 probe requests with zero errors through the recovery.

Keep your current deployment as the source and add the candidate as a target with zero traffic.

(2.34.0 or newer) gives you the

CLI:

with the default ladder (5% → 25% → 50% → 100%) and one router_latency regression gate:

with

(or the endpoint's Rollouts tab in the console) as it progresses through the steps. Pause, promote or cancel it with

Throughout, the endpoint URL and your clients stay unchanged; only the model behind them moves.
