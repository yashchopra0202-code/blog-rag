---
url: https://www.perplexity.ai/hub/blog/ai-detector
title: How AI detectors work and why a score alone can’t prove authorship
site: perplexity
date: 2026-09-15
scraped_at: 2026-09-16T08:58:27+00:00
---

Learn how AI detectors analyze writing, what scores mean, and why a percentage alone cannot prove who wrote the text.

Contents

Paste an essay, article, or email into an AI detector, and a few seconds later it may return a result like “85% AI.”

Seems precise. But it can also be easy to misread.

The detector didn’t observe

the document was written. It analyzed the finished text for patterns associated with AI-generated writing. Depending on the tool, that 85% might represent the estimated likelihood that AI produced the document or the share of the text the detector flagged.

That makes an AI detector useful as a signal, especially when something needs a closer look. But the score still needs context and supporting evidence before anyone draws a conclusion about who wrote the text or how they created it. Understanding how detectors produce their scores helps explain both what they can catch and why they sometimes get it wrong.

An AI writing detector looks at a finished piece of text and estimates whether it resembles writing produced by a language model. A user typically pastes in the text or uploads a document. Within seconds, the tool may return a label, a percentage, highlighted passages, or all three.

Note: Plagiarism checkers serve a related but separate purpose. They compare a document with published material and other sources to find matching language. AI detectors assess patterns in the submitted writing. A completely original passage can therefore receive an AI flag, while copied human writing may contain no strong signal of AI generation.

Many AI detectors rely on a classifier, a machine learning model trained on examples of human and AI-generated writing. As it compares the two, it learns which patterns tend to appear in each, including patterns in word choice and sentence structure. It then looks for those patterns in new text and produces a prediction.

What the detector learns depends on what it sees during training. A tool trained on a limited range of writing may struggle with a new subject, an unfamiliar style, or output from an AI model it hasn’t encountered before.

across different types of text and AI models has found that detection performance can drop under those conditions.

Some methods take a different approach. Instead of training a separate classifier, they use a language model’s own probability estimates to judge how likely it would be to produce a passage.

Every result reflects both the text and the system evaluating it, which is why different detectors can reach different conclusions about the same passage.

and

come up often in explanations of AI detection. They can reveal useful patterns in a piece of writing, but neither points to a single, uniquely AI way of writing.

One potentially confusing detail:

is doing double duty here. In lowercase, it’s a statistical measure. With a capital P, it’s us.

Language models generate text by assigning probabilities to possible next tokens, which may be whole words or parts of words. Perplexity measures how well a model can predict the tokens in a passage.

The score is

to the model doing the evaluation and the way the text is processed, so the same passage can receive different perplexity scores under different setups.

Take the sentence, “Please let me know if you have any questions.” A language model has likely encountered similar wording many times, making each word relatively easy to predict. That tells us something about the sentence’s familiarity. It says nothing conclusive about who wrote it.

Burstiness is used more loosely in discussions of AI detection. It generally describes how much the writing changes across a passage. That can include variation in sentence length and structure, or shifts between highly predictable and more surprising language.

Some AI-generated text is consistent and predictable, which is why burstiness became associated with detection. Human writing can have the same qualities, especially in business, academic, and technical contexts. AI models can also produce more varied language when prompted or edited to do so.

says perplexity and burstiness were two of several features used by an earlier version of its detector.

Perplexity and burstiness describe patterns in a passage. Those patterns may help explain why text was flagged, but they cannot establish who wrote it.

An “80% AI” result looks straightforward. Its meaning depends on the detector.

describes the percentage as its model’s estimated probability that AI or a human wrote the document.

uses the percentage to show how much of the qualifying prose its model flags as potentially AI-generated or modified with certain AI tools.

The same “80% AI” label could therefore mean:

Those are different findings. One makes a prediction about the document as a whole. The other identifies how much of the text matched the detector’s criteria.

Probability scores need another check: calibration. If a detector gives 100 documents an AI probability of around 80%, roughly 80 of them should actually be AI-generated for the score to be

. Testing the model against examples with known origins shows how closely its probabilities match real outcomes.

A percentage can look exact before its meaning or reliability is clear. The label, the scoring method, and the detector’s performance all determine what the number can support.

A detector still has to decide when a score is high enough to act on. That dividing line is called the cutoff, or threshold.

Suppose a tool scores text from 0 to 100 and flags anything above 70. Moving the cutoff to 60 would leave every score unchanged while increasing the number of documents flagged.

The two possible mistakes have different names.

Where a detector draws the line reflects which error it is designed to avoid. That choice carries more weight when a flag could affect a grade, a job, or someone’s credibility.

The impact of a 2% false-positive rate depends on how much human writing the detector reviews.

Consider a hypothetical set of 1,000 articles:

Here’s what happens:

AI-generated

50

45 correctly flagged

Human-written

950

19 incorrectly flagged

Total

1,000

64 flagged

The detector flags 64 articles in total. Nineteen are human-written, so nearly 30% of its flags are wrong.

The 2% and 30% figures measure different things. The detector incorrectly flags 2% of all human-written articles. Those mistakes then make up nearly 30% of everything it flags.

