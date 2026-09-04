---
url: https://www.together.ai/blog/glm-5-3-vs-glm-5-3-flash-on-deepswe-cost-coding-and-routing
title: GLM-5.3 vs. GLM-5.3 Flash on DeepSWE: Cost, Coding, and Routing
site: together
date: 
scraped_at: 2026-09-04T21:12:17+00:00
---

Key Takeaways

Run GLM-5.3 Flash first and escalate to the full GLM-5.3 only when your tests reject the answer. That cascade solves 80.9% of DeepSWE tasks at

1.70 each. GLM-5.3 alone solves 69.0% at

3.99. Twelve points better, 57% lower cost. If you are picking a single model, pick the Flash: it trails by 5.6 points on the first try but only 2.6 points by the fourth, because what distillation removed was reliability, and reliability is what retries buy back.

‍

and

are the same family at two sizes. GLM-5.3 is the full open-weight model; GLM-5.3 Flash is its distilled sibling at one-seventeenth the rollout price. The question every team asks about a flash variant is how much quality it gives up. On DeepSWE, a benchmark that tests a model's software engineering ability across many task types and programming languages, the answer is smaller than the headline pass@1 gap suggests, because the Flash is not a scaled-down clone of the full model. It is a redistribution of its abilities, and the thing it actually lost is not the thing the headline numbers point to.

DeepSWE · At a Glance

113 DeepSWE tasks · 4 trials per config · both at max effort · 900 rollouts total

We ran GLM-5.3 (max) against GLM-5.3 Flash (max) on all 113 DeepSWE tasks, four trials each, from the published per-trial records: 900 rollouts in total, 452 full and 448 Flash. What follows is the full comparison and the distillation autopsy in one place. Every figure below comes from this run, so it can differ from other public GLM-5.3 vs GLM-5.3 Flash scorecards.

Single shot, the full model leads by 5.6 points, 69.0% to 63.4%. That lead is a first-try artifact. It narrows to four points at pass@2 and to 2.6 points at pass@4, 87.6% against 85.0%. Distillation cost the Flash more of its single-shot polish than its ceiling. For any best-of-k workload the effective quality loss is under three points, at one-seventeenth the price. The collapse from 5.6 to 2.6 is the first clue to what changed, and the next section explains it.

Classify every task, for each model, as a wall (0 of 4 passing), flaky (some passing), or solid (all passing), then trace where the full model's tasks land in the Flash.

The top-right zero carries the section: of the 48 tasks the full model solves four for four, not one becomes unsolvable in the Flash. Half stay perfectly solid; the other half only lose consistency. Coverage retention says the same thing: of the 99 tasks the full model solves at least once, the Flash still solves 93, or 94%. Distillation did not remove the ability to solve these tasks. It removed the reliability. A consistency loss, unlike a capability loss, is exactly what retries recover, which is why the pass@4 gap is so much smaller than the pass@1 gap.

At

0.24 against

3.99, the Flash costs 17x less per rollout: 264 solves per

