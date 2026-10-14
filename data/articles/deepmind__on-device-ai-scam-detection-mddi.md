---
url: https://deepmind.google/blog/on-device-ai-scam-detection-mddi/
title: Google DeepMind and Singapore Government collaborate to build fine-tuned AI model for scam detection
site: deepmind
date: 2026-10-14
scraped_at: 2026-10-14T09:10:06+00:00
---

JJ Geewax and Miguel de Andrés

Collaborating with the Government Technology Agency of Singapore (GovTech Singapore) to protect users without compromising privacy.

Scams, such as investment fraud, fake job offers, and impersonation of public officials make up over half of Singapore’s reported crimes, and account for more than

. At the same time, scam tactics have shifted from simple phishing to complex social engineering, whereby attackers manipulate victims with convincing conversations before requesting money. Such scams now account for up to 80% of all losses.

To address this, Google DeepMind and the Government Technology Agency of Singapore (GovTech Singapore) have been working together as part of our

with the Singapore Government. Together, we've fine-tuned a privacy-preserving, on-device scam detection model.

Generic models often struggle with local deception techniques, making scam detection harder. To address this, Google’s lightweight Gemma model was fine-tuned on local scam conversations. These ranged from impersonations of public institutions, banks, and local figures, to trending regional schemes. This ensures the fine-tuned model will be able to distinguish benign social chatter from genuine manipulation when deployed in applications installed by citizens.

Unlike traditional threat detection, which relies on server-side scanning of messages in the cloud, this model can process conversation data directly on-device. When integrated into applications, this will allow faster analysis of conversation patterns to detect manipulative intent and help citizens act before financial or credential exposure can occur.

The roll out of the model within applications will be carefully phased and developed in partnership with the Singapore Government. When deployed, the model will only be able to access on-device conversations with the user's consent, in accordance with the terms of use of that application. As the model runs entirely on-device, neither the Singapore Government nor Google, will be able to access users’ conversations through its deployment.

Fighting scams shouldn't mean sacrificing personal privacy. Working with Google DeepMind, we're bringing advanced AI protection directly onto citizens' devices. This allows us to catch highly targeted, local scam attempts in real time while keeping personal communications private.

When the model detects manipulative conversational patterns, it triggers a real-time warning directly on the user's device advising them to pause and exercise caution before sharing sensitive information or funds.

Running a complex scam classifier model on modern smartphones is no easy task, with battery efficiency being a critical area of concern. To do this, we're relying on a two-stage pipeline:

Presented at Singapore International Cyber Week (SICW 2026), this collaboration provides a model for messaging platforms balancing user protection with end-to-end encryption. Strict governance was maintained throughout development:

The project demonstrates how AI can help counter criminality without compromising safety or privacy. It also shows how governments and model providers can work together to build tech for public good. With this lightweight, on-device model, we've proven the ability for local, real-time scam detection while ensuring chat interactions remain secure. We look forward to sharing more soon on our collaboration with the Singapore government, as well as exploring the potential for similar technology to be deployed in other countries.
