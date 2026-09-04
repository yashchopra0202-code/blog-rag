---
url: https://mistral.ai/news/agentic-search/
title: Agentic Search. More accurate and efficient results from your AI systems.
site: mistral
date: 
scraped_at: 2026-09-04T13:23:09+00:00
---

Product

August 20, 2026

By Mistral

9 min read

Thinking

Summary

Mistral Agentic Search delivers more accurate search results while reducing turns, token use, and latency against FinanceBench and OfficeQA Pro benchmarks. Agentic Search is the retrieval layer that enables AI systems to navigate, read, and verify information inside even the most complex documents. Available through Mistral Search Toolkit and Libraries.

Mistral Agentic Search helps enterprises get better results from their AI systems by letting models search and navigate their organization’s most complex data and documents. Agentic Search introduces a multi-step retrieval loop for finding, inspecting, and verifying information across data sources, wherever it is stored. Agentic Search is available through

, built into

in both

and

, and gives you:

. Mistral’s portable and open tooling helps you unlock value from your data without crossing your isolation boundaries in the cloud or on-premises.

Your models can search and navigate your data beyond retrieved chunks–inside long, dense documents or across multiple sources.

Agentic Search builds on your existing search index using five tools:

,

,

,

, and

.

Agentic Search delivers to

on financial filings, from 26.7% to 86%, based on FinanceBench. On table-heavy, multi-doc questions of the OfficeQA Pro benchmark, we measure a

gain (6.3% to 51.9%).

Targeted navigation enables Agentic Search to reduce p90

. Fewer repeated searches reduce token consumption by up to one-third.

Competitive edge is built upon years of real-world operations–your data, your processes, and your domain expertise. Proprietary knowledge is both critical to your success and highly confidential, meaning it lives behind isolation boundaries, segmented deployments, and self-hosted platforms. It accumulates in financial filings, legal contracts, internal resources, and government records–long, dense documents that traditional search methods can’t navigate effectively.

Agents that learn and improve continuously can help you compound your competitive advantage, but these agents are often separated from confidential data and proprietary knowledge for security reasons. Getting real impact from AI means pairing frontier reasoning with retrieval tools that can safely reach your most sensitive material.

Traditional, one-shot RAG retrieves a fixed set of text chunks and asks a model to answer in a single pass. This works when the answer appears in one of the top results, but falters when the model must navigate a long report, follow references, compare multiple documents, or verify the underlying evidence.

The limitation is more pronounced on dense, complex data and documents. The information needed to answer a question may be spread across documents or buried in a particular table, footnote, or clause. One-shot RAG-based search fails to use the full power of frontier AI and to provide reliable answers for three reasons:

The model must answer from the chunks selected during the initial retrieval, even when they are incomplete or not relevant. It cannot decide that it needs a different document, another section, or more context before responding, which limits the impact of the model’s reasoning.

Critical data is often held in complex multi-modal documents. When asked, “

an index may find the correct document but cannot open it, navigate to the table, read the surrounding context, or verify the answer.

Many questions need more than one retrieval pass to get the correct answer. The model may need to refine its search, inspect a promising document, follow a reference, compare multiple sources, keep track of what it has seen, and try a new route when the first results are insufficient. One-shot RAG provides no way to take these next steps.

Without Agentic Search (one-shot retrieval)

Using specifically only the reported values for all individual calendar months in 1953, what is the total sum of these values of expenditures for U.S. national defense and associated activities (in millions of nominal dollars)?

Trajectory

→ 10 hits: a scatter of monthly bulletins (Table 3), each framed fiscal-year, covering only part of 1953.

I found January–June 1953 data. But I need July–December 1953 monthly values to compute an answer.

With Agentic Search

Using specifically only the reported values for all individual calendar months in 1953, what is the total sum of these values of expenditures for U.S. national defense and associated activities (in millions of nominal dollars)?

Trajectory

→ per-month bulletins (partial year)

→ surfaces

p.15 (Table 3, all 12 months of 1953)

→ pulls the complete Table 3

Monthly Values for 1953

Table 3, in $millions

Sum = 44,463.

provides open modules for ingesting, embedding, and indexing critical and complex data in the cloud or on-premises. Agentic Search builds on this index by giving the model five tools that resemble familiar file-system operations:

finds relevant documents across the corpus using the existing index.

opens a specific document.

moves to a page, section, or region within it.

retrieves the content at that location.

finds a pattern within an open document.

Rather than answering only from the initial top-

results, the model can inspect what it finds, refine its search, open relevant documents, navigate to specific sections, and read the source material before answering. The index identifies likely sources; Agentic Search determines what to inspect within and across them.

