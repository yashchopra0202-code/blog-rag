---
url: https://research.google/blog/toward-provably-private-learning-from-federated-data/
title: Toward provably private learning from federated data
site: google-research
date: 
scraped_at: 2026-10-03T09:33:01+00:00
---

October 2, 2026

Katharine Daly, Software Engineer, and Daniel Ramage, Research Director, Google Research

We announce a new Federated Learning system that provides externally verifiable privacy guarantees while shifting computation to the server to improve training speed, accuracy, and device coverage.

In 2017, Google introduced

(FL) a machine learning technique that trains models across decentralized, private data. It has been used to power everyday helpful features, including

and

on Gboard,

in Google Messages, and

in Android.

Our FL systems development is guided by four essential

: (1) data minimization, (2) data anonymization, (3) transparency and control, and (4) verifiability and auditability. Years of research development on anonymization have led to

for production models through algorithms like

(MF-DP-FTRL) and

. In 2025, we

an evolved definition of FL centered on these four principles:

In “

”, we announce the next generation of our FL system, which leverages

(TEEs) to provide fully verifiable and auditable data anonymization guarantees. Logic that runs in TEEs is remotely attestable (third parties can verify the logic that is being executed), and it also gains confidentiality (its internal state cannot be observed) and integrity (the logic cannot be disrupted), subject to current-generation TEE

. Our new TEE-based FL system builds on these properties which TEEs offer at the level of a single machine to form a fully verifiable end-to-end FL system that achieves stronger privacy guarantees and improved accuracy.

has already adopted the new system and is benefiting from substantially faster compute times than our previous FL system.

Our TEE-based FL system builds on techniques developed in our earlier work on

and

The system coordinates four core operational concepts:

For more details on the TEE-based FL system design please see our whitepaper,

In earlier FL systems, device data was uploaded for the purpose of immediate aggregation, but there was no way for external observers to verify that the data was never logged or inspected. Later,

allowed uploads to be protected cryptographically, but was not compatible with

. Our new TEE-based system represents the next milestone in our ongoing effort to completely remove the need to trust the server operator.

In our new TEE-based FL system, only metrics and differentially private model weights are visible to workload operators. Encrypted training data collected from devices can only be decrypted and processed within TEEs running Python training programs represented in the access policies, and only for a limited amount of time after upload.

Devices participating in our new TEE-based FL system know the full set of server workloads that may access data they’re uploading. The access policies representing these potential future server workloads are published to

, a public transparency log, and external auditors are able to observe these logs to track the full set of server-side workloads that devices could potentially be participating in.

The KMS and data processing binaries used in our FL system can be reproducibly built from open source code published in the

Github repository.

In our earlier FL systems, the logic running on the server could be verified neither by devices nor auditors, and thus we needed to be trusted to correctly add random noise to gradient sums to provide differential privacy.

In our new TEE-based FL system, the access policies that are published to Rekor directly describe the Python program that expresses the FL training logic. To protect proprietary model architectures and data preprocessing logic while preserving auditability, our data processing TEEs support sideloading serialized information into the Python program at runtime. As long as all privacy-relevant logic remains hardcoded in the Python program, this sideloading functionality allows logic that must remain proprietary to run in the TEE while still providing strong externally verifiable privacy guarantees (see below for a discussion on

).

Gboard has deployed this TEE-based FL system to launch English and Japanese next word prediction models with stronger privacy guarantees and improved accuracy. These improvements can be attributed to several aspects of the new system design.

By collecting all device uploads before running the server-side training workload, we no longer have to worry about

in device availability impacting training progress. At server-side execution time, we can dynamically calculate the optimal device participation schedule within the program, and can use it to tune other DP parameters.

In the past, training these FL models could take 1-2 months each, with progress limited by device availability, on-device compute, and competition across multiple training workloads for the same set of device resources. With the new TEE-based system, bottlenecks have been moved to the server, and computation parallelization across many machines allows us to achieve significant speedups in training time, currently only limited by TEE resource availability.

In our new TEE-based FL system, computation of client gradients is shifted to the server, lifting limitations related to on-device compute resources that were present in earlier systems. This paves the way for training increasingly larger models using FL techniques. Integrating TEEs with accelerators will play an important role in such use cases.

The system we have described above is capable of executing not just FL training workloads in a verifiable manner, but also arbitrary workloads that can be expressed using Python. We are experimenting with running other types of workloads on this infrastructure, such as synthetic data generation workloads. Another area of exploration: using the data processing TEEs that execute arbitrary Python in combination with our other data processing TEEs that specialize in functionality such as LLM inference.

This work is a step toward rigorous proof that server side processing preserves individual privacy. With external verifiers able to inspect exactly what code we run at Google, we are able to offer strong assurances that data is processed server-side exactly as described. We expect future TEE hardware, along with ongoing research into mitigating side-channel observations, to offer deeper protections for dynamically loaded workloads against malicious server-side attacks. We anticipate that systems like ours may one day come with full proofs of correctness of the software implementations of the DP algorithms and system components.

June 26, 2026

June 10, 2026

May 27, 2026
