---
url: https://cohere.com/blog/the-culture-funnel-you-cant-align-what-isnt-in-the-data
title: The Culture Funnel: You can’t align what isn’t in the data
site: cohere
date: 
scraped_at: 2026-09-04T13:25:03+00:00
---

Key takeaways

Link to full paper: https://arxiv.org/pdf/2606.13808

Link to dataset: https://huggingface.co/datasets/CohereLabs/CultureMarkers

As AI systems become increasingly global, focusing on multilingual coverage alone is not enough for building systems that serve people around the world. A model may answer fluently in dozens of languages and still miss the context behind how people communicate local norms, values, assumptions, social expectations, or the ways culture shapes everyday interactions.

. But why do cultural gaps persist?

A core challenge to studying this question is that culture itself is inherently difficult to quantify: it is expressed implicitly across nearly all user interactions, shaped by context, and cannot be fully represented through language or geography alone. A common assumption is that the cultural knowledge already exists inside a trained language model and simply needs to be elicited through prompting, alignment, or better reasoning. But what if the limitation starts much earlier? In this work, we look upstream at the data itself.

To better understand where cultural gaps might originate in training data, our recent preprint,

, introduces a framework for surfacing and examining cultural signals at scale within training data. Using this lens, we trace how cultural representation changes across different stages of the LLM training pipeline and explore what these patterns suggest about building AI systems that better account for diverse cultural contexts.

After analyzing over 5.6 million

across different stages of the language model training pipeline, we found a consistent pattern: cultural diversity narrows as data moves from pretraining into post-training. We call this phenomenon

Our analysis investigates several factors associated with this pattern, including post-training dataset composition, long-tail effects in cultural content, and data curation practices.

With our analysis, we extend a principle

: “Every evaluation and data choice should be examined for culturally contingent considerations”, establishing culture as a primary factor in data documentation, processing, and evaluation.

To understand how cultural information appears throughout model development, we selected popular datasets used across different stages in LLM training - pretraining, SFT, alignment, and reasoning - and tagged a sample of prompts from each source for cultural signals. We used Cohere’s Command A model to automatically tag prompts following instructions we gave it and we validated the quality of generated tags by manually reviewing a subset of prompts across six languages. Importantly, we do not treat language or geography as substitutes for culture. The cultural signals we tag for reflect multiple dimensions of culture: domains, task intent, language, geolocation, and cultural characteristics. We define cultural characteristics based on a taxonomy developed by

) that categorizes common benchmarks used for evaluation (see examples below). This allows us to examine how cultural representation evolves as models move through training.

Our first observation is what we coin as

: pretraining data has much more cultural grounding, i.e. a higher percentage of data tagged with cultural markers, than any post-training dataset. Why is that the case? Posttraining datasets that aim to improve an LLMs reasoning or alignment tend to be much more heavily focused on technical tasks: performing mathematical calculations or writing code. This may be unsurprising given the vast improvements in LLM performance on such tasks, but it means that datasets which contain a higher percentage of cultural markers are less prominent. As a result, opportunities for LLMs to learn and reflect culturally diverse knowledge may be reduced.

We also found that most culturally grounded content that remains tends to fall into categories of

or

.This imbalance helps explain why models perform reasonably well on fact-based or trivia-oriented cultural benchmarks, yet struggle more with tasks requiring reasoning about

. If culture vanishes throughout training, models may only become better at solving abstract problems while losing the cultural understanding needed for the many other diverse user contexts they are meant to support.

One of the most common assumptions in multilingual AI is that adding more languages will automatically yield sufficient cultural coverage. Our results suggest the relationship is more complicated.

As we cumulatively add data from each language set within a dataset, we find that expanding multilingual coverage has diminishing returns in increasing the overall percentage of culturally grounded data in pretraining and SFT datasets (light blue lines in the above diagrams). The percentage of cultural content is rather determined by the strategies that data is curated: For example, the

has a much higher proportion of cultural content, because it intentionally curated culturally-grounded prompts and responses from an international community of contributors.

