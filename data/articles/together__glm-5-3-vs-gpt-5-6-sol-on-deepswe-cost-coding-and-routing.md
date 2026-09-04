---
url: https://www.together.ai/blog/glm-5-3-vs-gpt-5-6-sol-on-deepswe-cost-coding-and-routing
title: GLM-5.3 vs. GPT-5.6 Sol on DeepSWE: Cost, Coding, and Routing
site: together
date: 
scraped_at: 2026-09-04T21:13:22+00:00
---

Key Takeaways

Don't pick one. Run GLM-5.3 first, escalate to GPT-5.6 Sol when the tests fail. That cascade solves 85.9% of DeepSWE tasks at

6.61 each. Sol alone solves 72.7% at

8.37. Thirteen points better, 21% cheaper.

We ran

(max) against GPT-5.6 Sol (max) on all 113 DeepSWE tasks, four trials each, from the published per-trial records: 904 rollouts in total, 452 per side. Sol is the precision flagship. GLM-5.3 is the open-weight challenger that closed the gap. Every figure below comes from this run, so it can differ from other public GLM-5.3 vs. GPT-5.6 Sol scorecards.

DeepSWE · Head to Head

GPT-5.6 Sol still holds the single-shot crown on DeepSWE, a benchmark that tests a model's software engineering ability across many task types and programming languages. GLM-5.3 arrives less than four points behind it at half the price and pulls ahead the moment you allow more than one attempt. This is the closest the open tier has come to the frontier, and the question worth answering is what Sol's remaining premium actually buys.

Single shot, Sol edges ahead: 72.7% pass@1 to GLM-5.3's 69.0% under DeepSWE's official scoring. Allow retries and the order flips. At two attempts GLM-5.3 (81.1%) already ties Sol (81.0%); at four, GLM-5.3's 87.6% pass@4 leads 85.8%. The open model has the wider reach, so in any best-of-k setting it is the more accurate choice, and its extra attempts cost half of Sol's.

At

3.99 a rollout, GLM-5.3 is 2.1x cheaper than Sol (

8.37), which in value terms is 17 solves per

100 against Sol's 9. Sol buys that premium back on latency: an average 19 minutes and 61 steps against GLM's 35 minutes and 124 steps, with 60k output tokens to GLM's 80k. The tradeoff is unusually clean. Sol is the faster, terser worker; GLM-5.3 is the lower-cost one that takes the long route. If a human is waiting, Sol earns its premium on latency alone. If a budget or a batch queue is waiting, GLM-5.3 is the better buy.

Decompose pass@1 and pass@4 into coverage (tasks solved at least once across four tries) and reliability (tasks solved on all four), and the split is clean. Sol is the precision corner: 84.5% reliability and 61 tasks solved four for four, the marks of a model that lands what it touches. GLM-5.3 trades to the other axis: wider coverage at 87.6% against 85.8%, but lower reliability at 78.8% and fewer solid tasks, 48 against 61. That coverage edge is the same fact as its pass@4 lead. GLM-5.3 touches more of the benchmark than Sol and converts each touch a little less often per shot.

The failure profiles differ sharply, and the split favors the open model. Sol breaks the repository's existing test suite in 20% of its failures, the GPT-family regression signature. GLM-5.3 does so in 11%; when it misses, it usually misses forward, a near miss with the baseline intact, at a 61% near-miss rate against Sol's 54%. So the lower-cost model is also the safer one to accept without a heavy regression gate. Put a full regression run around Sol before you take its diff. GLM-5.3 needs that guardrail less.

The domain map splits evenly, four each. Sol takes data modeling and serialization (92%), build and ops tooling (73%), concurrency and durability (72%), and protocol conformance (59%), which is the exact-contract, systems-heavy work. GLM-5.3 takes query and config languages (88%, the highest single cell on the board), language and runtime internals (83%), stateful reactivity (73%), and program analysis, a 64 to 64 tie it holds on volume. That is the structured, interpreter-style work. GLM-5.3's one clear hole is protocol conformance at 44%, 15 points behind Sol. Sol has no single weak domain; it is simply strong across the board. Task types here were classified by an LLM from each benchmark prompt.

