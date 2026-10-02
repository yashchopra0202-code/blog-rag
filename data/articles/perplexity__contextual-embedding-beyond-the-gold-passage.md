---
url: https://www.perplexity.ai/hub/blog/contextual-embedding-beyond-the-gold-passage
title: Contextual embedding beyond the gold passage
site: perplexity
date: 2026-09-30
scraped_at: 2026-10-02T10:11:11+00:00
---

A new training method, model, and benchmark for retrieving answers and their supporting context.

Contents

Contextual embeddings capture the meaning of each passage or chunk in the context of the whole document. Their training and evaluation typically assume a single relevant chunk per query, known as the “gold passage.” However, a gold passage is often not enough in practice. It may contain the answer but lack the supporting context needed to understand or verify it, leaving it ambiguous in isolation.

We’re introducing

, our new contextual embedding model. The model is trained with a novel approach that uses Perplexity’s

as a teacher. We aggregate its token-level predictions into chunk-level relevance scores, teaching the embedding model to retrieve both answer chunks and supporting context rather than a single gold chunk. The model produces one embedding per chunk with no additional inference cost and supports 1024-dimensional and int8 embeddings.

It achieves state-of-the-art results on

, a new benchmark for context-aware retrieval created and privately held by

, and on

, a widely used public benchmark. Our model was developed independently of context-bench and evaluated as a blind submission.

Context-bench consists of 2,099 queries over 38,894 long documents in 21 domains and evaluates three capabilities of contextual embeddings: document disambiguation among near-duplicate documents, retrieval of gold chunks whose meaning depends on distant context, and recall of the supporting evidence required to verify an answer.

A preview of the model is publicly available on

. The benchmark is held privately by turbopuffer to reduce the risk of training contamination and preserve its value for measuring progress. To request an evaluation, please contact turbopuffer at contextbench@turbopuffer.com.

Retrieval systems typically divide long documents into smaller chunks that can be indexed and searched independently. Chunking is convenient in practice, but it removes the context in which each chunk originally appeared, creating a trade-off between the granularity of information compression and the context used during encoding. A chunk may refer to an entity introduced earlier, inherit its meaning from a section heading, or rely on definitions located elsewhere in the document. Once extracted, it may no longer contain enough information to be matched reliably to a query. Encoding the entire document as a single vector does not resolve this, since one pooled representation cannot faithfully capture every facet of a long document.

Contextual embedding models address this limitation by representing each chunk in the context of its surrounding content, most commonly through

: the document is encoded in a single pass and chunk representations are pooled afterwards, so that every chunk vector is computed with the whole document in view. Prior work, such as

and our own

, has shown that contextualized chunk representations substantially improve retrieval over independently encoded chunks, particularly on long documents.

Training contextual embedding models requires supervision that identifies which parts of a document are relevant to a given query. A common approach is gold-chunk annotations: for each query, an annotator, typically a large language model (LLM), identifies the chunk of the document that answers it.

Training usually combines two contrastive losses: a

that contrasts the gold chunk with chunks from other documents, and a

that contrasts it with the other chunks in the same document.

This approach has a few limitations:

We address the limitations of gold-chunk supervision by distilling relevance judgments from a

. This model serves as a teacher: it reads the query and document jointly and assigns each document token a relevance score. Its predictions offer several advantages for training contextual embeddings:

We train our model with a weighted sum of a

and a

over batches of query-document pairs. For each query, the paired document serves as the positive, while the remaining documents in the same batch serve as negatives.

For each batch, we randomly select a chunking strategy, split the documents accordingly, and insert separator tokens between chunks. We then process each document in a single forward pass and mean-pool the token representations within each chunk to obtain contextual chunk embeddings. Queries are encoded separately, with mean pooling over their token representations. Finally, we compute the cosine similarity between every query embedding and every chunk embedding in the batch.

While our embedding model only produces chunk-level similarities, we can naturally derive document-level similarities from them. We consider a document d to be as relevant to a query q as its most relevant chunk. This scoring rule is inspired by the MaxSim operation of

, applied here to chunks instead of tokens.

Specifically, given a query q with embedding

and a document d as an ordered list of chunks c with embeddings

, we define the document-level similarity as:

Given these document-level similarities, we can formulate a document-level

over in-batch negatives.

For a query q, let d⁺ denote its relevant document and 𝒟 the documents in the batch. The contrastive loss is as follows, omitting temperatures for readability:

The contrastive loss teaches the model which document is relevant to a query. The distillation loss teaches it where relevance lies within that document, which is essential for a contextual model.

During training, we pass each positive query–document pair to our context compression model, which assigns a relevance score to every token in the document. As with document-level scoring, we derive each chunk’s relevance from its most relevant contents. To reduce sensitivity to outlier tokens, including those at chunk boundaries, we define chunk-level relevance as the mean of the top n token scores within the chunk.

