---
url: https://www.together.ai/blog/kimi-k3-guide
title: Kimi K3: the complete developer guide
site: together
date: 
scraped_at: 2026-09-04T21:13:53+00:00
---

What you'll learn

Kimi K3 is Moonshot AI's most capable model to date: a 2.8-trillion-parameter model and the world's first open-source model in the 3-trillion-parameter class. It is designed for frontier intelligence work like long-horizon coding, end-to-end knowledge work, and deep reasoning. It is also the first open-weights model competing at the GPT 5.6 Sol and Claude Fable 5 tier, and Together AI is working directly with the Moonshot team to serve it.

The Kimi team is deeply committed to scaling, and it shows: in nine of the twelve months from July 2025 to July 2026, Kimi models set the upper bound of open-model scale. At 2.8 trillion parameters, K3 is now the largest open-weight model ever released.

Two architectural updates form K3's backbone, both designed to help information flow more easily through longer sequences and deeper into the network:

On top of that, Moonshot pushed Mixture-of-Experts sparsity further with the Stable LatentMoE framework, efficiently activating 16 of 896 experts. At this level of sparsity, roughly 2% of experts activated per token, routing and optimization become first-order challenges, so several supporting techniques enable stable training at 2.8T scale:

The API is OpenAI-compatible. The snippets below target Together AI and use the official Together Python SDK.

K3 can be configured with the top-level reasoning_effort field. Three levels are supported: low, high, and max, with max as the default. On Together, thinking can also be switched off via the standard reasoning={"enabled": False} toggle.

Streaming responses deliver separate reasoning_content (the thinking trace) and final-answer content deltas.

Multiple images can be provided as input. Moonshot has also released a visual reasoning benchmark,

.

Use response_format with json_schema and strict: true to constrain the final message.content.

The looser {"type": "json_object"} mode also works on Together when you only need syntactically valid JSON. Either way, keep max_tokens generous: the whole thinking trace is spent before the first schema-constrained token is emitted, so a tight cap truncates the JSON rather than the reasoning.

K3 keeps the standard tool-choice constraints. The standard loop: declare functions in tools; when the model returns tool_calls, append the complete assistant message to history, then append one tool message with the matching tool_call_id for each call, then call again. Use tool_choice="required" on a first turn to force at least one tool call, and switch back to "auto" afterward. Changing tool_choice does not invalidate the prefix cache.

You can place a complete tool definition (full name, description, and parameters) inside a system message that carries a tools field and no content. The tool becomes available from that message's position onward.

Key rules:

Recommended pattern for large tool catalogs:

Code Example:

Together supports the full 1M context length, and context caching is automatic. Keep your long prefix (system prompt, knowledge base, repo dump) byte-stable across requests so later calls can hit the cache. Moonshot recommends placing fixed bulk context (knowledge documents) at the very beginning of the messages array, ahead of the system message, then appending questions and replies after it.

The sampling parameters are fixed and you should omit them from requests. The model was trained using these params and does not support setting alternatives:

K3 was trained in preserved thinking history mode, so the trace is the state the next turn depends on. Use the following to preserve thinking tokens from the previous turn and forward them to future turns.

Drop the reasoning_content line and the same call answers with a different freshly-invented number every time. In real code you never hand-write the trace; you replay what the model produced, which is the one-liner from the tool loop:

Kimi K3 is priced per token, with a cache-hit input tier that rewards stable prefixes:

Two cost aspects to internalize:

Across the evaluation suite, Kimi K3 posts frontier-level numbers. It leads the field on several coding and agentic benchmarks (SWE Marathon, BrowseComp, DeepSearchQA, AutomationBench, OmniDocBench) and stays competitive with the strongest proprietary models on others, while clearly outperforming the other open model tested, GLM-5.2. On a handful of benchmarks it trails Claude Fable 5 and GPT 5.6 Sol, which is consistent with Moonshot's own positioning of the model.

All Kimi K3 results below use reasoning effort set to max.

Aggregate benchmark tables only go so far. For a head-to-head read on cost, coding quality, and routing behavior, we ran Kimi K3 against the leading proprietary models on DeepSWE:

Kimi K3 is Moonshot AI's flagship 2.8-trillion-parameter model and the first open-source model in the 3-trillion-parameter class, built for long-horizon coding, knowledge work, and reasoning.

Yes. It is released as an open-weights model, and Together AI works directly with the Moonshot team to serve it.

1M tokens (1,048,576), supported in full on Together AI with automatic context caching.

0.30 per 1M cache-hit input tokens,

3.00 per 1M cache-miss input tokens, and

15.00 per 1M output tokens.

On Together AI you can disable thinking with reasoning={"enabled": False}, or dial reasoning depth with reasoning_effort set to low, high, or max.

Yes. It has native vision and accepts multiple images per request, as long as the total request body stays under 100 MB.

Making K3 yours starts with a single API call.
