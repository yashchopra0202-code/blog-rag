---
url: https://openai.com/index/scaling-storage-one-billion-users-part-one/
title: Rapidly scaling online storage to serve over 1 billion ChatGPT users
site: openai-index
date: 2026-08-25
scraped_at: 2026-09-12T08:14:57+00:00
---

September 11, 2026

How we adapted our application storage platform, Habitat, in Python to manage unprecedented growth.

By Jon Lee, Chaomin Yu, and Ben Ries, Members of Technical Staff

Figure 01 · What is Habitat?

Habitat is the online storage platform we built so OpenAI products can quickly and reliably access needed information.

requests per second

people each week

data

Figure 02 · Habitat service

By decoupling the storage logic into a standalone service, we established a single point of control for deployments, observability, and platform enhancements.

Figure 03 · Tracking the asyncio delay

Python asyncio allows concurrent request processing, but only a single request executes on the CPU thread at a time. This has high impact on request latencies when there's a lot of CPU work to be done.

Figure 04A · Client-side connection pooling

After a burst of requests, slower servers return connections to pool last. LIFO encourages more work to concentrate on those same slower servers.

An initial burst reaches A, B, and the slower process C.

Figure 04B · Client-side connection pooling

FIFO maintains more active connections after a burst, but balances workloads fairly across all servers.

An initial burst reaches A, B, and the slower process C.

Figure 05 · Connection fan-in

Connection pooling and HTTP/2 connection multiplexing help reduce connection load on downstreams.