For each query, we apply a temperature-scaled softmax to the teacher’s chunk-level relevance scores within the positive document to obtain a target distribution. Chunks in the other documents in the batch receive zero target probability. We train the embedding model to match this target by minimizing the forward KL divergence between the target and its predicted distribution over all chunks in the batch:

Here, the superscripts T and S indicate the teacher and student, and rⱼ is the teacher’s relevance score for chunk cⱼ in the positive document d⁺. The teacher’s target distribution assigns zero probability to chunks in all other documents in the batch.

Unlike a single gold-chunk label, this target captures degrees of relevance. Supporting chunks receive weight according to the teacher’s scores rather than being treated as negatives, teaching the model to retrieve supporting context as well as the answer.

Our combined training objective is a weighted sum of the document-level contrastive loss and the chunk-level distillation loss. We average this weighted loss over the batch of query–document pairs.

Figure 2 illustrates our training approach. The context compressor serves as a teacher only during training. At inference time, the embedding model produces one contextual embedding per chunk, with no additional compression or reranking stage. The approach improves how contextual embeddings are learned without increasing index storage or adding teacher-model latency at retrieval time.

The training data consists of roughly 430 public and in-house query–document datasets covering over 50 languages.

We construct in-house pair datasets from PII-filtered production data and by synthesizing relevant queries over long documents. For each forward pass, we select one dataset and sample an entire batch from it to increase the difficulty of in-batch negatives and avoid shortcut learning. None of our training datasets carry chunk-level annotations: all within-document supervision comes from the compression model, and no ConTEB data is used for training. Moreover, no context-bench data was available during the model development.

The model starts from an in-house, 9B-parameter ColBERT retrieval model and produces 2048-dimensional embeddings through a linear projection layer. We mark chunk boundaries with a learned

token and form each chunk embedding by averaging its token embeddings. Queries are encoded by the same model, with their token embeddings averaged into a single vector.

We use

to support both 1024- and 2048-dimensional embeddings, and quantization-aware training to support

. During training, we gradually increase the learning rate, hold it constant, then reduce it.

The released model is a

that averages the weights of several checkpoints from the same training run.

Public contextual-retrieval benchmarks such as ConTEB share the assumption behind gold-chunk supervision: each query has a single relevant chunk and a model is rewarded only for ranking that chunk first. They also inherit its limitations.

First, ConTEB tests retrieval on tasks where a chunk is ambiguous without its surrounding context. On these tasks, contextual models outperformed models that encode each chunk independently. However, it does not ask whether a model also surfaces the other parts of the document that make the chunk understandable.

Second, it does not systematically test whether the right document can be found when near-identical documents in the same corpus differ only in the context that surrounds an otherwise identical sentence.

Both capabilities matter when a search agent or user must understand and verify an answer from a few retrieved sentences rather than an entire document. We therefore built context-bench, a controlled benchmark for retrieval over long documents, designed to distinguish the use of document context from general retrieval quality. It tests whether contextual embeddings use information from elsewhere in a document to support three capabilities:

Context-bench contains 2,099 queries and 38,894 documents. Sentence length chunks are used, resulting in 2,458,072 total chunks. The queries cover 21 domains including corporate filings, clinical research, travel, entertainment, education, government, legal contracts, and software documentation.

Each query is designed to test one of twelve contextual capabilities. The primary target documents are intentionally long: 1,061 of the 1,197 distinct primary target documents have at least 200 sentences, with a median length of roughly 6,100 tokens. Every query has exactly one correct answer in the corpus. Where the same fact is stated more than once in a gold document, for example in a summary sentence and a table row, any of those sentences are accepted as answers.

An answer route is one valid combination of an answer chunk and the supporting evidence needed to interpret or verify it. Across the 2,099 queries, the primary target-document answer route has one evidence group for 964 queries, two for 735, three or more for 332, and none for 68. Alternative valid answer routes can require different evidence groups.

Queries

2,099

Documents

38,894

Sentence chunks

2,458,072

Median primary target document length

6,100 tokens

Domains

21

Evidence groups per query (primary target-document answer route)

1: 964; 2: 735; 3+: 332; none: 68

How much did Northlake spend on share repurchases?

The company repurchased $12.8 billion of shares.

The introduction identifies Northlake as “the company.” A similar Southlake report is not relevant.

Which cartridge fits the M40 revision B?

Install the KC-42 cartridge.

The applicability section says these instructions cover revision B, not revision C.

What withdrawal rate did the 15 mg group have?

Zeta had a withdrawal rate of 12.7%.

The report defines Zeta as the 15 mg group. Without that definition, the chunk does not identify the requested group.

