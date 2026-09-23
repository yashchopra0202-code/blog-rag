---
url: https://huggingface.co/blog/evaleval-aisi
title: https://huggingface.co/blog/evaleval-aisi
site: huggingface
date: 
scraped_at: 2026-09-23T08:58:02+00:00
---

AISI and EvalEval have previously collaborated on research that began at a

, and feedback from the Institute has helped shape the

. This next phase of the collaboration puts that shared infrastructure into practice.

As AI deployment accelerates, evaluations are becoming increasingly important sources of evidence about model and system performance. Yet results are reported across many formats, platforms, and outlets, often without enough information to reproduce them. Running the evaluations again may itself be prohibitively expensive.

EvalEval's mission is to improve this ecosystem through a shared reporting schema,

, and an open platform,

, that brings evaluation results and the information needed to interpret them into a common structure.

This builds naturally on AISI's work to make evaluation more efficient through

, more statistically rigorous through

, and more standardised in areas including transcript analysis and capability elicitation. Together, AISI and EvalEval are working to diagnose gaps in evaluation reporting and build shared infrastructure to close them.

Transcript-level transparency matters not only for reproducibility, but also for analysis and diagnosis. In this new phase of the collaboration, AISI is making publicly reported evaluation methods and findings available through Evaluation Cards where appropriate. The release includes verified results, context, and configuration information for the five benchmarks in the paper's main experiment:

These results cover six frontier models: Claude Opus 4, Claude Opus 4.5, Claude Opus 4.6, GPT-5, GPT-5.2, and GPT-5.4. The release also includes results from two related cyber evaluations—Cyber CTFs and The Last Ones—which use a different, partially overlapping set of models. The data accompany AISI's paper,

, which studies how benchmark performance depends on inference-time compute and evaluation protocol.

When results are openly released with setup information, researchers and practitioners can examine individual studies more closely and compare findings across the wider ecosystem. Where other reports lack these details, releases like AISI's provide verified reference points for interpreting evaluations in context—for example, by helping researchers understand how setup choices may influence reported performance. As more evaluators adopt EEE, open comparisons like these can support broader and more reliable meta-research.

We are excited about this adoption and look forward to further standardising and sharing evaluations with AISI and other AI evaluation organisations.

The EvalEval Coalition is a research community developing scientifically grounded research and robust deployment infrastructure for the evaluation ecosystem. Its goal is to improve evaluation science, address the lack of consensus around documenting evaluation applicability and utility, and broaden coverage of the impacts that matter for scientific research and policy analysis.

The coalition's flagship projects include

, a shared schema and repository for evaluation results, and

, which combines benchmark metadata, evaluation-run data, and model metadata into interpretable records. Together, they make it easier to understand when apparently similar scores were produced under meaningfully different conditions.

The

is a research organisation within the UK government's Department for Science, Innovation and Technology. Its mission is to equip governments with a scientific understanding of the risks posed by advanced AI. AISI conducts research and builds infrastructure to understand advanced AI capabilities and impacts, develop and test mitigations, and inform policy.

More Articles from our Blog

or

to comment
