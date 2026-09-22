---
url: https://www.microsoft.com/en-us/research/blog/improving-synthesis-prediction-of-small-molecules-at-scale-with-retrochimera/
title: Improving synthesis prediction of small molecules at scale with RetroChimera
site: microsoft-research
date: 2026-09-21
scraped_at: 2026-09-22T08:55:43+00:00
---

Published

By

Share this page

Developing new medicines and materials requires making new molecules but planning how to make them is still largely manual, time-consuming, and costly. RetroChimera automatically proposes high-quality synthesis routes. The model combines two strong models with complementary strengths, learning how to rank their proposals to produce better predictions than either alone. In blind tests, PhD-level chemists prefer RetroChimera’s individual reaction predictions over preceding models and recorded literature reactions.

Custom-made molecules are unlocking advances in modern medicine, smart materials, and sustainable agriculture. Yet, progress is slowed by chemical synthesis—the time-consuming process of making new molecules from simpler building blocks in the lab. In addition, synthesis is a significant driver of drug development costs. So even as computational methods make it possible to explore large numbers of novel molecules, finding practical ways to synthesize them remains a critical challenge.

Retrosynthesis approaches this problem by working backwards from a target molecule, breaking it down step by step into simpler precursors (Figure 1). This process is comparable to playing strategic board games like chess and Go. It involves contemplating a wide range of possible immediate moves, or individual disconnections, while also requiring high-level strategic thinking to reach the end-to-end synthesis plan. However, the number of possible moves in retrosynthesis is much larger than in board games, and it is not obvious which moves would be available for a given molecule. Existing systems face major challenges, including recalling rare but strategically important reactions, robustness beyond the training distribution, and aligning with chemists’ expectations. As a result, retrosynthesis often requires highly specialized expertise, which hinders scaling and automation of scientific discovery.

In a paper recently published in the journal

, we present

, a new framework for retrosynthesis prediction. It is built around two models (Figure 2).

, a Transformer-based de-novo model, predicts precursor molecules directly from the input molecule. This gives it the flexibility to learn reaction patterns directly from data. However, its unconstrained generation can also make it prone to hallucination.

, in contrast, is a graph neural network- (GNN) based model that encodes both the target molecule and reaction templates as graphs. It selects reaction templates and predicts where they should be applied to the target molecule. Its predictions are grounded in reaction patterns extracted from the training data, so it tends to produce more accurate and reliable outputs. But it’s more constrained when encountering reactions not covered by the template library.

These differences actually turn out to be a strength. Rather than making the same kinds of predictions, the two models capture complementary patterns in chemistry and specialize in different reaction types. R-SMILES 2 performs particularly well on reactions that involve large changes over the course of the reaction, while NeuralLoc excels in reactions of low precedence and those involving more localized changes.

RetroChimera combines the ranked predictions of both sub-models using a learned ensembling strategy. Each model assigns a learned, rank-dependent vote to each predicted reactant set, and votes are added when both models propose the same reaction. By learning how much to trust each model at different ranks, RetroChimera can leverage their complementary strengths, approximately matching the better-performing sub-model across reaction classes.

As a result, RetroChimera performs strongly across both common and rare reaction classes and produces retrosynthesis predictions that better align with chemists’ judgment (Figure 3). In blind tests, expert chemists preferred disconnections of complex molecules suggested by RetroChimera over those obtained from its constituent sub-models, as well as those from more established approaches, and even from the test set itself.

We believe RetroChimera could help researchers identify promising synthesis route more efficiently, supporting faster design-make-test cycle across molecular science applications, including drug discovery and design of smart materials. RetroChimera could enable chemists to assess more—and more complex—candidate molecules at large scale. Paired with increasing levels of laboratory automation, we expect further acceleration toward closed-loop, self-improving systems for synthesis planning and execution.

RetroChimera is available on

(MIT license) and accessible via

. For instructions on how to access the checkpoint, we refer to the GitHub repository.

We invite the broader chemistry community to experiment with RetroChimera, helping us identify its strengths and shortcomings so we can enhance it in the future. We are looking forward to hearing how it performs on various targets you care about!

For a deeper look at the findings, including evaluation experiments with our external research collaborators, see the full

and the accompanying

Senior Research Scientist

Senior Researcher

Senior Researcher

Senior Principal Research Manager
