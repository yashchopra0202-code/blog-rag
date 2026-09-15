---
url: https://www.perplexity.ai/hub/blog/cobbledb
title: CobbleDB: Rebuilding AI Search Storage for Lower Latency and Cost
site: perplexity
date: 2026-09-14
scraped_at: 2026-09-15T09:05:58+00:00
---

A decoupled architecture with separated durable state, batched updates, and query-time retrieval.

Contents

AI-native search imposes different requirements on how web content needs to be processed, stored, and served. To meet those demands at scale, we have been rebuilding the entire stack from scratch to improve performance and reduce cost.

We built our

, and

to power efficient processing and fast serving. We’re now extending that approach to storage, the connective tissue that processing writes to and serving reads from.

Managed databases such as DynamoDB provided reliable storage, but we had limited control over how data was stored and reads were served, and usage-based pricing grew with our index size and query volume. Separately, our previous pipeline coupled document processing directly to the serving database, making it difficult to manage updates independently of live reads.

With help from a new internal coding agent swarm, we rebuilt this layer around CobbleDB, a key-value hot store, supported by Pillar for durable document state and publishing, and Lorry for batched updates. The redesign separates document processing from hot-store ingestion and lets us tune serving to our workload. Production before-and-after measurements show roughly 5× lower batch-read latency, and our internal cost model estimates at least 20% savings relative to DynamoDB.

A classic search stack is built for a human reader, not a language model. That difference changes the granularity at which the system needs to prepare, store, and serve web content.

To turn raw HTML into model-ready content, our processing pipeline cleans each page, splits it into semantically coherent passages, computes their embeddings, and stores the passages and embeddings together in the database. At query time, the serving pipeline selects the text most relevant to the query and passes it to the model.

The storage layer must therefore support two workflows with different demands: ingesting updates from the processing pipeline and serving low-latency reads.

On the write side, new pages arrive continuously, existing pages change, and changes to chunking methods or embedding models can require reprocessing large portions of the corpus. The storage layer must incorporate these updates into durable document state, track the current versions, publish the right representations to downstream systems, and support large backfills without repeating the full pipeline from the raw crawl.

In contrast, query-time reads request batches of page keys and retrieve the corresponding passage text and embeddings for ranking and passage selection. These reads sit on the path to the final answer, so they need to be completed quickly.

These workloads call for different designs. Processing benefits from durable queues and the ability to deliver updates efficiently, retry failures, and bring existing records up to date at scale. Serving benefits from precomputed records, warm caches, and fast batched reads with minimal query-time work. Tight coupling between the two can cause recovery work and large updates to compete with latency-sensitive reads.

DynamoDB gave us highly available storage without the burden of operating a distributed database. A dedicated prepared-pages table held passages and embeddings for query-time reads, while full page content and metadata were stored separately. However, as our workload grew, three constraints became important.

A single Search API request contains 100-120 keys corresponding to pages we need to fetch. The data retrieval process splits a request into smaller batches of 10-20 page keys with the average item size about 50 KB. Repeatedly reading those records consumed substantial capacity, while continuous crawls and changes to chunking or embedding models generated more writes. The economics also depended on the size and frequency of the records, not just the number of API calls.

The operation we needed was narrow: given a batch of page identifiers, return their prepared contents quickly. We wanted control over which machine held a partition, how much memory was devoted to its cache, and which replica handled a request. Those controls matter because an uncached read, a cross-zone hop, or a slow replica can delay the entire batch. DynamoDB manages its own storage and replica behavior behind the API. We could configure the service, but we could not tune its internal placement, storage-engine caches, or replica-selection policy around our workload.

Our previous processing pipeline wrote each prepared page directly to DynamoDB. A large reprocessing job therefore became a wave of individual hot-store updates, and processing had to accommodate the hot store's throughput limits and retry behavior. We could not run MapReduce over the entire database in 1-2 days to try a new chunking method, change our embedding model, or add a new field. There was no independent stream of saved page updates that a separate service could batch and deliver to the hot store at its own pace.

