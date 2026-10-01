---
url: https://cohere.com/blog/embed-5
title: Introducing Embed 5—A New Family of Frontier Embedding Models
site: cohere
date: 
scraped_at: 2026-10-01T10:36:14+00:00
---

Key takeaways

Today, we're releasing Embed 5, a new family of embeddings models at the frontier of high-quality enterprise retrieval.

Embed 5 delivers stronger retrieval across complex enterprise data while giving teams more control over latency, cost, and deployment.

is optimized for maximum quality across multimodal, multilingual, financial, code, and parsed-document retrieval.

brings highly competitive performance to latency- and cost-sensitive workloads. Both tiers share a single embedding space, so teams can index with Pro and query with either model without rebuilding the index.

Embed 5 establishes the retrieval foundation for search, RAG, and agentic workflows, surfacing more relevant context while filtering out noise before it reaches expensive generative models. Use Embed to improve answer quality and user experience while helping keep downstream inference costs under control.

Embed 5 is generally available today on the

, and

. Pricing is $0.12 per million tokens for Pro and $0.08 per million tokens for Fast.

Embed 5 Pro delivers our strongest retrieval performance to date. It achieves the highest average score of any model we tested across ViDoRe V3, financial documents, parsed PDFs, image retrieval, and across key business languages.

Embed 5 is also the first model family evaluated with

, our latest retrieval methodology. Instead of scoring only against a limited set of fixed labels, it evaluates retrieved documents against query-specific relevance criteria, capturing relevant results and giving a fuller view of performance on your own corpus

Embed 5 excels with visually rich documents where meaning lives in tables, charts, diagrams, and layout - not just text. On

, which features documents sampled across key enterprise domains including financial filings, technical manuals, regulatory material, government reports, textbooks, and lectures, Embed 5 Pro averages 85.8 - an impressive 8.8 gain from Embed 4

That puts it ahead of Voyage 4 Large (83.7), Gemini Embedding 2 (83.2), and OpenAI text-embedding-3-large (75.5). Pro leads five of the eight domains outright and ties Voyage 4 Large on energy, with its largest gains over Embed 4 on HR (+11.4) and industrial (+10.3). Embed 5 Fast averages 84.5, ahead of both Gemini Embedding 2 and Voyage 4 Large. See the full results

Embed 5 Pro establishes itself as the leading embeddings model for financial document retrieval.

Pro ranks first on three leading public financial benchmarks, with Fast second on each despite being considerably smaller than its peers:

(80.1 Pro, 80.0 Fast),

(90.0, 88.8), and ViDoRe V3 Finance (85.0, 83.9).

Across these, Pro averages 3.3 points higher than the next non-Cohere competitor, Gemini Embedding 2. Compared with OpenAI text-embedding-3-large, the lead grows to 21.4 points on FinanceBench.

Most enterprise search pipelines still convert PDFs to text before embedding them, but that process can strip away structure. Tables lose row and column relationships, multi-column layouts can scramble reading order, repeated headers add noise, and charts often disappear entirely. That makes parsed-document retrieval a harder test than clean-text benchmarks suggest.

Our parsed-document suite spans service documentation, corporate reports, SEC filings, product manuals, and privacy policies. Embed 5 Pro achieves the highest average across the suite at 84.8, ahead of Voyage 4 Large at 83.6, Embed 5 Fast at 83.4, Gemini Embedding 2 at 80.8, and Embed 4 at 78.6. The figure below highlights a subset of familiar public benchmarks, with Embed 5 Pro especially strong on financial documents represented by FinanceBench and CoFiF.

Some documents are better represented visually. Scanned pages, slide decks, schematics, and charts contain information that text extraction may miss. Embed 5 can embed page images directly (page-image), or combine an image with its metadata into a single vector (fused text-image).

On fused text-image corpora, Embed 5 Pro averages 82.3 across five datasets, ahead of Embed 5 Fast at 81.2 and Gemini Embedding 2 at 61.3. Pro outperforms Gemini Embedding 2 on every dataset in the suite. Page image retrieval is also robust: Embed 5 Pro continues to lead on financial datasets, averaging 77.0 from five datasets, ahead of Embed 5 Fast (73.2), Embed 4 (71.1), Voyage Multimodal 3.5 (70.1), and Gemini Embedding 2 (56.7).

Embed 5 is trained on more than 100 languages, with particular focus on the languages most used by our global customer base.

Across German, French, Spanish, Italian, and Russian, Embed 5 Pro achieves the highest average of the models we tested: 77, compared with 76 for Voyage 4 Large, and 73 for Gemini Embedding 2. It improves on Embed 4 by around 7 points on average, with the largest gains in Russian (+9) and Italian (+7).

