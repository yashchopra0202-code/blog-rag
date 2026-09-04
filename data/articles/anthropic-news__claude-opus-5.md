---
url: https://www.anthropic.com/news/claude-opus-5
title: Introducing Claude Opus 5
site: anthropic-news
date: 
scraped_at: 2026-09-04T13:11:24+00:00
---

Claude Opus 5 is available today. It’s a thoughtful and proactive model that comes close to the frontier intelligence of Claude Fable 5 at half the price.

On coding and knowledge work evaluations like

and

, Opus 5 is the new state-of-the-art, though it remains behind Mythos 5 on cybersecurity tasks.

Opus 5 is designed to be used every day: it works more efficiently than other models. It’s the new default model on Claude Max, and the strongest model on Claude Pro.

Claude Opus 5 provides greatly improved performance for the same cost as its predecessor, Opus 4.8. The charts in this section show how performance changes according to the model’s effort setting, which customers can use to optimize for intelligence or conserve tokens for faster and cheaper results.

Opus 5 excels on valuable software engineering tasks. For example, on

Opus 5 surpasses all other models, and more than doubles Opus 4.8’s performance at a lower cost per task. On

, at max effort, the model performs within 0.5% of Fable 5’s peak score, but at half the cost per task; it also achieves greater performance at a given cost than all other models on high, xhigh, and max effort.

We see similar results on knowledge work and problem-solving tasks. For example:

It’s also our best and most cost-efficient model on several related evaluations:

Opus 5 is a meaningful improvement over Opus 4.8 for scientific research. It shows better performance than Opus 4.8 on every one of our life sciences evaluations, which cover topics including structural biology, organic chemistry, and bioinformatics. Its improvements are most notable on organic chemistry tasks, like inferring molecular structures from spectroscopy data (it scores 10.2 percentage points higher than Opus 4.8 on our internal benchmark), and on protein-related tasks like predicting how variations in a protein’s sequence affect how it functions (here, it scores 7.7 percentage points higher).

Finally, Opus 5 is capable of producing much stronger visual outputs:

Claude Opus 5 is much stronger at verifying its work and iterating carefully until it succeeds. In evaluations and early-access testing, we and our users found many examples of Opus 5’s agency and thoroughness:

Below are further reports from our early-access customers on their experience of working with Opus 5:

During pre-deployment testing, our automated behavioral audit found Opus 5 to be our most aligned model to date (as shown in the graph below). It adheres to

better than Opus 4.8, Sonnet 5, or Fable 5; exhibits the lowest rates of deceptive behavior; and is the least susceptible to being tricked into misuse. It’s also our safest model yet in terms of avoiding reckless actions that could have hard-to-reverse side effects.

Opus 5 does not advance the frontier in risky, dual-use capabilities. In rigorous evaluations conducted alongside private-sector and government partners, we found it remains behind Mythos 5 in both biology research and offensive cybersecurity. More information about these evaluations can be found in our

.

As with its predecessor, Opus 4.8, we’ve intentionally avoided training Opus 5 on cyber tasks. The model has nevertheless improved substantially on these tasks as a result of becoming more generally capable, and it comes close to Mythos 5 at

cybersecurity vulnerabilities. However, it remains substantially behind Mythos 5 on the

of those vulnerabilities—that is, in turning vulnerabilities into material cyber threats.

This is illustrated by Opus 5’s performance on OSS-Fuzz, an evaluation we’ve developed to assess how well models can find and then exploit vulnerabilities without extensive human guidance. Although Mythos 5 and Opus 5 identify vulnerabilities with similar success, Opus 5’s score on the development of exploits is far behind that of Mythos 5.

Claude Opus 5’s safeguards are designed to allow beneficial uses of the model in both cybersecurity and biology. They are similar to those we applied to Opus 4.8, with the exception of some stronger guardrails on a narrow range of cyber tasks.

Opus 5’s cyber classifiers are proportionally less restrictive than those on Fable 5. They allow Opus 5 to find vulnerabilities in source code, but block “binary-based” vulnerability scanning (a method more likely to be associated with malicious actors), penetration testing, and exploit generation.

Based on our testing, we expect the classifiers to intervene around 85% less often than they do for Fable 5. In

, Claude Code, and Claude Cowork, any flagged requests will fall back to Opus 4.8 by default. Fallbacks to Opus 4.8 can also be enabled on the API.

Our

(CVP) facilitates cybersecurity work that would otherwise be impeded by the model’s safeguards. Enterprises and researchers who are already part of the CVP have immediate access to a version of Opus 5 with fewer security restrictions.

Since Opus 5 has a similar suite of safeguards to Opus 4.8, it is now our most capable generally available model for scientific research. Nevertheless, the model still shows important limitations on long-running, autonomous research tasks, which is where we expect AI models to pose the most substantial biology-related risks. (Mythos 5 remains the stronger model for this type of biological work.) As part of this launch, biology-related requests that are blocked on Fable 5 will now route to Opus 5 rather than Opus 4.8.

Claude Opus 5 is available today on all platforms, priced at $5 per million input tokens and $25 per million output tokens (the same as Opus 4.8). Developers can get started with claude-opus-5 on the Claude API.

It’s also offered in Fast mode, where it runs around 2.5 times the default speed. As with Opus 4.8, Fast mode is available at twice Opus 5’s base price on the Claude Platform and through usage credits in Claude Code.

Alongside Opus 5, we’re releasing two updates in beta:

Consistent with prior Opus models, Opus 5 does not have data retention requirements for general access.

For more guidance on how to get the best out of Opus 5, see our

.

These results are from an internal run of Frontier-Bench v0.1, on the mini-SWE-agent harness and a GKE backend, mean reward over 5 attempts per task. Opus 4.8 served as fallback on safety-classifier refusals for Opus 5 and Fable 5.