These tools do not require fine-tuning or model-specific training. As models get better at reasoning and tool use, retrievals get better without infrastructure changes. This is a key property: retrieval quality scales with model capability instead of being capped by your chunking strategy.

Filings, contracts, manuals, technical specifications, and reports where the answer may appear on a particular page or in a specific table, clause, figure, or footnote.

Research that requires the model to find, compare, or reconcile evidence from several documents before reaching an answer.

Financial figures, legal clauses, regulatory references, and operational data, where the response can be referenced in a stable and specific document location.

Financial statements, government records, and scanned PDFs where meaning depends on rows, columns, page position, or surrounding context–not narrative text alone.

Short, clean documents where the answer is likely to appear in one of the first retrieved chunks.

Keyword or semantic lookups that need to return relevant passages without reasoning over or navigating through them.

Use cases where the likely source and location of the answer are known in advance and additional retrieval steps are unlikely to improve the result.

One-shot RAG is often sufficient for these searches. Add Agentic Search when questions require the model to move beyond the initial results and investigate the source material. A well-configured index remains the right foundation in both cases.

We benchmarked Agentic Search on two industry-standard evaluations, using the out-of-the-box Mistral Search Toolkit stack: default chunking, default ranking, no tuning. These results are floors, not ceilings,

meaning you can further improve result quality with use-case-specific tuning.

With these benchmarks, we tested two models using the Mistral Search Toolkit:

(MM 3.5) and

(GLM-5.2), showcasing performance of a smaller model (MM 3.5) and a larger model (GLM-5.2).

Benchmark results are consistent: the agentic loop delivers substantive quality improvements and navigation tools increase accuracy while reducing wasted tokens, turns, and latency. We observe the same performance patterns across first- and third-party models, which indicates that Agentic Search is model-agnostic, and that search quality should improve with new models.

FinanceBench (Islam et al., 2023) tests financial question-answering over 368 SEC filings (10-K / 10-Q / 8-K), averaging ~147 pages each, ~53,900 pages total: long, table-heavy financial documents. Answers scored by an LLM judge calibrated against human labels.

Mistral Medium 3.5

GLM 5.2

We found:

Moving from one-shot RAG to a search-only loop lifts accuracy by

for MM 3.5 and

for GLM-5.2–a ~3x improvement for both models. Because models can search iteratively, they can recover from weak first results, refine queries, and use the index as an active tool.

Adding open, navigate, read, and grep lifts accuracy again (

for MM 3.5,

for GLM-5.2). This means a targeted drill-in search beats repeated broad search in complex documents.

The full loop with Navigation answers more questions correctly while using fewer tokens than the search-only loop (MM 3.5:

, GLM-5.2:

). The retrieval tools are not additional overhead–they replace wasted search retries with precise navigation.

Across FinanceBench, adding navigation retrieval tools improves latency: p90 drops

and mean latency drops

. In general, we see the search-only loops conduct repeated broad searches, while navigation helps the model identify evidence more quickly.

OfficeQA Pro is a verifiable numeric benchmark over historical U.S. Treasury Bulletins: scanned, table-heavy government-finance PDFs across a 696-document, ~89,000-page corpus. We report the first pass for the 133-question "pro" subset.

Mistral Medium 3.5

GLM 5.2

We found:

OfficeQA Pro has numeric answers, scanned PDFs, and deep table lookups. Even here, the full agentic loop lifts accuracy materially from one-shot RAG, reaching

for GLM-5.2 (

) and increasing

for MM 3.5.

Using the full loop (Agentic loop + Navigation) improves accuracy by

(

MM 3.5;

GLM-5.2), while reducing token consumption. Turns declined by

(MM 3.5,

GLM-5.2).

OfficeQA Pro is built around numeric answers in scanned, table-heavy documents. One-shot RAG barely gets started, while the agentic loop allows the model to search iteratively, inspect evidence, and deliver substantial accuracy improvements.

Per

, GLM-5.2 scores 41.4% on OfficeQA Pro with the Claude Code harness, compared with 51.9% on the Mistral harness–+10.5pp on the same underlying model.

Learn more about Agentic Search in the

. You can get started across cloud and on-premises deployments using either:

. Integrate Agentic Search into your own agents, workflows, and customer deployments.

. Use Agentic Search out-of-the-box in Studio and Vibe, without building the retrieval system yourself.

The fastest way to test Search Toolkit is with the

. It creates a local index for your own corpus using a default configuration, so you can try Agentic Search without needing to be a search expert. When you’re ready to configure your use case, you can:

. Select parsers, chunking strategies, embedding models, and extractors for your data and file types.

. Manage Vespa schemas, indexing behavior, and relevance profiles.

. Add query rewriting, reranking, or hybrid retrieval to the search pipeline.

0%