What is the Max model’s battery capacity?

Typical capacity: 4,250 | 4,700 | 5,150.

The table header establishes Mini | Base | Max, measured in mAh. The answer is therefore 5,150 mAh.

How long is battery coverage for commercial use?

Battery coverage lasts 18 months.

A section introduction restricts this coverage to commercial installations; household installations have a different warranty.

When did Mara become deputy mayor?

She took office in 2021.

The preceding narrative establishes that “she” refers to Mara, not Elin, who is also discussed.

Which song opened the encore?

14. Lantern Road.

A note elsewhere says songs 14–16 constituted the encore. Track 14 is therefore its opening song.

Which lens was used for the film’s cinematography?

A 35 mm prime was used throughout.

This passage belongs to “Principal Photography,” not the separate section about publicity photographs.

What reopening date did the mayor promise?

We will reopen on June 12.

The transcript identifies the mayor as the speaker. The same words from a contractor would not establish the mayor’s promise.

What notice period applied after the May amendment?

The notice period is now 45 days.

The amendment history establishes that this change took effect in May, replacing the earlier 30-day rule.

Why did the west pump stop?

That fault caused the shutdown.

The investigation identifies “that fault” as a seized bearing in the west pump, and distinguishes it from an unrelated inlet obstruction.

Figurative:

What does “the winter room” symbolize in the poem?

Cross-language:

Which component does the French instruction tell the technician to remove?

Figurative:

It represents exile, rather than a physical room.

Cross-language:

Retirez le capot. (Remove the cover.)

Figurative:

The commentary identifies “it” as the poem’s recurring “winter room” image.

Cross-language:

The guide’s glossary specifies that “capot” means the protective motor hood, not the shipping cover.

The queries, documents and capabilities being tested are inspired by conversations with turbopuffer’s customers.

To give one example, consider the search needs of a property management firm. These firms have hundreds, sometimes thousands of lease agreements that differ only in the tenants names, dates, and a few other key details. A common query for that dataset might be “when does 5 park avenue’s lease end and what is the current rent?”. Lease agreements can also be lengthy and the critical disambiguating components that would confirm you’ve retrieved the right document (like the date, address, tenant name, etc.) can often be very far away from the key answer sentence containing the monthly lease payment amount. In practice, identical sentences like “Monthly rent is $X,XXX.” can appear across many documents in the corpus.

A good contextual embedding model should use context from across the document to identify the correct document and retrieve both the answer and its supporting sentences. This lets a user or search agent quickly verify the answer and confirm that it comes from the right document.

For each query, we label “answer” and “evidence” sentences in the target document. A model passes our “reader sufficiency” test if it retrieves an answer sentence together with at least one sentence from each evidence group. Together, these sentences provide enough context for a reader to verify the answer with supporting evidence.

When contextual embedding models do this well, they can dramatically reduce the number of tokens search agents need to review as well as make it much easier for a person to quickly confirm that they have located the correct answer to their original query without having to read the entire document.

Every evidence group must be recovered, but any one of a group’s alternatives is enough to recover it. It’s common to see the same fact stated in several places across these lengthy documents. Retrieving just one sentence from each evidence group meets the reader sufficiency criteria and as such would be accepted as perfect evidence recall.

Every document is chunked into sentences, and the same boundaries are used for all models. Two conditions are tested for non-contextual embedding models: one where each sentence is embedded independently and another where the entire document is embedded as a single chunk.

We use the sentence-level condition to measure answer recall and evidence recall. It tests whether a non-contextual model can identify the correct answer and supporting evidence when each sentence is embedded without access to the surrounding document. This is intentionally challenging. In many queries, the answer sentence alone lacks the details needed to distinguish it from similar sentences elsewhere in the corpus.

We use the document-level condition as a document recall baseline. It tests whether fine-grained sentence embeddings provide enough retrieval benefit to justify their additional storage cost relative to storing one vector per document. A sentence-level index creates substantially more vectors than a document-level index, so it should outperform the one-vector-per-document baseline to warrant that cost.

All evaluations use exhaustive rankings against all 2,458,072 chunks. Differences between models therefore reflect the representations, not index configuration. We focus on three key metrics:

is defined as:

where

is the highest-ranked document in

is defined as:

where

is the top

chunks over the whole corpus and

is the set of accepted answer chunks.

is measured within

as follows: Rank the sentences of

by similarity, remove the highest-ranked answer sentence, and let

be the top

that remain. For evidence groups

, group

is recovered if some alternative

satisfies

, and

asks whether contextualization lets the right document beat siblings and distractors that share its vocabulary.

asks whether the answer sentence itself ranks among the top chunks.

asks how much of the supporting context is recovered among the correct document’s top K chunks, after excluding the highest-ranked answer chunk. Removing the answer keeps evidence recall from double-counting what