100 to the full model's 17. The usual flash tradeoff, slower per token, does not appear. The Flash is quicker, averaging 26 minutes to the full model's 35, and it does not get there by cutting corners: it runs the same number of steps, 123 against 125. The entire speed difference is per-step latency, 12.5 seconds per step for the Flash versus 17.0 for the full model, a smaller model executing each step about 27% faster in a smaller working window (145k average peak context to the full model's 155k). Lower cost, quicker, thinking the same length.

Group tasks by how reliably the full model solved them, then measure the Flash's mean pass rate in each group.

The result is a clean monotonic gradient: the more reliably the full model held a task, the more of that ability the Flash keeps. Distillation eats from the edges of the capability distribution and leaves the core intact. It sharpens the boundary between what the model can and cannot do rather than scaling the whole profile down.

This is the mechanism behind the flakiness, and the most surprising result in the study. On a flaky task, the question is whether the longer run tends to be the winning run. Same task, same difficulty, only the run varies.

So distillation did not only make the model a little worse per step. It removed the model's ability to

extra effort. This is not erratic exploration either: the Flash's within-task step variance is slightly lower than the full model's, a coefficient of variation of 0.12 against 0.14. It runs about the same length every time and sometimes lands, sometimes not. What it lost is the search ability that lets the full model turn a hard attempt into a solved one.

The losses are only half the ledger. The Flash gives capability back in specific places:

Across the eight domains the full model takes 5 and the Flash takes 3, and on languages the full model takes four (Go, TypeScript, JavaScript, Rust) to the Flash's one (Python). The full model wins the reasoning-heavy and JavaScript-heavy work; the Flash wins the systems and Python work. The Flash's JavaScript number looks alarming in isolation, but it rests on a five-task sample and is driven by a single task, so treat it as directional rather than settled. The broader read is that distillation reshaped the profile instead of simply lowering it.

The full model sits up and to the right on the coverage-reliability plane: 87.6% coverage at 78.8% reliability, against the Flash's 85.0% and 74.7%. The full model solves 48 tasks four for four to the Flash's 39, and walls out on 14 to the Flash's 17. Distillation shaved a little off both axes, but the Flash's run-to-run variance on the scoreboard grew more than its averages fell (pass@1 standard deviation 4.1 against 2.7), which is the same consistency story seen from the aggregate.

Not everything nets in the Flash's favor. Beyond accuracy and consistency, distillation made the model measurably less careful about collateral damage. Measured as the share of non-errored rollouts that break at least one already-passing baseline test:

The Flash is over 50% more likely to disturb working code when it acts. This is the one axis on which it is worse rather than merely lower-cost, and the one place to add a guardrail: run a full regression suite before accepting a Flash diff unreviewed.

Because the quality the Flash gives up is small and mostly recoverable, and the price it saves is large, a same-family cascade is a straight cost cut. Run the Flash first and escalate to the full model only when a verifier rejects the answer:

, above the full model's own single-shot pass@1 of 69.0% at less than half its price. Per-task correlation between the two is 0.61 and their union covers 102 of 113 tasks (90.3%), so the low-cost first stage clears most of the queue and the full model only ever sees the hard remainder, which then gets a second independent attempt.

Distillation of GLM-5.3 into GLM-5.3 Flash is a scalpel, not a hammer. It preserved capability and traded consistency: zero of the full model's solid tasks became unsolvable, and the pass@4 gap is 2.6 points, not 5.6. It removed the search ability that lets the model take a hard attempt to a win, an effort payoff of 61% falling to 46%, which is the true source of the flakiness. It reshaped the profile rather than shrinking it, gaining concurrency, Python, data modeling, and protocol while ceding JavaScript and query work, and the scariest headline in that set, the JavaScript drop, is a one-task effect in a five-task sample. Its single genuine regression is caution, a 6.9% baseline-break rate against 4.4%.

The economics dominate the rest: 17x lower cost per rollout, 264 solves per

100, faster wall clock, for under three points of best-of-k quality. Default to GLM-5.3 Flash for cost- and throughput-bound work and any best-of-k pipeline. Reach for the full GLM-5.3 when the task is JavaScript- or query-heavy or needs first-shot reliability. Gate the Flash with a regression run. And if you run the full model, front it with the Flash to more than halve the bill.

DeepSWE · Data Table

DeepSWE v1.1 · 113 tasks × 4 trials per config · both at max effort · Flash cost uses its current $0.24 average per task

Close, and closer the more attempts you allow. GLM-5.3 leads pass@1 by 5.6 points (69.0% vs 63.4%), but the gap falls to 2.6 points at pass@4 (87.6% vs 85.0%). None of the 48 tasks GLM-5.3 solves four for four become unsolvable for the Flash, so the loss is reliability rather than capability.

In our run, GLM-5.3 Flash cost

0.24 per rollout against

3.99 for GLM-5.3 at max effort, roughly 17x less. Measured per solved task, the Flash returned 264 solves per

100 to the full model's 17, about sixteen times the solved work per dollar.

It depends on the work. GLM-5.3 takes four of five languages (Go, TypeScript, JavaScript, Rust) and 5 of 8 domains, and it is the stronger pick for first-shot reliability and reasoning-heavy tasks. GLM-5.3 Flash leads on concurrency and durability (70 vs 62), Python (71 vs 66), data modeling (83 vs 79), and protocol work (48 vs 44).

Yes, if you can verify results. Running GLM-5.3 Flash first and escalating to GLM-5.3 when your test suite rejects the output reaches 80.9% at

1.70 per task, which beats GLM-5.3 alone (69.0% at

3.99) at less than half the price. Per-task correlation is 0.61 and the two together cover 102 of 113 tasks.

Add a regression gate. GLM-5.3 Flash breaks at least one already-passing baseline test in 6.9% of non-errored rollouts against GLM-5.3's 4.4%, so it is over 50% more likely to disturb working code. A full regression run before accepting a diff closes most of that gap.

pass@k measures whether at least one of k attempts at a task passes the hidden test suite. pass@1 rewards getting it right on the first try; higher k rewards a model that can eventually reach a solution across several tries. GLM-5.3 Flash's deficit shrinks as k increases, which is why it suits retry-tolerant pipelines.