The table below covers ten further languages where Embed 5 has made important strides against Embed 4. Pro’s largest gains are in middle eastern and subcontinent languages, notably Farsi (+13), Telugu (+12), and Hindi (+12). For the full list of multilingual evaluation results,

Embed 5 Fast is a lighter weight model built for latency-sensitive, high-volume retrieval. It costs a third less than Pro while retaining the same 128K-token context, multimodal inputs, multilingual coverage, and multiple compressed output formats.

That matters most on the query path, where embedding latency is paid on every search - and multiplied in agentic workflows that may issue dozens of searches per task. Fast’s smaller footprint also lowers serving costs in private deployments and speeds large ingestion and re-indexing jobs.

For document throughput - a closer proxy for indexing efficiency - Fast is consistently more efficient, delivering an average of 2.4× higher throughput than Pro across context sizes.

Fast raises the bar for compact embedding models. On ViDoRe V3, it leads Voyage 4 Nano by almost seven points and Jina Embeddings v5 Text Small, Perplexity, and Microsoft’s Harrier 0.6B by ten or more. It outperforms Qwen3-VL-Embedding-2B, despite being roughly half the size, by about 20 points. As seen above, its average also exceeds Gemini Embedding 2 and Voyage 4 Large on ViDoRe V3 and on financial retrieval. On parsed PDFs it exceeds Gemini Embedding 2 (83.4 vs 80.8) and trails Voyage 4 Large (83.6).

Pro and Fast share a single embedding space, so vectors from either model can be compared directly. We tested every corpus/query pairing across 40 development datasets spanning text, image, fused, and parsed-document retrieval.

That shared space lets teams choose each tier independently: documents can be indexed with Pro for maximum quality, while queries use Fast for lower latency and cost—without rebuilding the index. The cross-model combinations remain close to the same-model baselines (averaging just 1.6% and 2.7% losses for Fast and Pro queries, respectively), with no dataset showing a major failure.

For many customers, we recommend the following deployment pattern:

It captures much of the quality gain of an all-Pro system while keeping Fast’s latency and cost during request

Cross-model retrieval. Mean nDCG@10 across 40 development datasets, normalized to Pro corpus + Pro query = 100.

At enterprise scale, the vector index can cost more to operate than the model that generates it. Embed 5 supports Matryoshka representation learning and lower-precision outputs, letting teams shrink vectors and finely control the tradeoff between quality, storage, and search cost. These savings can be substantial - a 2,048-dimensional float32 vector requires 8 KB; a 1,024-dimensional int8 vector uses 1 KB; and a 256-dimensional binary vector just 32 bytes—a 256x reduction. Across 100 million chunks, that cuts raw vector storage from roughly 819 GB to 3.2 GB.

Importantly, int8 retains near-full-precision retrieval quality in both Embed 5 Pro and Fast. For most deployments, we recommend 1,024-dimensional int8 vectors as the ideal performance-efficiency point. Binary offers the smallest footprint, with some accuracy tradeoff, and is well suited to fast first-pass retrieval before higher-precision reranking.

Deploy Embed 5 Pro and Embed 5 Fast through the Cohere API, Model Vault, Microsoft Foundry (

), and Amazon SageMaker (

), or use Embed 5 directly within

. For private deployments in your own VPC or on-premises, both models can be served with vLLM.

for large-scale ingestion.

Embed 5 fits into existing retrieval stacks, with integrations across frameworks and vector databases including LangChain, Haystack, Weaviate, Qdrant, Pinecone, Elasticsearch, MongoDB, Redis, Milvus, and OpenSearch.

Start by

, then use the code snippets below to quickly make your first query.

Join us on X on

to hear from our search and embeddings leadership about Embed 5, Parse 5, and what else we’ve been preparing behind the scenes.

Also,

, our managed search and retrieval platform, is now in private beta.

to try it on your own retrieval and agentic workloads.

Samarth Bhargav, Fabian Schmidt, Clifton Poth, Arthur Maciejewicz, Florian Schneider, David Rau, Dennis Zhao, Timothy Ang, Nils Reimers, Carlos Lassance.

RCP-nDCG@10 requires evaluating embedding models in a two-stage retrieval setup, using their similarity scores to reorder a fixed candidate set. Scores therefore reflect reranking quality rather than first-stage retrieval performance, which we thoroughly evaluate elsewhere against nDCG and Recall.

The annotations and code needed to evaluate Vidore V3 with RCP-nDCG are available

Both sides must use the same output dimension. Compatibility also holds with Matryoshka truncation and int8 quantization, so the same pattern works with compressed indexes.

Written By

Cohere Team

Tags

AI isn’t a shortcut.

It’s how business gets ahead.