already measures, and leaves all

slots for supporting context. Requiring the gold document to be in the top 10 retrieved documents means no model receives evidence credit for a document it would not have surfaced. We also report

, the fraction of queries with every group recovered.

Together, these metrics decompose the challenges contextual-embedding models face: find the right document, find the right answer, and recover the minimal context that shows why the answer is correct.

Figure 3 illustrates the metrics with the property management example.

We evaluate our model against contextual and non-contextual embedding models on four fronts.

Our contextual baselines are

and

. Our non-contextual baselines are

and NVIDIA’s

, which encode chunks independently. The baseline set varies by experiment, as indicated in each figure.

We start with context-bench, which directly tests the capabilities that motivate this work, and then report results on ConTEB, the standard public benchmark for contextual embeddings. To check that these gains do not come at the expense of general retrieval quality, we also evaluate domain-specific document and chunk retrieval benchmarks that we built from public datasets. Finally, we examine two practical properties for deployment: retrieval quality versus storage costs per vector, and sensitivity to the chunk size used at indexing time. All evaluations encode documents of up to 32,768 tokens in a single pass.

As shown in

, our preview leads on Answer@K and Evidence Recall@K at every reported cutoff, as well as All-Evidence@10. At K = 10, it achieves 45.5% answer recall, 40.6% evidence recall, and 31.1% all-evidence recall. It also leads on Document@1 and Document@10, reaching 15.2% and 61.6%, respectively. At K = 10, our preview exceeds voyage-context-4 by 14.4 percentage points in answer recall and 5.0 points in evidence recall.

Our preview model achieves the highest average nDCG@10 among the models shown on ConTEB in Figure 4. It does not lead every task: pplx-context-v1-4B scores higher on NarrativeQA, while Nemotron-3-8B scores highest on COVID-QA. As the main authors also pointed out in the ConTEB paper, COVID-QA includes mostly query-chunk pairings that are very extractive and can be satisfied with simple surface lexical matching on technical medical terms. As a result, context understanding is less useful for this task and non-contextual models typically outperform contextual ones.

Beyond benchmarks designed for contextual embeddings, we assess the domain-specific performance of our model.

Our query-to-chunk (Q2C) suite uses MTEB tasks such as LegalBench and FinanceBench alongside additional retrieval tasks we curated from public datasets. Within each relevant document, a chunk is labeled relevant if it contains the exact answer span when the task provides one, and otherwise by an LLM judging its relevance to the query. The query-to-document (Q2D) suite uses the same tasks and scores whether the relevant document is retrieved.

Our model achieves the highest average score on chunk retrieval in Figure 5 and leads in the legal, technical and health domains. It does not lead in every domain: voyage-context-4 scores higher in finance and multilingual retrieval, and Nemotron-3-8B scores highest in conversation retrieval. On document retrieval in Figure 6, our model scores slightly below voyage-context-4 on average, while leading in the technical domain. The pplx-context-v1-4B baseline scores lower on average in both suites, which is consistent with it having been trained only on the ConTEB training set, showing that supervision tied to one benchmark's gold chunks transfers poorly to other domains.

A contextual embedding model produces one vector per chunk, so an index built with our model contains exactly as many vectors as a conventional chunk-level index with the same chunking strategy. Contextualization changes what each vector encodes, not how many vectors are stored. The storage footprint is therefore governed by the size of each vector. The model offers two ways to reduce it: truncating the embedding from 2048 to 1024 dimensions and quantizing it to int8.

Figure 7 shows a favorable tradeoff between retrieval quality and vector storage. At 1024 dimensions, our int8 embeddings use 1 KB per vector while slightly exceeding the chunk-retrieval score of voyage-context-4 at 2048 dimensions in float32, which uses 8 KB per vector. Increasing our embedding size to 2048 dimensions raises retrieval quality further at 2 KB per vector. These storage figures refer to the vectors alone, not the rest of the index.

Figure 8 shows only a modest change in retrieval quality as chunk size increases from 64 to 512 tokens: the average score falls from 81.0% to 79.9%, a decrease of 1.1 percentage points. This suggests that the model remains effective across the tested chunk sizes, giving indexing pipelines flexibility in how documents are split.

turbopuffer keeps the full corpus, queries and labels of context-bench private and reports results for submitted models. A public benchmark of this kind invites direct training on its queries and documents, which would gradually saturate it and erode its value for tracking progress over time. If you would like your model to be evaluated on the benchmark, please contact turbopuffer at contextbench@turbopuffer.com.

A preview of our model is available on

, and all results in this post are reported for this preview. We are working on making the model available through the Perplexity API, and on further improving retrieval over long documents together with turbopuffer.
