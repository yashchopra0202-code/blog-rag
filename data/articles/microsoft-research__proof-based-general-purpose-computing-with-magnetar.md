---
url: https://www.microsoft.com/en-us/research/blog/proof-based-general-purpose-computing-with-magnetar/
title: Proof-based general-purpose computing with Magnetar
site: microsoft-research
date: 2026-10-15
scraped_at: 2026-10-16T08:38:14+00:00
---

Published

By

Share this page

Every result a computer produces comes with an implicit question: did the program run as claimed and produce correct outputs? Today, answering that question often requires a degree of trust alongside verification. We trust the operator, the vendor, the counterparty, or the agent, and we rely on contracts, audits, and logs to establish that trust.

Zero-knowledge proofs offer a fundamentally different approach to establishing trust. A program runs, and along with its output it produces a short proof, a cryptographic certificate that this program, on these inputs, produced this output. The proof is small and fast to check. Whoever receives it can confirm the result in milliseconds without rerunning the program, and can pass the proof on to anyone else who needs the same assurance. With the zero-knowledge property, the proof also reveals nothing about inputs that should stay private.

This changes what correctness means in the real world. A result no longer has to be trusted because of who produced it. It can be checked because of what accompanies it. An AI agent acting on someone’s behalf could attach a proof that each action complied with the policy it was given. Regulated financial institutions could prove that transactions were processed correctly without making their transactions public. These become possible once producing a proof is as routine as running the program.

Zero-knowledge proofs were invented in the 1980s, and the ideas behind proving program execution have been around nearly as long. What has kept them from becoming a general tool is three challenges that have resisted being solved at the same time.

. Producing a proof has historically taken millions of times more computation than running the program itself. Years of research have brought that overhead down, but the fastest systems have achieved their speed by making compromises elsewhere.

Many proof systems require developers to manually rewrite their program as a cryptographic circuit, which is a fixed arithmetic description of that exact computation. This takes months. Every change to the application means a new circuit, and the translation is itself a frequent source of security bugs. A general-purpose alternative is to prove the execution of an ordinary processor, so that any compiled program can be proven as written. Until recently, that generality came at a steep cost in speed or security.

A proof is only as strong as the cryptography beneath it. Many proof systems rest on elliptic curves, which can be broken by a sufficiently powerful quantum computer. Microsoft is addressing this problem with its Quantum Safe Program, which will move its products and services to post-quantum cryptography, a goal it

. Post-quantum proof systems already exist, but some rest on lattice assumptions, and most rest on new cryptographic functions invented to reduce the cost of proving. These new cryptographic functions have not faced the decades of scrutiny given to the cryptography protecting today’s internet, and some rest on mathematical conjectures about error-correcting codes that have not been proven. They have bought their speed with strong assumptions.

Foundry Labs bridges the distance between Microsoft breakthroughs and the builders, scientists, and curious minds who can put them to work.

For more than a decade, Microsoft Research has worked on making zero-knowledge proofs and verifiable computing practical. Early research followed two approaches, both practical only for small programs.

lets a verifier check a long computation through a short conversation with the prover using a technique called

, but this applied only to computations with a particular layered structure.

used elliptic-curve cryptography to create very small proofs for almost any computation. But this requires a one-time trusted setup involving secret information which, if leaked, could allow anyone to forge proofs. This approach is also vulnerable to quantum computers.

In 2019, a new zero-knowledge proof system called

returned to the sum-check approach and made it work for general-purpose programs without a trusted setup. Spartan can also be instantiated with different cryptographic building blocks. That flexibility is what later allowed the proof system to be built on hash functions alone. A sequence of results then filled in the remaining pieces:

Each of these solved a piece of the problem. Magnetar is where the pieces come together.

is a zero-knowledge virtual machine, or zkVM, and it makes major progress on all three challenges at once.

Magnetar proves the execution of RISC-V, an open processor architecture with mature compilers for every mainstream language. A developer writes a program in Rust, Go, or C, compiles it as usual, and Magnetar proves it as written. Consider what this means in practice. A business policy, a data pipeline, or an interpreter for the Ethereum Virtual Machine (EVM) is just a program, and the engineers who already maintain it can prove their executions exactly as written. As a result, proving stops being a specialist activity.

Magnetar proves 7.2 to 8.7 million processor instructions per second on a laptop. Across 15 benchmark programs, from cryptographic hashing to token transfers inside a small EVM interpreter, it is 10 to 39 times faster on average than the fastest existing zkVMs on the same machine, and more than 300 times faster than two others on a token-transfer benchmark. An optimized Magnetar proves 9.5–12.8 million cycles per second, which increases each speedup reported here by about 1.3×. Its proofs verify in about 12 milliseconds.

Magnetar depends on a standard hash function such as SHA-256 or SHA-3, the same primitives that already protect every organization’s systems. It requires no elliptic curves, no lattices, no special-purpose hash functions, no trusted setup, and no unproven conjecture about error-correcting codes. Hash functions are the most thoroughly studied primitives in the cryptographic toolkit, and they are the basis of the stateless hash-based signatures that NIST standardized as its own conservative post-quantum option. For a system that must still be trustworthy in many decades to come, relying only on standard hash functions removes a cryptographic migration from the roadmap.

The same design decision pays a second dividend. Checking a Magnetar proof consists mostly of evaluating standard hash functions and binary-field arithmetic, which are exactly the operations Magnetar proves efficiently. Verifying a proof is therefore an ordinary workload for it. This is what allows Magnetar to prove computations of any size, by proving them in pieces and then combining the pieces. This also allows Magnetar to prove a long-running system such as a ledger or a blockchain.

The

gives the full design, security analysis, and measurements.

Magnetar advances zero-knowledge proofs and verifiable computing to a stage where they can be built on the cryptography that organizations already trust, at speeds that make it usable, by engineers who write normal code. Magnetar enables a future where cryptographic proofs are a routine output of computation. We expect that technology leaders will stop asking

and focus instead on

If you’re interested in exploring how zero-knowledge proofs can support your use case, we’d love to

Senior Principal Researcher and Manager
