---
url: https://www.perplexity.ai/hub/blog/q2d-web
title: Q2D-Web: Evaluating First-Stage Retrievers at Scale
site: perplexity
date: 2026-09-09
scraped_at: 2026-09-09T17:06:06+00:00
---

A benchmark and leaderboard with 70 thousand agent queries, 190 million web documents, and three sets of relevance judgements.

Contents

Today, we are introducing

, a private benchmark and

for evaluating retrieval in agentic RAG systems. Q2D-Web extends our original

to a large-scale corpus, a larger query set, and deeper judgment annotations.

Q2D-Web is built to evaluate embedding models on large-scale web search. It consists of 190 million web documents and 69,721 agent-reformulated queries in ten languages, sampled over nine months of PII-free production search traffic.

At this scale, relevance signal at the query-document level is inevitably sparse. Rather than treat one source as ground truth, we provide three relevance-judgment sets, derived from agent citations, production web rankings, and additional LLM judgments for previously unjudged pairs. Multiple sources limit bias from any single labeling pipeline, while deeper annotation reduces false negatives.

Our leaderboard

reports results for publicly released retrieval models, evaluated directly against the benchmark using a consistent indexing, retrieval, and scoring pipeline. An evaluation can be submitted via our

For each query, a production-scale retrieval system searches a corpus of billions of web pages and returns thousands of candidate documents. These candidates determine which sources downstream systems can see, directly shaping the evidence available to the agent.

Realistic evaluation of this first stage therefore requires benchmarks that scale along three dimensions: the number of documents in the corpus, the number of judged queries, and the number of relevance judgments per query.

Larger corpora can make a benchmark more discriminative by introducing hard negatives—documents that are semantically similar to a query but do not provide the information requested. Retrievers must distinguish these plausible matches from relevant documents. Shrinking the corpus while retaining known relevant documents can remove these distractors and inflate recall, as our subsampling experiments below show.

More judged queries make performance estimates more reliable. With a small query set, benchmark results depend heavily on which queries were sampled, making it harder to estimate each model’s performance precisely and confidently distinguish between models.

Deeper judgments reduce false negatives in evaluation. With sparse labels, a retriever can surface relevant documents that are unjudged and are therefore incorrectly counted as non-relevant. This makes the evaluation less reliable. MS MARCO is the main large-scale open dataset in information retrieval and shaped the development of neural retrieval models.

Existing benchmarks tend to scale in only one or two of these dimensions: web-scale collections often have relatively few judged queries, while benchmarks with many queries generally use much smaller corpora and sparse labels. Moreover, most benchmarks use human-written queries, whereas agentic RAG systems search with agent-reformulated queries that may differ in wording, structure, and specificity.

Q2D-Web scales across all three dimensions. It contains 190 million web documents, 69,721 agent-reformulated queries, and an average of 99.6 positive relevance judgments per query in its combined judgment set. The closest public comparison is MS MARCO Web Search, the web-scale version of MS MARCO. It has 100.9 million documents, 9,374 test queries, and one click-derived positive label per query.

Q2D-Web is built upon 23,000 PII-free production searches in ten languages and dozens of domains collected over a nine-month period.

A search consists of all web search tool calls an agent performs in response to a user message. Each tool call contains one or more queries. Each query is reformulated from the user request, prior conversation, and, where applicable, documents retrieved earlier in the same search. Each production search contains one primary query, which restates the user's information need, and zero or more support queries, which explore alternative phrasings, background information, or related entities. Although they address the same broader request, they can require different documents, so Q2D-Web evaluates each query independently with its own relevance judgments.

We apply strict privacy filtering for all included queries. Queries must come from users who allowed their data to be used, and PII detection using

excludes queries containing personal information. We also remove exact duplicates, very short queries, and queries containing search operators like

or quoted phrases.

The benchmark covers ten languages. English accounts for 65.8% of queries, followed by Spanish, Russian, German, French, Portuguese, Italian, Korean, Japanese, and Chinese. The query distribution also spans a broad mix of domains, including consumer goods, programming, law, health, business, science, education, technology, finance, travel, entertainment, politics, local information, and news.

For every query, we retrieve the top 5,000 documents with a production retrieval system and take the union of these result sets. We then deduplicate the corpus using MinHash–LSH, clustering documents whose token 5-gram sets have Jaccard similarity of at least 0.975.

The collection is intentionally not a random web sample. Each document was considered a plausible result for at least one benchmark query. This creates a dense set of difficult distractors: pages that match a query’s topic or language but may miss a required date, entity, version, quantity, or aspect.

Relevance labels are incomplete by nature at large scale. Labeling every possible query-document pair is infeasible, and each source of judgments carries a different bias.

Q2D-Web uses three relevance sets rather than treating one source as ground truth, to increase the annotation depth without suffering from a single bias.

labels a document as relevant when an agent cited it in a response. This is the closest signal to downstream use: the agent selected the document as evidence for a claim. But citation is high precision and low recall by construction. Once an agent has sufficient support, it has little reason to cite every other relevant page.

consists of up to 50 documents per query (43.1 on average), identified by an internal retrieval stack using BM25 and dense retrieval in the first stage, followed by cross-encoder reranking. This captures documents that are useful but not cited.

