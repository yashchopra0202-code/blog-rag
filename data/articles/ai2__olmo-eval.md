---
url: https://allenai.org/blog/olmo-eval
title: olmo-eval: An evaluation workbench for the model development loop
site: ai2
date: 
scraped_at: 2026-09-04T21:11:57+00:00
---

June 12, 2026

While you're building an LLM, you evaluate it over and over across many interventions. Every adjustment to its data, architecture, or hyperparameters – and every step up in scale – sends you back through the same loop: adding or reconfiguring benchmarks, re-running them on each new model checkpoint, noting the results, and checking whether something that helped in a small experiment still holds up on the full training run. Most evaluation tools aren't designed for this—they’re either built to run established benchmarks across finished models or run a model through multi-step, tool-using problems in a sandbox. They don’t keep up with a model that's constantly changing, nor do they reflect how a model might behave under specific real-world conditions.

Our last project to address this evaluation challenge was

, the Open Language Model Evaluation Standard. Introduced in 2024, it was meant to make LLM benchmark scores easier to compare across releases. The same models were being scored on the same benchmarks in different ways – aspects like prompt formatting and task formulation often varied from paper to paper – so claims about which models performed best often weren't reproducible. OLMES pinned benchmarking choices down in an open, documented standard, and it became the basis for evaluating our open models from Olmo to Tulu.

But a model's final score is only part of the evaluation process—which is why we're releasing

, a new workbench that builds on OLMES and extends it across the rest of LLM development. Compared to OLMES, olmo-eval cuts down the work of implementing new evaluations, offers more flexibility in defining where and how they run, and makes it easier to compose individual components into larger workflows. Agentic and multi-turn evaluation is supported as a first-class use case, and stronger analysis tools help you judge whether an intervention actually improved on the baseline or the difference amounts to noise.

olmo-eval overlaps in some ways with Harbor, an open framework for evaluating AI agents inside containerized, sandboxed environments. But the two tools differ in their scope. Harbor is aimed mainly at running and publishing agent benchmarks; olmo-eval was built for the everyday work of developing a model—adding and configuring benchmarks, running them across checkpoints, and analyzing the results prompt by prompt instead of as a single overall score.

Harbor runs everything the same way—inside sealed, reproducible containers. Because containers can be resource-intensive, olmo-eval lets you choose how each benchmark runs instead. A benchmark that just needs a model to answer questions can run directly, which is faster and cheaper; a benchmark that needs a locked-down environment – say, one that runs code the model wrote – gets an isolated container setup. The lightweight path is the default, and olmo-eval only opts for the heavy setup when a benchmark actually requires it.

Harbor's process for adding a benchmark is built for evals you plan to publish and share publicly, with the extra verification steps that entails. olmo-eval is built for moving quickly while you develop, and how you add a benchmark depends on what the benchmark needs: a short definition for a basic eval, with options to let a model use tools as it works through a benchmark, or – for a benchmark that already has its own code and procedure – a thin wrapper so olmo-eval can run it as is and report the results alongside other benchmark scores in the same format.

Both Harbor and olmo-eval keep benchmarks separate from the runtime policy (how the model is run to produce its answers) so you can change one without rewriting the other, but olmo-eval is designed for greater modularity. In olmo-eval, the model being evaluated, the tools it can use, the containerized environment, and any helper models – like an LLM-as-a-judge – are all swappable components. You can reuse a tool across many harnesses, or plug a grading model into one benchmark without perturbing the others, and adjust small settings (e.g., the exact wording of the prompt) without extensive effort.

Harbor reports an overall score for each model. olmo-eval reports those scores too, each with a standard error and a minimum detectable effect (the smallest difference that can be reliably distinguished from noise). But the more useful view lines the same questions up across two model checkpoints and compares them one by one, with all else held fixed. This helps you to see whether a tiny change in an overall average might indicate a real improvement or simply noise.

olmo-eval is composed of four components that are useful on their own but designed to work together to tighten the experimental LLM development loop:

In most model evaluation setups, adding a benchmark is a sizeable integration project. In olmo-eval, all that’s needed is a

—tasks define the benchmark dataset, how evaluation requests are built, and how model answers are scored:

Variants express changes in evaluation policy without duplicating the benchmark:

Suites group benchmarks into standard sets you run together:

And because runtime policy lives in the harness rather than the task definition, the same benchmark can be easily rerun under different execution rather than relying on whether a generated point track merely looks plausible.

Use

when evaluation is part of ongoing model development rather than a one-off run—when you need to run the same benchmarks repeatedly across checkpoints under reproducible conditions and compare interventions at both the aggregate and per-question level.

If your recurring question is "How does this checkpoint differ from the last one, and where exactly did it improve or regress?", that’s the workflow olmo-eval is built for.

Reproducible evaluation should keep pace with how models are built—not only how they're scored once they're finished. olmo-eval carries the OLMES standard into active model development, and we're releasing it openly so the community can build on it.
