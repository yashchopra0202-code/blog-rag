---
url: https://www.together.ai/blog/kimi-k3-vs-gpt-5-6-sol-on-deepswe-cost-coding-and-routing
title: Kimi K3 vs GPT-5.6 Sol on DeepSWE: Cost, Coding, and Routing
site: together
date: 
scraped_at: 2026-09-04T21:14:17+00:00
---

Summary

GPT-5.6 Sol edges Kimi K3 on single-shot quality, but Kimi wins on pass@k with k > 1 and costs 64% less per completed task. The two models succeed and fail in different ways, which makes routing between them the strongest play on the benchmark.

DeepSWE · Head to Head

In our Kimi K3 vs GPT-5.6 Sol comparison on DeepSWE, a benchmark that tests a model's software engineering ability across many task types and programming languages, the story is not who sits at the top of the leaderboard. GPT-5.6 Sol took the pass@1 crown two weeks ago with 72.7% under DeepSWE's official scoring, the strongest single shot and the highest reliability ever recorded on the benchmark. Kimi K3, the open-weight newcomer, answers on the other axis: 89.4% pass@4, better than every flagship on the board, Sol included, while costing

4.65 a rollout to Sol's

8.37. We analyzed all 904 graded rollouts (113 tasks, four trials each, at max effort on both sides) from the published per-trial records at deepswe.datacurve.ai.

Given a single attempt, Sol wins clearly: 72.7% to 68.5% under DeepSWE's official scoring. But the gap closes fast. At two attempts Kimi K3 is already ahead, 82.0 to 81.0. At four attempts, Kimi's 89.4% beats Sol's 85.8% by 3.6 points, the best pass@4 of any flagship-tier config on the board.

The two are tied on Go (79 each). Sol leads Python (74-68), TypeScript (66-60), and JavaScript (75-65). Kimi K3 takes Rust (65-60).

Decompose pass@1 and pass@4 into coverage (tasks solved at least once across four tries) and reliability (tasks solved on all four), and the two models sit in opposite corners. Sol posts 84.5% reliability with 61 tasks solved four-for-four, across a modest 85.8% of the benchmark. Kimi K3 reaches 89.4% coverage, wider than any flagship, but only 76.6% reliability and 45 rock-solid tasks. Sol is steadier and more deterministic; Kimi K3 casts the wider net.

Where Kimi K3 versus Fable was essentially an echo chamber (0.72 correlation), Kimi K3 and Sol diverge: per-task correlation is 0.46, with four-for-four-versus-zero-for-four corners in both directions. The models succeed and fail in genuinely different ways. That is exactly what makes them a strong pair to route and cascade between: together they cover 108 of 113 tasks (95.6%), the best two-model portfolio on the benchmark.

Because the two disagree on 18 of 113 tasks, routing turns that disagreement into free accuracy. How much you capture depends on whether you have a verifier (your test suite) to catch a bad answer and escalate.

The practical answer is about 85.6%: run Kimi K3 first and escalate to Sol only when the test suite rejects the result. That beats either model alone and even a perfect one-shot router (83.4%), because the cascade gives hard tasks two independent attempts instead of committing to one. It is also cheaper per solve than Sol alone, since Kimi K3 clears roughly 70% of the queue before Sol is ever invoked. The verifier does the heavy lifting: without one, a realistic router lands in the 70s and 83.4% is the ceiling.

DeepSWE · Routing strategies

The hard ceiling for this pair is 95.6%. Five of the 113 tasks are solved by neither model across all eight combined attempts. Past 95.6% you need a third model, not a better router.

To route well, classify tasks by what the coding ask actually is. Sol leads 5 of 8 domains, Kimi K3. Send serialization (92-79), concurrency (72-55), and program analysis (64-56) to Sol. Send ops tooling (79-73) and runtime internals (77-75) to Kimi K3. Conformance is a 61-59 coin-flip. Task types here were classified by an LLM from each benchmark prompt.

They fail in very different ways - Kimi K3 gets close but doesn't pass all tests whereas Sol breaks more of the baseline tests. Sol breaks the repo's existing tests in 20% of failures - this is pretty consistent with other GPT models actually. Kimi K3: 11% base tests failed but 65% near misses where > 80% new tests were passing but some failed!

Kimi K3 ships as an open-weight model, which is what makes the pass@4 reach, the low cost, and the routing story above usable on your own terms. Once the weights are available, Together AI's inference stack is built to serve open models like Kimi K3 at production scale, so you can run the Kimi-first cascade and chase the wider pass@k net without frontier token prices.

See

to size it against your workload.

It depends on the metric. GPT-5.6 Sol wins single-attempt quality on DeepSWE (pass@1 72.7% vs 68.5%) and solves more tasks four-for-four. Kimi K3 wins pass@2 and pass@4 and costs far less, so it is the stronger value pick for high-volume or retry-tolerant agent work. For most teams the best answer is to route between them.

In our run, Kimi K3 cost

4.65 per rollout versus

8.37 for GPT-5.6 Sol, a little over half the price. Measured per solved task, Kimi K3 returned 14.7 solves per

100 against Sol's 5.3, about 2.8x the work per dollar.

Yes, if you can verify results. The two models diverge (0.46 correlation) and fail differently, so running Kimi first and escalating to Sol when your test suite rejects the output reaches about 85.6%, beating either model alone and even a perfect one-shot router. Together they cover 108 of 113 tasks.

For coding they are close. They tie on Go; Sol leads Python, TypeScript, and JavaScript; Kimi takes Rust. Sol is steadier on any single attempt, while Kimi casts a wider net across multiple attempts.

pass@k measures whether at least one of k attempts at a task passes the hidden test suite. pass@1 rewards getting it right first try; higher k rewards a model that can eventually reach a solution across several tries. Kimi K3's edge grows as k increases.

‍
