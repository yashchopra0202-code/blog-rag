---
url: https://huggingface.co/blog/train-multi-vector-encoder
title: https://huggingface.co/blog/train-multi-vector-encoder
site: huggingface
date: 2025-07-04
scraped_at: 2026-09-05T05:08:11+00:00
---

Finetuning multi-vector models involves several components: the model itself, datasets, loss functions, training arguments, evaluators, and the trainer class. I'll have a look at each of these components, accompanied by practical examples of how they can be used for finetuning strong multi-vector models.

Lastly, in the

section, I'll show you that my finetuned

model, trained in 14.5 hours on a single RTX 3090 alongside this blogpost, easily outperforms every general-purpose retrieval model I could find on my medical retrieval evaluation: dense, sparse, lexical, and multi-vector alike.

If you're interested in finetuning dense embedding models, sparse embedding models, or rerankers instead, then consider reading through my prior

, and

blogposts.

This blogpost is about

multi-vector models. If you want to learn how to

them, from loading and encoding to indexing in vector databases, see the companion

blogpost.

A dense embedding model compresses a whole text into a single vector, and similarity is one dot product between two such summaries. A multi-vector model (also called a late-interaction or ColBERT-style model) skips that compression. It keeps

and scores a query against a document with the MaxSim operator, where every query token finds its best-matching document token and the scores are summed. Token-level matching preserves exactly the fine-grained signals that a single vector has to average away, which usually means stronger retrieval, at the cost of a bigger index.

The companion

blogpost covers the architecture, encoding, scoring, and indexing in detail, so I'll keep this section short and get to the training.

Finetuning multi-vector models significantly improves their retrieval performance on your specific domain: the vocabulary, the query style, and the notion of relevance all differ between web search, legal discovery, code search, and scientific literature review. Because queries and documents are matched token by token, multi-vector models pick up fine-grained domain signals that single-vector models tend to average away, and they respond very well to even modest amounts of in-domain finetuning data.

Beyond that, most released retrieval models were configured for short passages. The classic ColBERT checkpoints truncate documents at 180 or 300 tokens, and many popular dense models at 256 or 512, because their MS MARCO-style training data rarely goes beyond that. If your documents are long, these models silently discard most of every document before scoring it. On my medical evaluation with passages averaging 941 tokens, I measured that this truncation costs up to 0.24 NDCG@10, considerably more than any difference between model architectures. When you train your own model, you configure the document length that

data needs.

LightOn ran into this same dynamic with code retrieval, where general

wasn't enough and they trained

. Your domain, whether that's medical, legal, financial, or your company's internal documents, is not getting an official model. This blogpost shows you how to build it yourself, in a matter of hours, on a single consumer GPU.

Training MultiVectorEncoder models involves the following components:

Let's take a closer look at each component.

Multi-vector training gives you a real choice of starting point, and it matters more than you might expect.

If you want to further finetune an existing multi-vector model, you don't have to worry about the architecture at all:

The checkpoint brings its own recipe along: its query and document marker tokens, its projection head, its scoring skiplist. For finetuning, you generally want to keep all of that and change only what your data demands. The first thing to check is the length configuration, since many released checkpoints cap documents at 180 to 512 tokens (see

), and my medical passages run to 1,400 tokens. The mLateOn family already serves the backbone's full 8192 token context, but if your starting checkpoint carries caps, lift them:

With the per-task caps unset, truncation falls back to the tokenizer's

, which is why I configure that limit at load time above.

I made one more change, adding a punctuation skiplist that excludes punctuation tokens from document-side scoring and storage. In a 4-way ablation (none, punctuation, stopwords, both) it modestly won on quality, and it shrinks the document index by 9.6% on this data for free:

You can also point

at any base transformer, and a fresh, randomly initialized token-level projection is appended for you:

That's the classic ColBERT pipeline: a

producing contextualized token embeddings, a token-level

projecting each of them down to 128 dimensions, a

deciding which tokens count during scoring, and a token-level

. The projection starts random, so training is required before this model is useful. Interestingly, this works with strong dense embedding backbones too. A fresh projection on

reached within 0.03 of the existing-checkpoint starting points in my experiments, from nothing but the projection and 25k training pairs.

The classic ColBERT tokenization tricks (

query expansion,

prefix tokens, a document length cap, a punctuation skiplist) are all off by default and configurable. See