Addressing these constraints required more than replacing the database. We needed to separate durable document state and update delivery from query-time storage, then optimize the hot store specifically for fast batched reads.

The new architecture assigns each responsibility to a different component. Pillar maintains a durable document state and decides what to publish. Lorry turns those exports into partitioned batches. CobbleDB ingests the batches and serves prepared records by page key.

CobbleDB is our hot store optimized for serving prepared records at query time. It’s a distributed key-value store: the keys are page identifiers (hashed URLs), and the values are the page’s processed representation (their pre-chunked passages and per-chunk vector embeddings).

The important change is our control over storage configuration.

Data is partitioned and split across data nodes. This distributed format ensures that the database can scale horizontally to accommodate an enormous corpus of processed pages. Each partition has three replicas on three different nodes; if one copy becomes unavailable, the others can continue serving reads.

Each data node is assigned a subset of the partitions. The node stores its data using

, an open-source embedded key-value storage engine well-suited to read-heavy workloads fed by batch ingestion.

Cached data can be served from memory, while uncached reads use local NVMe storage. This gives us a direct way to tune the memory-to-disk balance for the observed workload, rather than accepting a managed service's internal cache policy.

A stateless query router hashes keys to partitions and routes requests to nodes in parallel. The architecture also includes a PostgreSQL-backed metadata service and durable object storage.

This design supports the read patterns our workload demands. After a query goes through retrieval and ranking to obtain a candidate set of relevant pages, the hot store is queried in bulk for the contents of those pages. These read requests arrive at the router and are routed to a corresponding data node. The router prioritizes sending requests to a node in the same availability zone to minimize cross-zone latency, if possible. Each data node can fetch the page contents using MultiGet, a RocksDB batch-read API designed to fetch multiple keys simultaneously at low latency. If a node is slow to respond, the system can also query another partition replica on a different node, improving tail latency.

We can also avoid implementing common features that our workflow doesn’t require. For example, most databases offer consistency guarantees and transaction support, but our hot store doesn’t require transactions or synchronized replicas. It’s acceptable for there to be a short gap between when a document is written and when it’s available for reads, and it’s also fine for one replica to ingest data faster than another. Omitting features we don’t need reduces the overhead and cost of our system.

A separate storage layer keeps track of everything we crawl and process, merging updates into versioned document state and publishing the necessary representations to CobbleDB and the search index. We built Pillar, our document state and publishing layer, for this purpose.

Pillar is backed by

. It stores page components (such as metadata, chunks, and embeddings) in separate YTsaurus table families. It also tracks the versions of chunks and embeddings, letting multiple representations co-exist without overwriting each other so that the underlying models can change. Since Pillar and YTsaurus use cheap HDD storage, we can store far more documents than we previously stored in DynamoDB.

Pillar tracks subsets, or policy-defined groups of pages such as fresh pages or high-value pages. Subset membership determines which updates need to be passed on to downstream components like CobbleDB. CobbleDB uses more expensive NVMe storage, so we only export the documents we actually want to use in search results. When a page’s contents are updated, or if it is added or removed from a subset, Pillar is responsible for queuing the corresponding export work.

Atomic YTsaurus transactions cover state, export intents, and consumed input in order to ensure correctness. For a transaction to complete successfully, the system must update the durable state, mark the input as accounted for, and queue all required exports; if the transaction aborts, no change is made at any layer.

CobbleDB expects updates to be batched according to partition. Pillar exports are converted to this format by a stateless service we call Lorry. Its sole job is to read export records from a persistent partition-aligned queue, accumulate them into per-partition batch files, and hand them to CobbleDB.

