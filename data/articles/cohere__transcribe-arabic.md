---
url: https://cohere.com/blog/transcribe-arabic
title: Meet Cohere Transcribe Arabic
site: cohere
date: 
scraped_at: 2026-09-04T13:25:21+00:00
---

Key takeaways

Today, we are releasing Cohere Transcribe Arabic as an open-source model. Based on our

released earlier this year, Cohere Transcribe Arabic is built for the realities of Arabic in business and developer settings: dialect variation, bilingual Arabic-English speech, code-switching, and domain-specific vocabulary.

It is the most accurate, open-source Arabic speech-to-text model to date, outperforming leading alternatives, including Whisper and OmniASR, across dialects and common speech patterns. It also delivers substantial gains over Cohere Transcribe on both Arabic and bilingual Arabic-English audio.

Cohere Transcribe Arabic is available under the

. Developers can

and read our quickstart implementations on Hugging Face, or access the hosted model through the

or

.

Arabic is a remarkably rich language in both script and speech. More than 300 million people speak Arabic as their mother tongue, across roughly 30 recognized varieties shaped by distinct cultural, regional, and historical contexts. Saudi Arabia alone is home to three major dialect groups and many more linguistic subgroups.

This diversity, however, heavily complicates efforts towards normalisation. While Modern Standard Arabic (MSA) provides a

common written standard, everyday speech varies significantly across dialects. Morphological differences, regional pronunciation, and code-switching — the use of Arabic and non-Arabic vocabulary in the same conversation, often in professional settings — make a single, uniform approach to communication difficult.

The challenge is especially stark in the development of natural language technology, such as ASR. How do you train a model that preserves dialectal nuance while remaining useful beyond a particular market? The result has been a frontier-language gap: Arabic remains under-served by state-of-the-art AI systems while English continues to dominate model development and evaluation.

To help narrow that gap, Cohere embarked on a simple mission: build an enterprise-ready solution that lets Arabic users speak in their natural voice.

We started with Cohere Transcribe (launched in March with leading English-language accuracy and broad multilingual coverage) and trained it extensively on data spanning Arabic dialects, professional language, code-switching, and varied acoustic conditions.

The result is a new state-of-the-art solution in how Arabic speech is captured, ready for production use and openly available to all.

Cohere Transcribe Arabic achieves the lowest average word error rate (WER) of any open-source model on the

, with a WER of 25.87. This is a 2.45-point improvement over the previous leader, Meta’s OmniASR-LLM-7B, and an 11-point improvement over OpenAI’s Whisper Large V3.

Image 2: the Open Universal Arabic ASR leaderboard as of 07.07.26. This public benchmark evaluates zero-shot multi-dialect generalization across six test sets spanning MSA, Egyptian, Gulf, Levantine, and Maghrebi dialects. See the

on the benchmark methodology.

The gains are broad-based. Cohere Transcribe Arabic delivers the best overall WER and ranks first on four of the six composite task sets. On Casablanca, for example, which evaluates conversational Arabic across eight dialects, it improves on OmniASR by nearly six points. On Common Voice, a crowd-sourced dataset covering 25 dialects, it reduces WER by more than two points from a low previous base.

The performance carried through to human evaluations with native Arabic speakers. Evaluators assessed transcription quality across three dimensions:

Cohere Transcribe Arabic scored highest on all three dimensions compared with Whisper and Cohere Transcribe. In head-to-head evaluations, it was preferred over Whisper in 95.8% of tests.

The model also improved significantly on Cohere Transcribe for English spoken with an Arabic accent, covering many workplace and second-language English use cases. Human evaluators preferred Cohere Transcribe Arabic over Cohere Transcribe in 77.2% of tests, and found it broadly comparable to Whisper on these inputs, with Cohere Transcribe Arabic preferred in 52.6% of tests.

Cohere Transcribe Arabic is built for high-throughput serving in production environments, where performance under concurrent demand matters as much as model quality.

around vLLM to handle high-volume speech workloads, even when audio inputs vary in length. Further updates to the runtime and model stack helped yield up to 2x higher throughput.

Overall, Cohere Transcribe Arabic achieves an RTFx (real-time factor multiple) score of 525 versus 146 for Whisper Large V3 and 66 for omniASR 7B-LLM.

Read the following examples to see how Cohere Transcribe Arabic successfully handles code-switching and dialectic nuance within an enterprise setting.

Where Cohere Transcribe Arabic wins:

Where Cohere Transcribe Arabic wins:

Everyone deserves sovereignty when it comes to AI — no matter their mother tongue. It begins with control: over data, infrastructure, and your models.

Cohere Transcribe Arabic runs efficiently on consumer hardware, with no reliance on external APIs or cloud services, and is available under a permissive license. We’re giving developers open access to state-of-the-art speech AI in their own language and deployable on their own terms.

What’s next? We’re expanding enterprise-grade transcription capabilities and bringing support for new speech-powered applications for North users. This is all in collaboration with our regional partners and fast-growing local developer communities.

If you’d like to know how Cohere can make your AI capabilities more sovereign, please

.

Model weights are available today on

. You can test the model beforehand in our

.

Cohere Transcribe Arabic is also available through the

with free access subject to rate limits. Get a production key and refer to the

to get started.

For managed production deployment

rate limits, provision a dedicated Model Vault from your

. Pricing is calculated per instance-hour, with discounted plans available for longer-term commitments.

We want to see what developers build with Cohere Transcribe Arabic. Share your projects with us on

,

, or Hugging Face. These are also the best places to provide feedback and discuss new features or integrations.

Written By

Cohere Team

Tags

Share

AI isn’t a shortcut.

It’s how business gets ahead.