for the full set. For what it's worth, I tested

query expansion in four configurations for my domain finetune and none of them made a measurable difference, so don't feel obliged to reach for the classic recipe.

I measured this directly while preparing this blogpost, taking six starting points and training each with the identical recipe on 25k medical question-passage pairs from

, then evaluating on 1,000 held-out questions against a 50,000 passage corpus:

The result surprised me, and it replicated across two model families. *The

checkpoints adapt to a new domain far better than their finished siblings, overtaking them despite starting lower. These checkpoints sit after large-scale contrastive pretraining but before supervised finetuning on general retrieval, so they carry all the late-interaction structure with none of the general-purpose tuning that domain training then has to undo. The finished checkpoints, by contrast, barely moved or even regressed, at every learning rate I tried.

So, if the model family you like publishes a pre-supervised checkpoint, start there. If not, a fresh projection on a strong retrieval-pretrained backbone is a close runner-up. Continuing from a fully finished checkpoint is the weakest option for domain adaptation, despite being the most natural-feeling one.

The

uses

or

instances for training and evaluation. You can load data from the

or use local data in whatever format you prefer (e.g. CSV, JSON, Parquet, Arrow, or SQL).

Lots of public datasets that work out of the box with Sentence Transformers have been tagged with

on the Hugging Face Hub, so you can easily find them on

. Consider browsing through these to find ready-to-go datasets that might be useful for your tasks, domains, or languages.

You can use the

function to load data from datasets on the Hub:

This is the dataset I'll train on in this blogpost: 4.4 million medical questions from

, each paired with the source passage that contains its answer (averaging 941 tokens). Simple (query, relevant passage) pairs like these are the easiest retrieval training data to collect for your own domain, and as you'll see, they're all you need.

You can also use

for loading local data in common file formats:

And if your local data requires pre-processing, you can use

to initialize your dataset with a dictionary of lists:

It is important that your dataset format matches your loss function (or that you choose a loss function that matches your dataset format). Verifying whether a dataset format works with a loss function involves two steps:

There are two multi-vector specific conventions on top of this:

Loss functions quantify how well a model performs for a given batch of data, allowing an optimizer to update the model weights to produce more favourable (i.e., lower) loss values. The right loss function for your task depends on the data you have and what you're trying to achieve. You can find a full list of options in the

For the common case of question-answer or question-passage pairs, the workhorse is in-batch negatives training with

, where every other document in the batch acts as a negative for each query. Bigger batches mean more negatives and stronger training, so in practice you'll want its GradCache variant,

, which decouples the effective batch size from what fits on your GPU:

The

parameter bounds the memory by encoding documents in chunks of this size, while the effective contrastive batch size (128 in my run below, and in my ablations bigger batches bought nothing further) stays a free choice. GradCache guarantees identical results regardless of the chunk size, so lower it for smaller GPUs at only a wall-clock cost. When your document lengths vary a lot, consider its sibling

, which packs each chunk to a total token budget instead of a document count, so a chunk of unusually long documents can never spike your memory (my

at roughly 940 tokens per document corresponds to

).

One multi-vector specific trap is that the contrastive losses default to

, unlike the dense embedding equivalent which defaults to

. That 20.0 exists because a cosine similarity is a single value in [-1, 1], too narrow a range for a sharp softmax. A MaxSim score instead sums one best-match similarity per query token, so it already spans roughly [0, query_length]: a 32-token query can score up to 32. So don't copy

over from a dense training script, since it would saturate the softmax and kill your gradients.

For distillation from a stronger teacher, which is how the strongest general-purpose late-interaction models are trained, see

and the Knowledge Distillation tab in the

documentation.

You can customize the training process using the

class. This class lets you adjust parameters that can impact training speed and help you understand what's happening during training.

For more information on the most useful training arguments, check out the

. It's worth reading to get the most out of your training.

Here's an example, using the values from my actual training run:

A few of these deserve a comment:

To track your model's performance during training, you can pass an

to the trainer for evaluation loss, but concrete retrieval metrics are much more informative. Sentence Transformers includes the following built-in evaluators for multi-vector models:

For domain finetuning, the

built from your own held-out data is the one that matters. One tip on constructing it is that the corpus should be hard enough that models can be told apart. In my case the MIRIAD questions are generated from their own source passages, which makes retrieval unusually easy. Against just the 10k gold passages, nearly every model scored above 0.97 NDCG@10. If your evaluation saturates like that, add