Between Lorry and Cobble, an additional protocol splits the data plane (S3) from the control plane. Lorry writes the batch to S3 under a unique identifier and registers the batch within Cobble. Cobble partition replicas independently query the batch or control plane API for the next S3 batch to ingest and asynchronously apply batch updates in chronological order. This means that a slow or recovering node can catch up at its own pace, rather than slowing down the rest of the system.

The new path separates the immediate processing transaction from hot-store ingestion and provides a replayable path for incremental updates and bulk rebuilds. This division of labor ensures that updates to durable document state don’t interfere with the read path latency.

After migrating the hot store, median batch-read latency fell from 31.4 ms to 5.60 ms. The p90 fell from 56.7 ms to 9.77 ms, and the p99 fell from 123 ms to 24.2 ms. The ratios range from 5.08× to 5.80×, with improvements in both typical requests and the tail.

These numbers are derived from batched reads, where each query requests roughly 10-15 keys. The average payload item size is 50KB. Both systems were queried at about 200k rps, although we also ran load tests up to 500k rps with no degradation.

To isolate the contribution of CobbleDB, all other aspects of the setup were held constant. However, this remains an observational before-and-after comparison; the systems served live production traffic at different times rather than the same requests under controlled conditions. We therefore also measured the performance of both systems on a synthetic benchmark. To approximate the requests seen in production, we queried both with batches of 10-15 keys and values ranging from 100B to 100 KiB.

DynamoDB struggles in this context because its managed read path can’t be tuned for batched reads of this size. In contrast, CobbleDB is optimized for exactly this setting, since we manage the placement, caching, and replica controls. It groups keys by partition, executes reads in parallel against partition replicas, and can hedge slow reads against other replicas. Our results demonstrate that these design choices translate to faster reads in a production environment.

CobbleDB is also significantly cheaper than DynamoDB. In addition to storage, DynamoDB also charges every byte read or written. At the scale of our corpus and serving traffic, these usage-based charges become a substantial part of the total cost. Continuous updates consume write capacity, while every batch of prepared pages fetched for a query consumes read capacity.

We computed the cost savings based on internal estimates of storage size, write capacity units, and read capacity units. At every commitment tier, CobbleDB is at least 20% cheaper than DynamoDB. The real savings are likely even higher, since these results don’t take into account the likely backup savings from compression.

Building CobbleDB and the surrounding infrastructure was far from trivial. CobbleDB’s core database alone is roughly 40,000 lines of Rust, and the migration also required extensive work to verify correctness and failure behavior at production scale, integrate CobbleDB with both processing and serving paths, and safely transition live traffic.

We accelerated this effort using an internal system that operates a swarm of coding agents. The system is designed to be highly persistent; it retains the project's goals, active risks, repository history, and prior decisions across sessions.

We assigned a collective of such proactive, always-on agents to the CobbleDB project. Their first task was to build an accurate model of the work already in flight. They audited the project channel and active threads, connected outstanding items to their pull requests and owners, and produced a current readout of system health and next actions. From there, they operated across several parts of the engineering loop:

Engineers still set the architecture, reviewed consequential changes, and authorized production operations. The agents handled much of the continuous inspection and follow-through between those decisions. This allowed a small team to drive the project efficiently—the core CobbleDB infrastructure was built by two human engineers and hundreds of AI agents in two months.

CobbleDB isn’t a general-purpose database; it’s purpose-built for our specific workload of repeated batch reads of prepared page records, fed by an asynchronous processing pipeline. By separating durable state, update delivery, and query-time serving, we can optimize each responsibility independently without forcing a single database interface to accommodate all of them or pushing maintenance work onto the live query path. Migrating to CobbleDB significantly improved both median and tail latency while reducing infrastructure costs.

As we continue to develop AI-native infrastructure in-house, we can optimize performance and cost in ways that aren’t possible when we’re tied to third-party implementations and pricing models. Powerful AI agents shift the calculus even further in favor of building over buying.

We plan to open-source CobbleDB soon, so other teams building AI-native search systems can benefit from the same storage layer that makes search faster and cheaper inside our products.