GLM-5.3's standout is JavaScript at 90%, 15 points clear of Sol's 75 and the best JS number of any model on the board. It also takes Rust, 70 to 60. Sol answers with Python (74 to 66), Go (79 to 76), and TypeScript (66 to 61). The routing rule is simple: JavaScript and Rust to GLM-5.3, the rest to Sol, with GLM-5.3 a lower-cost and close second almost everywhere.

Different enough to route on. Per-task correlation is 0.43, real disagreement for two models this close on aggregate. They both solve 90 tasks; GLM-5.3 alone gets 9, Sol alone gets 7, and 7 defeat both. Their union covers 106 of 113 tasks (93.8%), and the hard disagreements run one way: GLM-5.3 sweeps two tasks four for four that Sol never lands (koota-pair-relation-tracking, participle-grammar-conflict-analysis), while Sol sweeps none that GLM-5.3 zeros. The open model reaches places the flagship does not.

That divergence plus the price makes the cascade the best row on the board. Run GLM-5.3 first and escalate to Sol only when your test suite rejects the answer: 85.9% solved at

6.61 per task. That is thirteen points above Sol alone (72.7%) and still cheaper than one Sol rollout (

8.37), because the open model clears most of the queue at half of Sol's price and the hard remainder gets a second independent attempt. The cascade also beats a perfect one-shot oracle router (83.8%), because two independent attempts beat one perfect pick. Expected accuracy is the same whichever model leads, but GLM-first is cheaper (

6.61 against

9.47), so lead with the lower-cost model.

GPT-5.6 Sol keeps the single-shot crown and the things that come with it: the highest first-try rate, the highest reliability, and by far the fastest and most concise runs. You pay roughly double for that, and you must guardrail its 20% regression rate. GLM-5.3 is the value and best-of-k pick: within four points on the first shot, ahead on pass@2, pass@4, and coverage, at half the price, with a cleaner failure profile and the best JavaScript on the board. Its real weaknesses against Sol are protocol conformance and raw speed. And because the two genuinely diverge, the sharpest deployment is neither alone. It is GLM-5.3 as a lower-cost front end with Sol as the verifier-gated escalation, which lands flagship-beating coverage for less than the flagship's own per-task price. Check out new

DeepSWE · Full Results

113 DeepSWE tasks · 4 trials per config · both at max effort · 904 rollouts total

It depends on the metric. GPT-5.6 Sol wins single-attempt quality on DeepSWE (pass@1 72.7% against 69.0%), solves more tasks four for four (61 against 48), and is roughly twice as fast per rollout. GLM-5.3 ties pass@2 and wins pass@4 (87.6% against 85.8%) at half the cost per rollout, so it is the stronger value pick for high-volume or retry-tolerant agent work.

In our run, GLM-5.3 cost

3.99 per rollout against

8.37 for GPT-5.6 Sol at max effort, about 2.1x lower. Measured per solved task, GLM-5.3 returned 17 solves per

100 against Sol's 9, roughly twice the solved work per dollar.

They split the board. GLM-5.3 takes JavaScript (90 against 75) and Rust (70 against 60); Sol takes Python (74 against 66), Go (79 against 76), and TypeScript (66 against 61). By task domain it is four wins each: Sol leads the exact-contract and systems work, GLM-5.3 leads query and config languages, runtime internals, and stateful reactivity.

Yes, if you can verify results. The two diverge (0.43 correlation) and fail differently, so running GLM-5.3 first and escalating to Sol when your test suite rejects the output reaches 85.9% at

6.61 per task, beating Sol alone (72.7% at

8.37) and a perfect one-shot oracle router (83.8%). Together the two cover 106 of 113 tasks.

pass@k measures whether at least one of k attempts at a task passes the hidden test suite. pass@1 rewards getting it right first try; higher k rewards a model that can eventually reach a solution across several tries. GLM-5.3's edge grows as k increases.