passages (I use deduplicated passages from the training split) until the scores spread out:

The

is where all previous components come together. Here is the complete script that trained

, the model from the introduction:

That's the whole recipe: a pre-supervised checkpoint, a million domain pairs, in-batch negatives, full document length, and a higher-than-usual learning rate. The run took 14.5 hours on my single RTX 3090 at a peak of 17.5 GB VRAM, and every one of those choices was the winner of a measured comparison rather than a guess.

For readers on smaller budgets, my scaling experiments put 100k pairs (75 minutes of training) within 0.012 NDCG@10 of the full million-pair run. Most of the gain comes in the first hour.

The MultiVectorEncoder trainer supports various

subclasses, including:

Enable these via the

training argument, e.g.

, with the required dependencies installed. It defaults to

, and

activates every integration whose dependency is installed.

Refer to the

for more information on these callbacks and how to create your own.

Typically, top-performing general-purpose models are trained on multiple datasets simultaneously. However, this approach can be challenging due to the varying formats of each dataset. Fortunately, the

allows you to train on multiple datasets without requiring a uniform format. Additionally, it provides the flexibility to apply different loss functions to each dataset. Here are the steps to train with multiple datasets at once:

Each training/evaluation batch will only contain samples from one of the datasets. The order in which batches are sampled from the multiple datasets is defined by the

enum, which can be passed to the

via

. Valid options are:

To find out where the finetuned model stands, I evaluated it against over 50 retrieval model configurations across four architecture families on the MIRIAD evaluation set, built exactly as in the

section above, with 1,000 held-out medical questions searching 200,000 unique passages (the 10k gold passages hidden among 190k deduplicated distractors from the training split). This corpus is four times the size of the 50,000-passage one from

, so scores are not comparable between the two tables.

The headline results, with the full table in the collapsible below:

The finetuned model tops the table, beating the strongest zero-shot model of any architecture by +0.062 NDCG@10. In other words, the strongest zero-shot model returns the right passage as the very first hit for 75.8% of the queries, while the finetuned model does so for 84.9%, cutting the rank-1 error by more than a third.

The architecture pattern is just as clear, with the top of the table exclusively late interaction. On long documents, one vector per token beats one vector per document, even at matched training and matched backbones. DenseOn and LateOn share training data and architecture except for the head, and the late-interaction sibling wins by +0.12, with the multilingual pair (mDenseOn and mLateOn) replicating this at +0.13. Scale doesn't rescue single vectors either.

, the strongest dense model with roughly 33x the active (non-embedding) parameters of mine, still stops 0.13 short, and the 8B version scores lower than the 4B.

BM25 also performs surprisingly well, beating every sparse model, every truncation-capped multi-vector model, and all but three dense models: the multi-billion

and

, and

, which reads its full 32k token context to edge past by just 0.006. Don't expect that to transfer to your own data though. MIRIAD's questions are generated from the passages, so the lexical overlap between a query and its gold passage is far larger than in typical retrieval, and BM25's unlimited context length lets it use every one of those overlapping words while most neural checkpoints truncate. A BM25 baseline is cheap and always worth running, just don't count on this margin.

The full field at a glance, sorted by score and colored by architecture family.

Models marked

are evaluated with their document length cap lifted to N tokens, since their native caps (180 to 512 tokens) would otherwise truncate the 941-token average passages. For every multi-vector model this lift was worth +0.08 to +0.24 NDCG@10 over the as-served row, and even the dense DenseOn gained +0.03 from the same treatment.

Note that this does not mean that

is the strongest model on

domains. It's simply the strongest in

domain. This is totally fine, as I just need this model to work well on my data.

Don't underestimate the power of finetuning multi-vector models on your domain. Fourteen and a half hours on a single consumer GPU produced a model that no general-purpose retriever comes close to on this data, and the recipe is a single script with no teacher model and no mined negatives!

The fair objection to multi-vector retrieval is index size, and this domain is close to the worst case for it. Storing one vector per token, my model needs about 878 vectors per passage, so the 200,000-passage corpus takes roughly 45 GB at fp16, where a dense model needs well under 1 GB. Document length is what makes that gap so wide. The Natural Questions passages in the

