---
url: https://www.anthropic.com/engineering/claude-think-tool
title: The "think" tool: Enabling Claude to stop and think in complex tool use situations
site: anthropic-engineering
date: 
scraped_at: 2026-09-04T13:10:52+00:00
---

Extended thinking update

Dec 15, 2025

Extended thinking capabilities have improved since its initial release, such that we recommend using that feature instead of a dedicated think tool in most cases. Extended thinking provides similar benefits—giving Claude space to reason through complex problems—with better integration and performance. See our extended thinking documentation for implementation details.

As we continue to enhance Claude's complex problem-solving abilities, we've discovered a particularly effective approach: a "think" tool that creates dedicated space for structured thinking during complex tasks.

This simple yet powerful technique—which, as we’ll explain below, is different from Claude’s new “

” capability (see here for

)—has resulted in remarkable improvements in Claude's agentic tool use ability. This includes following policies, making consistent decisions, and handling multi-step problems, all with minimal implementation overhead.

In this post, we'll explore how to implement the “think” tool on different applications, sharing practical guidance for developers based on verified benchmark results.

With the "think" tool, we're giving Claude the ability to include an additional thinking step—complete with its own designated space—as part of getting to its final answer.

While it sounds similar to extended thinking, it's a different concept. Extended thinking is all about what Claude does before it starts generating a response. With extended thinking, Claude deeply considers and iterates on its plan before taking action. The "think" tool is for Claude, once it starts generating a response, to add a step to stop and think about whether it has all the information it needs to move forward. This is particularly helpful when performing long chains of tool calls or in long multi-step conversations with the user.

This makes the “think” tool more suitable for cases where Claude does not have all the information needed to formulate its response from the user query alone, and where it needs to process external information (e.g. information in tool call results). The reasoning Claude performs with the “think” tool is less comprehensive than what can be obtained with extended thinking, and is more focused on

information that the model discovers.

We recommend using extended thinking for simpler tool use scenarios like non-sequential tool calls or straightforward instruction following. Extended thinking is also useful for use cases, like coding, math, and physics, when you don’t need Claude to call tools. The “think” tool is better suited for when Claude needs to call complex tools, analyze tool outputs carefully in long chains of tool calls, navigate policy-heavy environments with detailed guidelines, or make sequential decisions where each step builds on previous ones and mistakes are costly.

Here's a sample implementation using the standard tool specification format that comes from

:

We evaluated the "think" tool using τ-bench (tau-bench), a comprehensive benchmark designed to test a model’s ability to use tools in realistic customer service scenarios, where the "think" tool is part of the evaluation’s standard environment.

τ-bench evaluates Claude's ability to:

The primary evaluation metric used in τ-bench is pass^

, which measures the probability that all

independent task trials are successful for a given task, averaged across all tasks. Unlike the pass@

metric that is common for other LLM evaluations (which measures if at least one of

trials succeeds), pass^

evaluates consistency and reliability—critical qualities for customer service applications where consistent adherence to policies is essential.

Our evaluation compared several different configurations:

The results showed dramatic improvements when Claude 3.7 effectively used the "think" tool in both the “airline” and “retail” customer service domains of the benchmark:

Claude 3.7 Sonnet's performance on the "Airline" domain of the Tau-Bench eval

The best performance in the airline domain was achieved by pairing the “think” tool with an optimized prompt that gives examples of the type of reasoning approaches to use when analyzing customer requests. Below is an example of the optimized prompt:

What's particularly interesting is how the different approaches compared. Using the “think” tool with the optimized prompt achieved significantly better results over extended thinking mode (which showed similar performance to the unprompted “think” tool). Using the "think" tool alone (without prompting) improved performance over baseline, but still fell short of the optimized approach.

The combination of the "think" tool with optimized prompting delivered the strongest performance by a significant margin, likely due to the high complexity of the

part of the benchmark, where the model benefitted the most from being given examples of how to “think.”

In the retail domain, we also tested various configurations to understand the specific impact of each approach

Claude 3.7 Sonnet's performance on the "Retail" domain of the Tau-Bench eval

The "think" tool achieved the highest pass^1 score of 0.812 even without additional prompting. The

is noticeably easier to navigate compared to the airline domain, and Claude was able to improve just by having a space to think without further guidance.

Our detailed analysis revealed several patterns that can help you implement the "think" tool effectively:

A similar “think” tool was added to our SWE-bench setup when evaluating Claude 3.7 Sonnet, contributing to the achieved state-of-the-art score of 0.623. The adapted “think” tool definition is given below:

Our experiments (

=30 samples with "think" tool,

=144 samples without) showed the isolated effects of including this tool improved performance by 1.6% on average (Welch's

-test:

(38.89) = 6.71,

< .001,

= 1.47).

Based on these evaluation results, we've identified specific scenarios where Claude benefits most from the "think" tool:

To get the most out of the "think" tool with Claude, we recommend the following implementation practices based on our τ-bench experiments.

The most effective approach is to provide clear instructions on when and how to use the "think" tool, such as the one used for the τ-bench airline domain. Providing examples tailored to your specific use case significantly improves how effectively the model uses the "think" tool:

We found that, when they were long and/or complex, including instructions about the "think" tool in the system prompt was more effective than placing them in the tool description itself. This approach provides broader context and helps the model better integrate the thinking process into its overall behavior.

Whereas the “think” tool can offer substantial improvements, it is not applicable to all tool use use cases, and does come at the cost of increased prompt length and output tokens. Specifically, we have found the “think” tool does not offer any improvements in the following use cases:

The "think" tool is a straightforward addition to your Claude implementation that can yield meaningful improvements in just a few steps:

The best part is that adding this tool has minimal downside in terms of performance outcomes. It doesn't change external behavior unless Claude decides to use it, and doesn't interfere with your existing tools or workflows.

Our research has demonstrated that the "think" tool can significantly enhance Claude 3.7 Sonnet's performance

on complex tasks requiring policy adherence and reasoning in long chains of tool calls. “Think” is not a one-size-fits-all solution, but it offers substantial benefits for the correct use cases, all with minimal implementation complexity.

We look forward to seeing how you'll use the "think" tool to build more capable, reliable, and transparent AI systems with Claude.

1. While our τ-Bench results focused on the improvement of Claude 3.7 Sonnet with the “think” tool, our experiments show Claude 3.5 Sonnet (New) is also able to achieve performance gains with the same configuration as 3.7 Sonnet, indicating that this improvement generalizes to other Claude models as well.