The numbers add up this way because the detector reviewed far more human-written articles than AI-generated ones. Even a small error rate can produce a meaningful number of incorrect flags when it applies to a much larger group.

The term

describes how common AI-generated writing is in the material being checked. As that share changes, so does the meaning of a positive result. If the detector’s true-positive and false-positive rates remain the same, a flag will generally be more reliable when AI-generated writing is common in the collection and less reliable when it’s rare.

These numbers are hypothetical and do not describe a particular detector. In a real review, the share of AI-generated writing is usually unknown. That uncertainty is another reason to treat a flag as a reason to look more closely, rather than proof of how a document was written.

An accuracy rate describes performance under a particular set of conditions. Before applying that rate to another piece of writing, check:

, for example, requires at least 300 words of long-form prose. It says its model does not reliably detect AI-generated poetry, scripts, code, or other non-prose formats. Strong performance on essays therefore tells us little about how the same detector will handle a poem or a short email.

In 2024, researchers tested 12 detectors using

, a benchmark containing more than 6 million AI-generated passages across 11 models and eight subject areas. Performance fell when detectors encountered unfamiliar models, different generation settings, or deliberately modified text.

using RAID produced stronger results under more familiar conditions. Several participants detected over 99% of the machine-generated text while maintaining a 5% false-positive rate. The subject areas and AI models used in the test were also represented in the training data.

Together, the results show that detectors can perform well on varied material they were trained to recognize, while unfamiliar material remains harder to assess.

In a

, seven detectors incorrectly classified an average of 61.3% of 91 TOEFL essays written by non-native English speakers as AI-generated. That result applies to the tools and samples tested at the time. It also shows why an overall accuracy rate may not describe performance equally well for every group of writers.

The closer the submitted text is to the material used in testing, the more relevant the reported result becomes.

AI can play many roles in the writing process. Someone might use it to research a topic, organize notes, translate a passage, polish a sentence, or produce a first draft.

Those workflows can lead to very different documents. One writer may use AI for research and compose every sentence independently. Another may substantially rewrite an AI-generated draft. A third may add one generated paragraph to an otherwise human-written article.

A text detector sees the words that were submitted. It has no access to the prompts, edits, or decisions that came before them. Its score cannot reconstruct the full writing process or determine whether the author followed a particular policy. For example,

Applying those rules requires evidence about the process as well as the finished text. Draft history, research notes, and a writer’s explanation can provide context that a detector cannot.

explicitly advises educators against using its AI-writing score as the sole basis for adverse action against a student.

A detector can identify language that resembles the patterns it associates with AI. Deciding what happened, and whether it was allowed, requires a broader review.

Some AI systems can add a detectable pattern as they generate text. This process is called watermarking.

Google DeepMind’s

provides one example:

Because the pattern is added during generation, it can provide information tied to the system that produced the text.

Watermarks can strengthen the evidence when a compatible system generated the text and enough of the signal remains. They cannot identify every piece of AI-generated writing.

These records provide more direct context about the writing process than a pattern-based score alone.

Whether the wording matches patterns associated with AI-generated text

Who wrote the document or which tools were used

Which sections most influenced the detector’s result

Why those passages have those patterns

How the document changed over time

Every influence on the writer’s thinking

Which sources informed the work

Who composed every sentence

Where an AI tool contributed to the process

Whether all AI use was disclosed

Whether text contains a detectable signal inserted by a compatible generator

That unmarked text was written by a person

A detector result becomes more useful when it has a defined role. Before acting on a flag, reviewers should understand what the tool measured, confirm that the text falls within its scope, and examine the other evidence available.

Five checks can help:

The stakes should shape the depth of review. An editor may use a flag to decide which article needs another look. A decision affecting a grade, job, or publishing agreement calls for stronger evidence and an opportunity for the author to explain their process.

An AI detector compresses a complex judgment into a score. Interpreting that score requires information the number does not contain: what the tool measured, which threshold it used, how it performed on comparable writing, and how common AI-generated text is in the material being reviewed. The score can direct attention. A detector score can contribute to that review, but any conclusion about authorship also requires evidence about the writing process.

Yes. A false positive occurs when a detector flags human writing as AI-generated. A false negative occurs when AI-generated writing goes undetected. The frequency of each error depends on the detector, its threshold, and how closely the submitted text resembles the material used to test it.

There is no single accuracy rate for AI detectors. Performance can vary with the language, length, subject, writing style, generating model, and amount of editing. An accuracy claim is most useful when the test conditions resemble the writing being reviewed and the result reports false positives as well as successful detections.

The definition depends on the tool. It may represent the estimated probability that a document is AI-generated, the percentage of qualifying text flagged, or a form of confidence in the result. The detector’s documentation should explain which measurement it reports.

A detector score alone cannot prove how a document was created. It analyzes the submitted text without seeing the prompts, drafts, edits, or research behind it. A reliable review considers the score alongside process evidence and the policy governing acceptable AI use.

Human and AI-generated writing can share the same statistical patterns. Formulaic language, predictable phrasing, limited vocabulary, or a style that differs from the detector’s training data may contribute to a false positive. Research has also found that some detectors tested in 2023 disproportionately flagged essays written by non-native English speakers.