average about 125 token vectors each, seven times fewer, so a corpus of short passages starts from a far smaller index than this one does. The

module compresses exactly this by clustering each document's token embeddings and storing the cluster means, keeping roughly

of the vectors:

I measured it post-hoc on the finished model, with no pooling-aware training, and on long documents it is remarkably cheap.

The solid points are uncompressed embeddings, so that every family is counted the same way and scored with exact search. You would not deploy any of them like that, though. Dense indexes routinely use int8 or binary quantization with rescoring, sparse indexes compress their postings, and multi-vector indexes use PLAID-style residual compression. Don't read those points as the disk you need to buy, but as relative storage cost.

Token pooling is the solid line. Halving the vector count costs 0.0033 NDCG@10 and leaves rank-1 accuracy untouched, and keeping only a quarter of them, at 11.2 GB, still scores 0.8991. The curve keeps going (I measured out to a tenth of the vectors, still at 0.8765) but there is little reason to push pooling that far once quantization is on the table, which is what the dashed line below is about.

The dashed line is what a real deployment might look like. I gave Omar Khattab early access to the model and the benchmark, and he measured these configurations with

at 1-bit residual quantization, using compact 17-bit centroid ids and 18-bit document ids instead of its ordinary unpacked 64-bit integers, plus document-side pruning:

That first row is 13x smaller than the raw embeddings, for 0.0155 NDCG@10. That is a far better trade than anywhere on the pooling curve. Quantization shrinks each vector while pooling and pruning cut how many you keep, so they compose, and quantization is the one to reach for first. Push further and the last row lands at 1.45 GB,

than the fp16 embeddings of

(1.64 GB), while scoring 0.0895 higher. The objection that multi-vector indexes are too big does not survive a properly configured index.

The pruning here is naive, meant only to establish that token reduction works on top of quantization, so read the bottom two rows as a floor rather than the frontier. If you would rather not hand-tune quantization at all, the

section of the companion post covers fast-plaid, Qdrant, Weaviate, and Vespa.

Multi-vector retrieval is only as expensive as its index. The raw embeddings for this corpus are 45 GB, and a properly configured index is at least 7x smaller at nearly the same accuracy. The index deserves as much of your attention as the checkpoint.

Thanks to

for measuring the quantized and pruned index configurations in

, and for the discussions around late-interaction index costs.

These pages have training examples with explanations as well as links to training scripts. You can use them to get familiar with the multi-vector training loop:

For further learning, you may also want to explore the following resources on Sentence Transformers:

And here is an advanced page that might interest you:

And the companion blogpost, covering everything about

these models:

More Articles from our Blog

Finetuning multi-vector models involves several components: the model itself, datasets, loss functions, training arguments, evaluators, and the trainer class. I'll have a look at each of

these components, accompanied by practical examples of how they can be used for finetuning strong multi-vector models.

This is a really interesting deep dive into multi-vector embedding models... 🔥 The introduction of

in Sentence Transformers v6.0 looks especially useful for ColBERT-style late interaction retrieval, where keeping multiple representations can capture much finer-grained matching than a single dense embedding. The fact that the same framework supports RAG, semantic search, and reranking makes this a very practical direction for modern retrieval systems. 🚀

I also like how the post breaks the finetuning process down into the individual pieces... datasets, loss functions, training arguments, evaluators, and the trainer class. 🧠 Having practical examples around each component makes the approach much easier to understand and reproduce, especially for people who want to move beyond using a general-purpose retriever and actually optimize a model for their own domain.

The medical retrieval results are probably the most impressive part... 💡 Training the mLateOn-medical multi-vector encoder for just 14.5 hours on a single RTX 3090 and getting better results than dense, sparse, lexical, and other multi-vector approaches shows how valuable domain-specific finetuning can be. It’s a great reminder that the biggest gains in retrieval often come from matching the model and training data closely to the actual search task rather than simply choosing the newest general-purpose model. 👏📚

Overall, this is a great practical resource for anyone experimenting with advanced retrieval pipelines... ⚡ The ability to train strong multi-vector models from scratch as well as finetune existing ones opens up plenty of possibilities for specialized search and RAG applications. I especially appreciate that the whole workflow can be set up with

... it makes an otherwise fairly complex retrieval training process feel much more approachable. 👍🤖

or

to comment
