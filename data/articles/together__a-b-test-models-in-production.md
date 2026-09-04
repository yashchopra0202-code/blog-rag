---
url: https://www.together.ai/blog/a-b-test-models-in-production
title: A/B test models in production
site: together
date: 
scraped_at: 2026-09-04T21:13:27+00:00
---

Summary

A/B experiments allow you to split an endpoint's live traffic into fixed cohorts of one control and up to 20 variants, each with a percentage split of the traffic. This allows you to measure how a candidate model performs

at an exposure level you choose. Ramping up a variant can also be done with one call where you can promote the winner using a blue-green rollout. Deleting the experiment returns 100% of traffic to the control without the need to make any client-side or routing logic changes to unwind afterwards. Below we'll run an experiment on a live endpoint where we create at 95%/5%, ramp to 80%/20% and 50%/50%, then delete and check the observed traffic shares at every stage.

Sooner or later every team wants to answer the same question:

Not better on a benchmark but rather better on retention, thumbs-up rate, task completion, whatever your product actually measures.

can't answer that question. Shadowing tells you the candidate is

sound with respect to latency, errors, throughput, but its responses are discarded; no user ever acts on them. Quality questions need real exposure to end users where a cut of your users get model B, and you compare what happens.

Typically teams build this themselves in the application layer using some combination of:

It works, but it entangles your experiment with your infrastructure in ways that hurt later: the routing logic ships with your application, the cohort split can drift as clients cache decisions, and even after the experiment "ends" the branching code lives on long afterward because nobody's sure it's safe to remove.

The Together AI platform allows you to run A/B experiment logic at the endpoint level.

An A/B experiment attaches to an endpoint and declares members with exactly one

and one or more

, each pointing at a deployment, each with a

setting, that must sum to 100, controlling traffic routing.

How the endpoint router works is that whenever the base traffic sends a request to the control the experiment re-samples it among the arms and redistributes such that 95% stays on the control, 5% goes to the variant.

To be precise about the mechanism:

Routing first resolves a request through the weight split; when the winner is the control of an A/B experiment, the request is re-sampled among the experiment's arms by their percents. With the control as the only entrypoint in the split member percents therefore

absolute traffic shares. Also worth noting is that a control whose split weight is zero gives the experiment nothing to subdivide and as a result the whole experiment receives no traffic.

Importantly

the platform requires variants to carry zero weight; only the control lives in the base split. The experiment will own traffic routed to the variant entirely; its percentage

its traffic share. If a variant could also draw capacity-weighted traffic from the split, your measurements would be quietly wrong. One way to think about it is that you should set up the variant like a shadow deployment: created,

, weight zero and then let the experiment percentage setting route to it.

Another important point here is that A/B percents are

summing to 100% and are independent of replica counts. We made this deliberately different from traffic-split weights (which are per-ready-replica and follow capacity). An experiment is a

; you want the split to be constant while you measure and not drift with autoscaling.

Creating a 95/5 experiment:

Your clients won’t notice this experiment because on the surface the same endpoint name, API and keys persist. On the backend 5% of requests will now be answered by the variant candidate.

There's no separate "ramp" API, an update will

, which keeps the mental model simple (the experiment is always exactly what its members say) and makes every ramp an explicit reviewable change:

Updates are guarded by an etag because if a teammate ramped the experiment while you were composing your update, yours will be rejected instead of silently overwriting theirs.

With this API design you still need to make the common exposure choice of how much traffic to route to group B:

With up to

you can also run multi-way tests, lets say for example you want to try out a full-precision endpoint along with three other quantized variants (V1, V2, V3). This will work as expected as long as the percents still sum to 100% and there's exactly one control.

Every request is served by a specific deployment, and every

is available per deployment — so the infra side of the comparison (latency, errors, throughput per cohort) is a filter, not a project. The product side is yours: log which deployment served each response (it's in the response metadata) alongside your quality signals — ratings, retries, task completions — and the join key is just the deployment ID. The platform deliberately doesn't guess at your quality metrics; it makes the attribution trivial so your analytics can do the judging.

Suppose the experiment shows the variant wins. Ending it is a two-step process:

And if the variant loses, you can just delete the experiment and traffic will return entirely to the control. On the backend the variant deployment scales to zero or gets deleted.

Only its cohort. Deployments are independently monitored and independently autoscaled, which means that a struggling variant won’t drag the control down. To fix this you can resend the member set without the sick variant and its users will be back on control within a certain propagation time. This is also why starting at 5% is a good idea.

Over meaningful volume, yes! For an example of this in action check out the experiment below. Over small windows you can expect sampling noise: a 5% share of 1,000 requests is a small sample. If your observed share is off by a lot

stays off, check the setup rule above.

Yes, and the composition order is defined as: routing resolves the base split first, then A/B experiments (subdividing the control's share),

rollouts (re-sampling between a source deployment and its rollout target). The platform still enforces one

per endpoint but the stages are designed to compose if they overlap.

Assignment uses the request's

, for example a top-level

or

field in the request body, so requests carrying the same key route consistently and a given user can stay in one test arm across a session. Requests without a key are assigned effectively at random per request (our experiment measurements below used key-less traffic, which is why observed shares match the percents so closely). If per-user consistency matters to your study, especially if you have multi-turn quality comparisons, send a stable

field.

Each member deployment scales on its own policy, sized by its own share of traffic. A variant at 5% with bounds 1-2 and a control at 95% with bounds 2-8 is a perfectly normal shape. You should watch each cohort's replicas independently, this is what we capture in the chart below.

We ran the full lifecycle against a live endpoint where we create at 95/5, ramp to 80/20, ramp to 50/50 then delete. We do this while maintaining a steady 3 RPS stream, with every request attributed to the deployment that served it. The graph below shows traffic seen at the variant with green dots capturing variant traffic share:

Here are the configured vs observed traffic shares at every stage:

Three details from the run worth calling out:

Here's the experiment as the console shows it, on the endpoint's

tab (A/B tests and shadow tests share the page):

You need an endpoint with a control deployment serving traffic, plus a candidate deployment (created,

,

in the traffic split). Then:

📚

Dedicated Model Inference →
