---
url: https://cohere.com/blog/north-mini-code
title: Introducing North Mini Code: Cohere’s first model for developers
site: cohere
date: 
scraped_at: 2026-09-04T13:24:47+00:00
---

Today we're launching North Mini Code open-source. A mixture-of-experts (MoE) model, North Mini Code is Cohere's first agentic coding model, and the inaugural member of our next generation of powerful models.

At 30B total parameters with just 3B active, North Mini Code delivers strong software development performance without demanding extensive hardware to match. Efficient by design, it's built to run where you need it.

Freely available under an

license, North Mini Code advances Cohere’s mission to make sovereign AI a practical reality, giving developers direct access to agentic coding capabilities. We're building in the open, because the future of AI should be shaped by the people running, testing, and improving it.

Download the weights on

(

,

,

), or deploy in a dedicated, managed inference environment on

. Alternatively, try it in your harness of choice on

,

, or with a

. Share what you build and tag @ Cohere on

or

, or engage with us on

.

North Mini Code achieves competitive scores across benchmarks against models of this size class, demonstrating strong performance in real-world software engineering tasks.

North Mini Code’s benchmark scores

, a competitive position among similarly sized models.

North Mini Code is designed for speed and efficiency, with a strong focus on minimizing total cost of ownership as we continue to refine and scale the model.

In our testing, North Mini Code achieved up to 2.8x higher output throughput than Devstral Small 2 under identical concurrency levels and hardware configurations. In practical terms, that translates to nearly three times the work rate, enabling faster iteration while reducing computational overhead.

North Mini Code also demonstrated a 30% advantage in inter-token latency, a metric that reflects the consistency and pacing of token generation. Time-to-first-token (TTFT) performance was more closely matched between the two models, with Devstral Small 2 maintaining a slight edge across the tested conditions.

North Mini Code is our first open-source model for developers. As coding agents transform software engineering, developers need control and flexibility over their agentic coding infrastructure.

North Mini Code represents a step forward in small agentic coding models that can accomplish tasks that matter to developers. Specifically, it is built for agentic workflows, including understanding and orchestrating sub-agents, mapping systems architecture, and running code reviews. Deploy on-prem or locally, on your own terms.

Community feedback will directly shape our roadmap as we expand the ecosystem toward more open and sovereign developer models. Try North Mini Code when you need freedom from vendor constraints, and help us build what's next.

North Mini Code launches as the first — but certainly not the last — of Cohere's new generation of powerful models, designed for a more sovereign open-source ecosystem.

We're committed to increasing our capabilities, with community input informing what comes next.

Help us build a complete sovereign AI ecosystem for software development by trying North Mini Code. North Mini Code is available for free on

(

,

,

),

, and

— our fully managed inference platform. We've specifically trained it for compatibility with

, but it works with most coding agents.

Share what you build and tag @ Cohere on

or

, or engage with us on

to help shape the future of sovereign models.

Visit our

for detailed model specs, deployment guides, and cookbooks to get started.

We used publicly reported scores for competitor models either from original reports or Artificial Analysis Intelligence Index where available. Additionally, Gemma 4’s scores for agentic coding tasks were reported by

. For the benchmark results that any public report is missing denoted by (*) in Image 1, we run internally with recommended model configuration.

We evaluated North Mini Code using “SWE-agent” harness for SWE-Bench Verified and SWE-Bench Pro, and a simple ReAct harness employing a single terminal-use tool for Terminal Bench v2. For Terminal Bench Hard, we used Terminus-2 harness for both North Mini Code and the other models that are evaluated internally.

Written By

Cohere Team

Tags

Share

AI isn’t a shortcut.

It’s how business gets ahead.
