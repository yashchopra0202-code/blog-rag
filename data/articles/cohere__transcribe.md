---
url: https://cohere.com/blog/transcribe
title: Introducing Cohere Transcribe: a new state-of-the-art in open-source speech recognition
site: cohere
date: 
scraped_at: 2026-09-04T13:24:52+00:00
---

Cohere is announcing Transcribe, a state-of-the-art automatic speech recognition (ASR) model that is open source and available today

.

Speech is rapidly becoming a core modality for AI-enabled workloads and automations — from meeting transcription and speech analytics to real-time customer support agents.

Our objective was straightforward: push the frontier of dedicated ASR model accuracy under practical conditions. The model was trained from scratch with a deliberate focus on minimizing word error rate (WER), while keeping production readiness top-of-mind. In other words, not just a research artifact, but a system designed for everyday use.

Cohere Transcribe reflects that intent. It is available for open-source use with full infrastructure control, maintains a manageable inference footprint suitable for practical GPU and local utilization, delivers best-in-class serving efficiency, and is also available via

— Cohere’s secure, fully managed model inference platform.

Cohere Transcribe currently ranks #1 for accuracy on HuggingFace’s

, setting a new benchmark for real-world transcription performance.

This marks our zero-to-one in bringing high-performance speech recognition into enterprise AI workflows. Read on to learn more.

Image 1: Cohere Transcribe is an open-weights Conformer ASR model converting speech audio into text across 14 supported languages.

Cohere Transcribe is the latest standard for English speech recognition accuracy. It leads the HuggingFace Open ASR Leaderboard with an average word error rate of just 5.42%, outperforming all open- and closed-source dedicated ASR alternatives, including Whisper Large v3, ElevenLabs Scribe v2, and Qwen3-ASR-1.7B. This captures the model’s versatile capability across real-world speech tasks, such as robustness to multiple-speaker environments, boardroom-style acoustics (e.g. AMI dataset), and diverse accents (e.g. Voxpopuli dataset).

Image 2: the Hugging Face Open ASR Leaderboard as of 03.26.2026. This is a widely used, standardized benchmark evaluating automatic speech recognition systems across curated datasets using word error rate (WER) as the primary metric, computed over normalized reference-hypothesis alignments, where lower WER indicates higher transcription fidelity. See the live leaderboard

.

Critically, these gains aren’t limited to benchmark datasets. We see the same state-of-the-art performance carried over into human evaluations, where trained reviewers assess transcription quality across real-world audio for accuracy, coherence, and usability. Consistency across both evaluation methods reinforces that Cohere Transcribe’s performance translates reliably from controlled tests to practical enterprise settings.

In production settings, ASR systems must operate under strict latency and throughput constraints; even if accurate, slow or resource-intensive transcription can directly impact user experience, operational efficiency, and cost.

Transcribe extends the Pareto frontier, delivering state-of-the-art accuracy (low WER) while sustaining best-in-class throughput (high RTFx) within the 1B+ parameter model cohort.

Paige Dickie

Vice-President

Radical Ventures

We are working towards deeper integration of Cohere Transcribe with

, Cohere’s AI agent orchestration platform. With planned updates, Cohere Transcribe will evolve from a high-accuracy transcription model into a broader foundation for enterprise speech intelligence.

Cohere Transcribe is now available for download on

. Follow the setup instructions to run the model locally, or even in edge environments.

You can also access Cohere Transcribe via our

for free, low-setup experimentation subject to rate limits. See the

for usage details and integration guidance.

For production deployment without rate limits, provision a dedicated

. This enables low-latency, private cloud inference without having to manage infrastructure. Pricing is calculated per hour-instance, with discounted plans for longer-term commitments.

to discuss your requirements.

Written By

Cohere Team

Tags

Share

AI isn’t a shortcut.

It’s how business gets ahead.
