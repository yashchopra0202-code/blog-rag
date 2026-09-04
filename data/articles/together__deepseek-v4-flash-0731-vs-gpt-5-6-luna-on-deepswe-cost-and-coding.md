---
url: https://www.together.ai/blog/deepseek-v4-flash-0731-vs-gpt-5-6-luna-on-deepswe-cost-and-coding
title: DeepSeek-V4 Flash 0731 vs GPT-5.6 Luna on DeepSWE: Cost and Coding
site: together
date: 
scraped_at: 2026-09-04T21:13:32+00:00
---

Key Takeaways

While GPT-5.6 Luna is the stronger engineer on every quality measure, DeepSeek-V4 Flash 0731 is cheap enough that a DeepSeek-first cascade beats Luna alone on both accuracy and cost.

‍

is the cheapest model on the entire DeepSWE board: about ten cents a task! GPT-5.6 Luna, a solid upper-tier flagship, runs

0.61 a task, roughly six times DeepSeek’s price. So the question is not which one wins the leaderboard (Luna, comfortably) but what six-times-cheaper buys you, what it costs you, and whether the two together beat either one alone.

We ran DeepSeek-V4 Flash 0731 (max) against GPT-5.6 Luna (max) on all 113 DeepSWE tasks: real, long-horizon feature requests from live open-source repos, four trials each, graded pass/fail by a hidden test suite. That is 900 rollouts in total from the published per-trial records (452 on DeepSeek's side, 448 on Luna's). Every figure below comes from this run, so it can differ from other public scorecards.

DeepSWE · Head to Head

Luna is ~6x the cost for ~14 points more accuracy; DeepSeek uses more output tokens and steps to get less far, but at

0.10 it is the cheapest run in the set by a wide margin.

Luna wins single shot clearly: 67.2% pass@1 to DeepSeek's 53.3% under DeepSWE's official scoring, a 14 point lead, or about 26% more accurate in relative terms. At equal attempt counts Luna stays ahead at every k (81.6 vs 70.1 at two attempts, 90.3 vs 80.5 at four). On raw solving ability, this is not a close fight.

But DeepSWE is exactly the kind of workload where you can fan out several attempts in parallel, and there the economics rewrite the picture. DeepSeek's pass@2 (70.1%) already edges Luna's single shot (67.2%), and two DeepSeek attempts cost about

0.20 to Luna's

0.61. If a verifier can pick the winning run, the cheap model matches the flagship's first-try quality for a third of the price, before any of the routing tricks below even come into play.

The other thing the cheap model quietly wins is discipline. When DeepSeek fails, it breaks the repository's existing test suite in only 9% of failures. Luna does so in 15%: the GPT-family regression signature, the same 15 to 20% we see across Sol and the other OpenAI-lineage models. Both fail mostly by near miss (DeepSeek 69%, Luna 66%), but the more expensive model is the one more likely to disturb code that already worked. If you deploy Luna, gate it behind a full regression run; DeepSeek needs that guardrail less.

Classify the 113 tasks by what the code actually is, and Luna wins 7 of 8 domains. Its biggest edges are exactly the reasoning-heavy work: program analysis (69 vs 33), concurrency and durability (70 vs 38), language and runtime internals (86 vs 59), roughly a 30 point gap in each. This is where model capability actually shows up, and DeepSeek falls off hard.

DeepSeek holds exactly one domain, and it is a telling one: query and config languages, 78 vs 70. The SQL builders, window functions, keyset pagination, config parsers. Structured, schema-shaped, convention-following work is where the cheap model is genuinely competitive, even ahead. Everywhere the task demands holding a hard invariant across a whole system, Luna's capability separates.

Luna wins all five, but the margins tell you where to be careful with DeepSeek. It is respectable on Rust (55 vs 60) and Go (62 vs 79), but its JavaScript is a collapse: 35 vs Luna's 60, the weakest single cell in the entire matchup, and a 25 point hole. DeepSeek's Python is also soft (49 vs 65). If your stack is JS-heavy, the cheap model is a false economy; if it is config, query, or Rust, DeepSeek closes most of the gap.