takes the union of Citation and Web Ranking, then adds LLM judgments for previously unjudged candidates, with the goal of reducing the number of false negatives. We pool results from

, and seven dense retrievers released before January 1, 2025, merge their rankings using

(RRF), select the top 500 unjudged documents, and apply a strict binary relevance judge using

The three sets let us ask whether model performances depend on how relevance is defined. They also reduce reliance on a single labeling stack, which could otherwise favor retrievers similar to the system used to generate labels.

Full-corpus evaluation is expensive and slow. A single evaluation on Q2D-Web with pplx-embed-v1-4b requires 4,608 H200 GPU-hours, while even a small model like EmbeddingGemma-300M requires nearly 200 H200 GPU-hours.

To keep evaluation practical, we build a subsampled version of the corpus.

We ran an extensive ablation across sampling strategies to build a smaller subcorpus that reflects full-corpus behavior. Every strategy retains all positively judged documents and varies only in how unjudged distractors are selected. The distractors that matter are the ones a retriever is likely to rank above a relevant document, because those change a model's score and its position in the ranking.

We compared uniform random sampling, pooling to a fixed depth across the construction retrievers, and per-query RRF over different depths. RRF-based sampling uses only

It preserves the full-corpus model ranking, while staying close to absolute scores, inflating mean Recall@1000 by only 4.5 points versus 11.1 points for random sampling at the same size.

This reduces evaluation costs to about a third of the full-corpus cost. Using the RRF-based subcorpus, pplx-embed-v1-4b requires roughly 1,500 H200 GPU-hours and EmbeddingGemma-300M requires under 70.

Every submission is evaluated first on the sampled subcorpus version. Submissions are split into two groups by total parameter count: up to 1B and above 1B. A model that reaches the top ten of its group on the sampled subcorpus is then evaluated on the full corpus. Models ranked outside the top 10 in their group will be published only on the sampled subcorpus leaderboard.

Across the evaluated models, Q2D-Web provides a consistent view of retrieval performance at web scale across its 3 different relevance sets. The

makes these complementary views available side by side, allowing users to inspect how models perform under narrower citation-based labels and broader relevance judgments.

We focus on Recall@1000 as our primary metric because a first-stage retriever only needs to place relevant documents in the candidate pool, while subsequent reranking determines their final order.

BM25-tantivy

43.92

42.50

44.77

5.74

11.45

30.30

EmbeddingGemma-300M

58.17

58.93

65.45

9.20

17.30

43.56

mDenseOn

51.78

52.56

59.31

7.63

15.06

40.20

Nemotron-3-Embed-1B

54.40

54.37

61.68

7.54

14.83

40.21

Nemotron-3-Embed-8B

61.73

68.58

10.16

18.69

47.44

pplx-embed-v1-0.6b

58.35

62.15

67.02

9.37

19.76

44.36

pplx-embed-v1-4b

61.22

10.33

21.29

45.84

Qwen3-Embedding-0.6B

50.10

51.82

57.89

6.58

14.11

37.38

Qwen3-Embedding-4B

54.95

55.60

62.01

7.67

14.97

40.21

Qwen3-Embedding-8B

57.38

58.34

64.53

8.30

16.27

42.69

voyage-4-nano

49.38

50.14

56.67

5.41

11.77

31.63

mLateOn

52.85

53.12

60.98

8.44

15.51

43.11

pplx-embed-v1-late-0.6b

56.56

58.14

63.40

9.13

17.25

43.39

No model leads on all three judgment sets. On Recall@1000, pplx-embed-v1-4b is highest on Web Ranking (65.73) and Combined (69.11), and Nemotron-3-Embed-8B on Citation (61.68). On Combined Recall@100 and nDCG@10 the order changes, with Nemotron-3-Embed-8B (30.03 and 47.44) above pplx-embed-v1-4b (29.82 and 45.84).

Within a family, larger models score higher on Combined Recall@1000. Qwen3-Embedding rises from 57.89 (0.6B) to 64.53 (8B), Nemotron-3-Embed from 61.68 (1B) to 68.58 (8B), and pplx-embed-v1 from 67.02 (0.6B) to 69.11 (4B).

Perplexity models are evaluated using the same pipeline as all other submitted models. However, because Q2D-Web is derived from Perplexity production traffic, these models may benefit from an in-distribution advantage. Even though the benchmark’s evaluation queries and corpus were excluded from model training, results should be interpreted with this potential advantage in mind.

To request an evaluation, submit a publicly available Hugging Face model through our

We follow the model card in the submitted repository for model-specific inference settings, including recommended query and document instructions or prefixes, pooling, normalization, and similarity function. All queries and documents are truncated to 512 tokens with the model's own tokenizer, including instructions, prefixes, and special tokens, so a longer supported context confers no advantage. Please ensure the model card provides complete, unambiguous instructions for reproducing the intended retrieval setup.

Eligible models must load through standard

or

APIs. Models that do not run with

require a manual review of the custom code and of the submitter before evaluation, which takes considerably longer. Private or gated repositories are not eligible.

Read our

to learn more about the methodology and findings.