However, adding languages leads to an increase in the number of unique geolocations found across datasets. Thus, scaling multilinguality does not increase the overall percentage of culture-focused content in the data but does increase its geographic diversity. This means, the more multilingual, the more knowledge a model could pick up about more regions of the world.

When we examine the geolocation tags, we see that some regions are represented much more than others. We know this pattern well from

looking at the distribution of languages in large data: They follow a long-tail distribution where a small number of languages dominate most NLP resources. We found that cultural representation behaves similarly. In our analysis, within the subset of culturally tagged data, India emerges as the most frequently represented geolocation, alongside a concentration of Asian and European countries. For the example of Cultura X as shown in the figure above, only a single South American, one African, and one North American country appear within the top 50 geolocations.

Besides India, China and the USA are the dominant locations that rank under the top 10 in other datasets as well. As a consequence, when models are trained on this data, they will be favored throughout the entire training pipeline. Furthermore, cultural knowledge associated with underrepresented regions will be particularly difficult for models to learn, even if the language spoken there is well represented.

Post-training knowledge is task-centered, i.e. data is curated with user tasks in mind, and then combined in multi-task fine-tuning.The figure above highlights the cultural content distribution across tasks. We found that translation, local information requests, and message writing contain the strongest cultural signals. More technical categories such as coding or medical questions contained fewer explicit cultural markers. When we compared these patterns with our

, a more interesting picture emerged: users reported most frequently needing better cultural awareness for creative writing, translation, and email/message writing—the same tasks that our analysis reported to carry most culture in training. In addition, cultural awareness appears relevant across a wider range of tasks than current training distributions reflect, e.g. also in medical and business contexts..

Our analysis of cultural markers across training datasets makes one thing clear: cultural content is scarcely distributed in the data underlying modern AI systems. Improving cultural representation throughout the data pipeline requires efforts beyond simply scaling data; it also demands intentional curation to include diverse cultural coverage. Ideally, we would address this through community sourced data that better reflects diverse global perspectives from the start. But in practice, doing so at scale is expensive and difficult to curate across all possible domains, task intents, and geolocations, and sparcities will inevitably remain. Thus interventions beyond collecting further data are also still necessary to address these gaps.

showed that adding explicit markers to fine-tuning data can help models better learn long-tail distributions. Inspired by this approach, we add cultural markers while fine-tuning the

base model, i.e. not changing the data distribution, but adding meta-information to each training sample. This means we are not making the data “more cultural”, but the cultural content more explicit, giving the model an opportunity to learn cultural properties even if sparsely represented. We observe an improvement in performance on downstream cultural benchmarks without sacrificing general multilingual capabilities, with gains of +8% on NormAd, +6% on BBQ, and +2.3% on GMMLU.

The more common alternative, training on “more cultural” data without any markers, leads to smaller improvements in cultural benchmarks as well as degradation in general capabilities.

Across the training pipeline, we observe a consistent narrowing of cultural diversity from pretraining to post-training data. Our findings point to three key factors driving this cultural funnel.

Our findings highlight the inherently long-tailed nature of cultural representation in modern AI data. More importantly, we find that data pipelines themselves act as alignment mechanisms, shaping which kinds of cultural knowledge remain learnable by models. As a best practice, this suggests moving beyond multilingual scale alone and instead intentionally balancing representation across languages, geolocations, domains, and task intents. We also find that explicitly marking cultural dimensions during training can help models better preserve and learn long-tail cultural properties.

Ultimately, cultural capabilities in LLMs will not emerge automatically from scaling up data alone, but from intentionally designing data pipelines that make the many dimensions of culture visible, represented, and learnable.

We would like to thank everyone who shared their expertise and contributed to the Culture Funnel project and blog post. In particular we would like to thank Mehrnaz Mofakhami, Daniel D’souza, Thomas Euyang, Brittawnya Prince, Madeline Smith, Frédérique Horwood, Olivia Lasche, Aidan Peppin, Laith Sarhan, Claire Cheng.

Written By

Ananya Sahu

Research Scholar

Julia Kreutzer

Senior Research Scientist, Cohere

Marzieh Fadaee

Head of Cohere Labs

Tags

Share

AI isn’t a shortcut.

It’s how business gets ahead.