Less than the cheap-tier pairs. Per-task correlation is 0.50, and the diversity is lopsided: they both solve 87 tasks, Luna alone gets 15, and DeepSeek alone gets only 4. Crucially, there is no task DeepSeek sweeps that Luna misses entirely (zero four-for-zero corners in DeepSeek's favor), while Luna sweeps four that DeepSeek never lands (go-critic-doc-link-checker, langchain-request-coalescing, meriyah-explicit-resource-declarations, superjson-error-stack-serialization). Their union covers 106 of 113 (93.8%), but almost all of that is Luna's own reach. As a raw diversity play, DeepSeek adds little.

So the pairing should be pointless. It is not, and the reason is the price. Run DeepSeek first and escalate to Luna only when your test suite rejects the answer: 78.9% solved at

0.385 per task. Read that carefully. It is more accurate than Luna alone (67.2%, up 11.7 points) and cheaper than Luna alone (

0.61), landing at about 63% of Luna's per-task cost.

The near-free first stage is the entire trick: DeepSeek clears roughly 53% of the queue for a dime each, so Luna's charge only ever touches the hard remainder, and the tasks that reach Luna get a second independent attempt on top. The cascade even beats a perfect one-shot oracle router (74.3%), because two swings beat one perfect pick. Accuracy is identical whichever model leads, but DeepSeek-first is much cheaper (

0.385 vs

0.64), so always lead with the cheap one.

The pair's ceiling is 93.8%; the 7 tasks neither ever solves (including gql-incremental-graphql-delivery and bandit-structured-nosec-directives) need a stronger third model, not a better router.

On its own, DeepSeek-V4 Flash 0731 is a mid-pack model with one real domain (query and config), a clean failure profile, a catastrophic JavaScript weakness, and an unbeatable price. GPT-5.6 Luna is the better engineer by every quality measure: 14 points of pass@1, 7 of 8 domains, all 5 languages, faster too. You pay about 6x for it, plus a GPT-family regression habit to guardrail. At

0.61 a task the flagship is genuinely cheap, and it is the easy default when quality is what you care about. But the sharpest use of DeepSeek is not as a Luna replacement; it is as a Luna front-end. A first stage that costs a dime and clears half the work lets you buy flagship-beating accuracy for less than the flagship's own price. When the cheap model is this cheap, the cascade stops being a compromise and becomes the best row on the board.

DeepSWE · Appendix

On quality, yes. GPT-5.6 Luna wins DeepSWE pass@1 67.2% to 53.3%, leads at every equal attempt count, wins 7 of 8 task domains and all 5 languages, and is faster. DeepSeek-V4 Flash wins on price by roughly 6x per rollout and fails more cleanly when it does fail.

In our run, DeepSeek-V4 Flash cost about

0.10 per rollout versus

0.61 for GPT-5.6 Luna, roughly a sixth of the price. Measured per solved task, DeepSeek returned 532 solves per

100 against Luna's 110, about 4.8x the work per dollar.

Yes, in a cascade. Running DeepSeek first and escalating to Luna only when the test suite rejects the answer solved 78.9% of tasks at

0.385 each in our run: more accurate than Luna alone (67.2%) and cheaper than Luna alone (

0.61). Always lead with the cheap model; accuracy is the same either way but DeepSeek-first costs less.

Luna wins every language in our breakdown, but the margins vary. DeepSeek is respectable on Rust and competitive on query and config work, where it actually leads. Its JavaScript is the weakest cell in the matchup (35 vs 60), so JS-heavy stacks should not rely on the cheap model alone.

pass@k measures whether at least one of k attempts at a task passes the hidden test suite. pass@1 rewards getting it right first try; higher k rewards a model that can eventually reach a solution across several tries. DeepSeek's pass@2 (70.1%) already edges Luna's pass@1 (67.2%), which is what makes the parallel-attempt and cascade economics work.