On July 30, we reported three incidents in which Claude models gained unauthorized access to real computer systems. We are conducting an in-depth analysis of both incidents, and planning to work with METR for an independent review. In the meantime, we’re sharing some of the changes we’ve made over the past month.

We’re opening a research preview of the Model Hardware Standard (MHS), a shared specification for AI agents to safely operate physical devices, to a first group of scientific research labs and advanced manufacturers.

Claude Opus 5 is available today. It’s a thoughtful and proactive model that comes close to the frontier intelligence of Claude Fable 5 at half the price.

On coding and knowledge work evaluations like

and

, Opus 5 is the new state-of-the-art, though it remains behind Mythos 5 on cybersecurity tasks.

Opus 5 is designed to be used every day: it works more efficiently than other models. It’s the new default model on Claude Max, and the strongest model on Claude Pro.

Claude Opus 5 provides greatly improved performance for the same cost as its predecessor, Opus 4.8. The charts in this section show how performance changes according to the model’s effort setting, which customers can use to optimize for intelligence or conserve tokens for faster and cheaper results.

Opus 5 excels on valuable software engineering tasks. For example, on

Opus 5 surpasses all other models, and more than doubles Opus 4.8’s performance at a lower cost per task. On

, at max effort, the model performs within 0.5% of Fable 5’s peak score, but at half the cost per task; it also achieves greater performance at a given cost than all other models on high, xhigh, and max effort.

We see similar results on knowledge work and problem-solving tasks. For example:

It’s also our best and most cost-efficient model on several related evaluations:

Opus 5 is a meaningful improvement over Opus 4.8 for scientific research. It shows better performance than Opus 4.8 on every one of our life sciences evaluations, which cover topics including structural biology, organic chemistry, and bioinformatics. Its improvements are most notable on organic chemistry tasks, like inferring molecular structures from spectroscopy data (it scores 10.2 percentage points higher than Opus 4.8 on our internal benchmark), and on protein-related tasks like predicting how variations in a protein’s sequence affect how it functions (here, it scores 7.7 percentage points higher).

Finally, Opus 5 is capable of producing much stronger visual outputs:

Claude Opus 5 is much stronger at verifying its work and iterating carefully until it succeeds. In evaluations and early-access testing, we and our users found many examples of Opus 5’s agency and thoroughness:

Below are further reports from our early-access customers on their experience of working with Opus 5:

During pre-deployment testing, our automated behavioral audit found Opus 5 to be our most aligned model to date (as shown in the graph below). It adheres to

better than Opus 4.8, Sonnet 5, or Fable 5; exhibits the lowest rates of deceptive behavior; and is the least susceptible to being tricked into misuse. It’s also our safest model yet in terms of avoiding reckless actions that could have hard-to-reverse side effects.

Opus 5 does not advance the frontier in risky, dual-use capabilities. In rigorous evaluations conducted alongside private-sector and government partners, we found it remains behind Mythos 5 in both biology research and offensive cybersecurity. More information about these evaluations can be found in our

.

As with its predecessor, Opus 4.8, we’ve intentionally avoided training Opus 5 on cyber tasks. The model has nevertheless improved substantially on these tasks as a result of becoming more generally capable, and it comes close to Mythos 5 at

cybersecurity vulnerabilities. However, it remains substantially behind Mythos 5 on the

of those vulnerabilities—that is, in turning vulnerabilities into material cyber threats.

This is illustrated by Opus 5’s performance on OSS-Fuzz, an evaluation we’ve developed to assess how well models can find and then exploit vulnerabilities without extensive human guidance. Although Mythos 5 and Opus 5 identify vulnerabilities with similar success, Opus 5’s score on the development of exploits is far behind that of Mythos 5.

Claude Opus 5’s safeguards are designed to allow beneficial uses of the model in both cybersecurity and biology. They are similar to those we applied to Opus 4.8, with the exception of some stronger guardrails on a narrow range of cyber tasks.

Opus 5’s cyber classifiers are proportionally less restrictive than those on Fable 5. They allow Opus 5 to find vulnerabilities in source code, but block “binary-based” vulnerability scanning (a method more likely to be associated with malicious actors), penetration testing, and exploit generation.

Based on our testing, we expect the classifiers to intervene around 85% less often than they do for Fable 5. In

, Claude Code, and Claude Cowork, any flagged requests will fall back to Opus 4.8 by default. Fallbacks to Opus 4.8 can also be enabled on the API.

Our

(CVP) facilitates cybersecurity work that would otherwise be impeded by the model’s safeguards. Enterprises and researchers who are already part of the CVP have immediate access to a version of Opus 5 with fewer security restrictions.

Since Opus 5 has a similar suite of safeguards to Opus 4.8, it is now our most capable generally available model for scientific research. Nevertheless, the model still shows important limitations on long-running, autonomous research tasks, which is where we expect AI models to pose the most substantial biology-related risks. (Mythos 5 remains the stronger model for this type of biological work.) As part of this launch, biology-related requests that are blocked on Fable 5 will now route to Opus 5 rather than Opus 4.8.

Claude Opus 5 is available today on all platforms, priced at $5 per million input tokens and $25 per million output tokens (the same as Opus 4.8). Developers can get started with claude-opus-5 on the Claude API.

It’s also offered in Fast mode, where it runs around 2.5 times the default speed. As with Opus 4.8, Fast mode is available at twice Opus 5’s base price on the Claude Platform and through usage credits in Claude Code.

Alongside Opus 5, we’re releasing two updates in beta:

Consistent with prior Opus models, Opus 5 does not have data retention requirements for general access.

For more guidance on how to get the best out of Opus 5, see our

.
