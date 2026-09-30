---
url: https://www.microsoft.com/en-us/research/blog/introducing-quine-an-ai-research-system-designed-for-the-complexity-of-biology/
title: Introducing Quine: An AI research system designed for the complexity of biology
site: microsoft-research
date: 2026-09-29
scraped_at: 2026-09-30T10:07:58+00:00
---

Published

By

Share this page

For more than two decades, Microsoft Research has worked at the intersection of computation and biology.

has spanned immunology, virology, genomics, biomedical imaging, cell biology, and protein engineering. That work has produced foundational methods, new science, and technology that reached the clinic, from rare and infectious disease diagnosis to cancer biomarker detection.

Across that work, one lesson has become increasingly clear: biology does not divide itself into the neat boundaries our models and tools often do. Genes influence proteins; proteins interact within cells; cells organize into tissues; and experiments continually reshape what scientists know and what they choose to ask next. Making progress on the hardest biological questions therefore requires more than increasingly capable models of individual datasets or tasks. It requires systems that can connect knowledge across scale and modalities, reason about experiments and evidence, and participate in the iterative process through which science advances.

Today, Microsoft Research is introducing

, a research effort designed to work across those boundaries, reflecting our long-term vision for a discovery system that evolves through scientific use. Quine brings together a world model of biology with a harness that connects scientific tools, literature, the wet lab, and the researchers using them.

Even as experimental techniques have improved and wet-lab throughput has increased, biology remains fundamentally constrained by time and complexity. Nature cannot be rushed, nor can it be derived from first principles. Experiments are slow, iteration cycles are long, and many of the most important questions involve interactions, combinatorial design spaces, and downstream effects that are simply too large to explore experimentally alone.

At the same time, advances in large-scale machine learning, particularly the emergence of general-purpose foundation models and reasoning models that can iteratively work through problems, suggest a new possibility. These systems are beginning to demonstrate capabilities beyond pattern recognition: integrating information across domains, reasoning over abstractions, and supporting iterative problem-solving. Just as importantly, many of the techniques developed for human language have proven remarkably adaptable to aspects of biology, enabling models to learn representations of biological systems across diverse data types and scales.

This raised a provocative question for us:

By

, we mean a system that can represent the state of a biological system, predict how that state will evolve in response to interventions, and reason over the consequences of those interventions multiple steps into the future. Such a system would not replace experimentation. Rather, it would allow us to use computation to explore, propose, rank, and prioritize potential paths forward before committing scarce laboratory resources. Our north star is a future in which scientists, models, and experiments operate in a continuously accelerating loop.

Quine is our first step toward that vision. It includes both a world model of biology and a harness that connects the model to orchestration and reasoning models, scientific tools, the literature, and the teams of scientists using them.

Core to this effort is the world model, which learns shared representations across biological modalities and scales, including sequence, structure, function, cellular state, and imaging data. By training across these modalities jointly, Quine can use evidence from one modality to inform predictions in another, capturing relationships that would otherwise remain siloed or lost when separate single-domain specialist models are orchestrated by the system. This multimodal design reflects the reality of biology: understanding any one level requires context from the others. Rather than diluting performance, we find that learning across these connected representations strengthens it, enabling the model to generalize more effectively and to support a broader range of biological reasoning tasks.

By integrating this model in a unified system that facilitates computational experimentation and learns from iteration, researchers can generate predictions across modalities and reason about the consequences of biological interventions before they are tested in the lab. Critically, the world model doesn’t need to be perfect—indeed, it will never perfectly model biology—it simply needs to usefully inform experimental design.

A concrete example comes from our work on pancreatic ductal adenocarcinoma (PDAC), the most common form of pancreatic cancer and one of the most challenging to treat. In

, we have spent years developing and applying patient-derived

models to investigate a longstanding hypothesis: that tumor behavior and drug response depend not only on genetics, but also on transcriptional cell state. In PDAC, tumor cells can occupy different cellular states associated with how they respond to treatment.

With Quine, we have now put that hypothesis into practice, exploring whether non-genetic features of cancer, particularly cellular state, can serve as actionable therapeutic targets. We used Quine to predict and prioritize thousands of compounds based on their potential to shift tumor cells between therapeutically relevant states. In wet-lab studies focused on the transition from classical to basal cell states, Quine’s highest-ranked compounds produced the largest intended shifts across experimental assays. The entire process—from rapidly narrowing the compound search space to prioritizing a handful of promising candidates to be validated in the lab—took just one weekend, potentially saving months of experimental work and significant research costs. Notably, some of the strongest effects came from compounds with unexpected mechanisms of action, offering early evidence that AI can uncover new opportunities for drug repurposing and discovery.

While the reverse state transition proved more difficult (from basal to classical cell states), Quine predicted that available compounds would have this weaker effect. More notably, the experiments revealed something we did not fully anticipate: Quine predicted that several compounds would consistently move cells toward a

third phenotype—an observation borne out in the lab—suggesting that the pancreatic cancer cell-state landscape is richer than a simple classical-basal axis. The experiments not only tested the model’s hypotheses but also generated new ones.

Our continued work here will use newly integrated RNA datasets and tasks to represent this richer landscape, strengthen state-transition predictions, and provide calibrated confidence estimates that help scientists prioritize the most promising hypotheses for wet-lab testing. And this is exactly the feedback loop Quine was built to support. Each round of experimentation improves our understanding of biology, and each new insight can become training signal for the next generation of the system.

We created Quine to improve how we do science ourselves. As the system evolved, we embedded it in our ongoing scientific programs. Every research question, experimental result, and unexpected finding became an opportunity to refine the models, improve the workflows, and better understand where AI could meaningfully accelerate our research. Over time, the system became central to how we approached discovery across multiple domains, including in cancer biology, protein engineering, genomics, and bioimaging.

We’d like to continue building on that foundation by introducing Quine at this early stage. Quine grew out of our own research, but we don’t want its continued development to happen in isolation. Many of the questions that will determine where it goes next are not ones we can answer alone; they require the expertise, creativity, and perspectives of the broader scientific community. For this reason, we’re opening the

to put the system directly into the hands of scientists working at the frontier of biology and medicine.

Building responsibly will always come first. We believe progress in AI and biology must go hand in hand with safety, security, and responsible stewardship. We are taking a deliberate, phased approach to Quine’s development and access, with initial availability limited to the Quine Fellows program and select research collaborations. Ongoing internal review and built-in safeguards will help us maintain appropriate oversight as the system evolves. As the technology matures, we expect to expand access through products like

It’s tempting to frame progress in AI for biology around benchmarks and leaderboards. Those matter, but the real test of Quine is what happens when it encounters science as it’s actually practiced. Can it be useful when evidence is incomplete? When facing questions genuinely never asked before? Can it help make the path from questions to discovery shorter?

Ultimately that’s the standard we care about. The ambition is for Quine to recede into the background of scientific practice, while the science moves faster in the foreground. The protagonists are not the model or the platform. They are the scientists, the experiments, and the discoveries that follow.

VP and Distinguished Scientist

Vice President
