---
url: https://www.together.ai/blog/99-9-uptime-for-inference
title: What does 99.9% uptime mean for inference?
site: together
date: 
scraped_at: 2026-09-04T21:14:45+00:00
---

Reliability numbers are easy to publish. What’s hard is explaining what they mean: which failure domains the architecture actually covers, whether the provider controls the infrastructure at those layers, and what happens when something breaks at 3 a.m.

Together runs inference for teams like Cursor, Decagon, Cartesia, and Yutori. We’ve been paged for most of what follows; here’s what we’ve learned.

When inference goes down, someone’s product goes down with it. GPU inference fails differently from conventional services. The hardware has failure modes; CPU infrastructure doesn't, and the systems are tuned hard for performance. Hitting 1M tokens per minute per GPU at 200 TPS, or sub-50ms TTFT on voice models with custom kernels, leaves limited slack. Adding reliability to a system like that is exponentially harder with each nine.

The useful mental model is layers, and the failure modes in each one are distinct:

None of these fail in isolation. A storage hiccup surfaces as a capacity problem, a thermal event shows up as degraded output quality long before any health alert fires. Getting good at this means learning to read the real signal from the misleading symptom.

Each tier is a different engineering problem, not just a harder version of the same one. Here’s what each one actually takes, and what we’ve built around it.

The goal is to catch a degrading node before a request reaches it. Detect fast, drain, replace. The interesting engineering problem is observability.

Passive health checks (hardware telemetry, metrics) give you visibility without capacity overhead, but miss a class of failure that only shows up under real GPU load. Active health checks catch those, but they require capacity to run. You can’t exercise a GPU that’s already serving traffic, since this creates obvious tension. Everyone wants to run near 100% utilization, and maintaining excess capacity for health checks just trades reliability for inefficiency. That path we’ve taken is getting fast at rescheduling: integrating checks with the scheduler so they run in the gaps between workloads, and making the checks themselves as quick as possible. It’s still something we tune.

The ceiling at this tier is the building itself. A thermal issue, a substation event, an edge router failure. Any of these takes a single-DC deployment down regardless of in-DC redundancy. Most providers have backup systems for this, but a redundant system that isn’t regularly tested under real conditions is like calling a player off the bench who hasn’t practiced in six weeks. The failover might be there on paper, whether it works is a different question.

The whole facility is the failure domain here: Power, cooling, network ingress, edge networking. What surviving it requires: Weights deployed across two facilities, enough capacity on each side to absorb the full load, and routing traffic that shifts cleanly.

The architectural decision that defines whether a provider actually delivers this tier is whether they run live traffic to both facilities continuously, or maintain a cold standby. We chose continuous. Most 99.9% SLA claims implicitly promise this tier. The question is whether the architecture behind the claim is actually built for it.

This is also where infrastructure ownership matters concretely. A provider renting capacity from a hyperscaler or neocloud doesn’t own their failure domains. When something breaks at the power or cooling layer, they’re filing a ticket with whoever does. They can’t tell you what their SLA physically survives at that layer because they don’t control it. When you’re with Together AI, one ticket covers the hardware, network, storage, and software because we have chip-to-token visibility across our entire global footprint. The alternative: ticket to the provider, ticket from the provider to hyperscaler/neocloud, queue. We’ve seen what that looks like at 3 a.m.

The underlying challenge at this tier is that we’re building reliable infrastructure on inherently unreliable hardware. GPU failure rates are meaningfully higher than CPU failure rates, and every failure mode has to be accounted for. What four nines requires: multi-region deployment with AZ redundancy, and reserved capacity in the failover region sized to absorb a full regional outage. The key word here is reserved. Not “we can route traffic there” but “we have room sitting idle there right now.”

SLAs are a starting point. These questions get to the architecture underneath it, who owns what when things break, and how fast recovery happens. We’d expect you to ask them of us too:

Vague SLA definitions are where the gap between what’s promised and what’s delivered lives. Here’s exactly what we measure and how we define each term.

‍

We measure at inference completion, not at the gateway. A request that reaches the load balancer but fails at the GPU is downtime in our accounting. One more thing: availability and performance are different contracts. In Provisioned Throughput, you’re paying for a GPU allocation to deliver specific TPS, not just for the endpoint to respond. A service that’s up but delivering 30% of contracted throughput isn’t meeting the deal.

Every provider will give you a number. What matters is whether the architecture behind it is built to back it up, and whether they own the infrastructure where the guarantee has to hold.

Those are answerable questions. Ask any provider to walk through the architecture behind each SLA tier. Ask whether they own the infrastructure or sit above someone else’s. Ask whether the failover paths run under live traffic. A provider that knows their infrastructure can answer these quickly.

We can walk you through ours anytime. If you want to dig in, we’re here.
