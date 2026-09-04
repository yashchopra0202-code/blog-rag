---
url: https://cohere.com/blog/tiny-aya-in-the-wild
title: Tiny Aya in the wild: What people are building with open multilingual AI
site: cohere
date: 
scraped_at: 2026-09-04T13:25:16+00:00
---

Key takeaways

Tiny Aya is Cohere Labs' answer to a familiar problem: most AI is built for a handful of languages and needs serious hardware to run.

is open-weight, strong across 70+ languages, and light enough to run locally, even on a phone.

Shortly after release, we launched Expedition Tiny Aya, a mentor-supported research program to put the model in the hands of builders, researchers, students, and practitioners around the world, and see what they build with it. Alongside the growing body of community projects, the

was recently accepted to COLM 2026, underscoring the model's impact as both a practical foundation for multilingual AI and a contribution to the research community.

What follows is an overview of what emerged from the Expedition. Projects from this initiative yielded insights across four key themes: education and learning, building safer multilingual AI, accessibility and local deployment, and language understanding and processing. In each area, a shared pattern holds: meaningful AI innovation thrives with accessible models, strong mentorship, and the freedom to explore problems that matter locally.

Access to quality education remains a global challenge, particularly in multilingual communities. Expedition teams tackled this by creating tools that make learning more accessible and effective.

Teaching Tiny Aya to show its work (breaking solutions into ideas, lemmas, sketches, and final answers) didn't guarantee correct math, but it surfaced clear tradeoffs between how a model organizes its reasoning and how well it actually performs. This team explored whether structured reasoning could improve mathematical problem solving. Alongside the project, the team released a

, which served as the foundation for many of their experiments. The work remains ongoing: the team is continuing model training, investigating new methods through a series of research papers, and plans to publish a comprehensive paper in the coming months.

The team built a

. They combined Tiny Aya with speech recognition and text-to-speech systems, specifically designed for young users. Beyond the prototype, they developed a

, expanding children's conversations across dozens of languages to assess safety, educational value, and age-appropriate responses. Together, the voice companion and benchmark provide both a practical tool for young learners and an open resource that can help future researchers study multilingual AI safety and performance across diverse linguistic and cultural contexts, as described in their

.

As models become increasingly multilingual, safety cannot be treated as a single-language problem translated outward. Instead, it becomes a question of how alignment behaves under linguistic and cultural interference.

,

This team investigated how Tiny Aya's safety behavior changes under code-mixed prompting, where conversations naturally blend multiple languages, dialects, and scripts. Their experiments showed that safety evaluations can produce markedly different results when languages are mixed rather than used in isolation,

. Their work highlights how evaluating multilingual safety requires fundamentally different approaches than traditional methods, exposing important gaps in current alignment measurement frameworks.

,

This team explored what happens when unsafe behavior learned in one language appears in another. Through mechanistic interpretability, they found evidence that certain directions associated with misalignment may generalize between languages, though transfer strength varied significantly across language pairs. This suggests multilingual models can share underlying safety-relevant representations, but in more nuanced ways than previously thought. The team has submitted to a major conference and their work will be made public soon.

This team examined how multilingual models respond when cultural signals, language, and surrounding context point in different directions.

that models frequently rely on shallow cues rather than robust cultural understanding, with behavior shifting in surprising ways when language, geography, and context were manipulated. As Ankita Maity later reflected in a

, the project emerged from a desire to explore questions that do not fit neatly into existing benchmarks or evaluation frameworks. Their findings challenge the assumption that multilingual competence implies cultural competence and point to the need for more rigorous ways of evaluating cultural understanding in language models.

A new challenge emerges once models are no longer confined to the cloud: how to make them usable under real-world hardware, bandwidth, and privacy constraints. Expedition teams tackled this challenge from multiple angles, developing new approaches to model compression, local deployment, multilingual data creation, and privacy-preserving applications.

This team addressed one of the biggest bottlenecks in multilingual speech AI: the lack of high-quality training data for many language pairs. Focusing on Hindi and Turkish, they built a

capable of producing large-scale speech-to-speech translation datasets, with the goal of creating more than 1,300 hours of training data. Rather than starting with model architecture, they concentrated on the underlying infrastructure, developing tooling, workflows, and evaluation processes that could unlock speech translation research in under-resourced languages. Whether through the resulting translation model or the open datasets and data-generation pipeline, their work aims to make multilingual speech research more accessible to the broader community, as described in their

.

,

For newcomers navigating complex paperwork, the DocuNative team developed a system that helps users understand important documents while keeping sensitive information entirely on-device. Built around Tiny Aya, the project combines multilingual retrieval and question answering, showing that retrieval quality depends strongly on language alignment between documents and queries. The

was done alongside related efforts such as Tiny Aya Vision (below), and reflects broader exploration into practical multilingual AI tools for real-world document understanding. Continued evaluations, including benchmarks such as

, suggest strong performance for models in this size class across Norwegian language settings.

This team explored whether lightweight multilingual vision-language systems could be made accessible to researchers without large-scale compute resources. Rather than training a multimodal model from scratch, they connected existing visual encoders to Tiny Aya while keeping most parameters frozen. This parameter-efficient approach produced surprisingly strong results, nearly doubling performance in some experiments while dramatically reducing training requirements. The implementation and experiments are available in their

.

This team demonstrated that multilingual tool use could run entirely on-device. In their

, they describe a

across dozens of languages, enabling Tiny Aya to interact with external tools under tight hardware constraints. The project includes heavily optimized

, designed for efficient on-device inference, as well as an Android-based tool-calling infrastructure that exposes multilingual capabilities to mobile applications. Their experiments show that Tiny Aya remains remarkably effective even at extreme compression, making multilingual assistants significantly more accessible to developers working with limited compute resources.

,

,

Compressing language models is essential for deployment on phones, laptops, and other resource-constrained devices, but multilingual models introduce an additional challenge: compression does not affect all languages equally. This team investigated language-aware quantization strategies for Tiny Aya, exploring how model compression impacts performance across diverse languages and whether multilingual capabilities can be preserved more effectively through targeted optimization. Their findings suggest that treating multilingual compression as a single uniform problem can obscure important language-specific tradeoffs. By better understanding how quantization affects different linguistic communities, the project contributes practical techniques for making multilingual AI more accessible without disproportionately sacrificing performance in lower-resource languages.

True multilingual competence requires deep semantic understanding, not just translation. Teams pushed the boundaries of language comprehension across diverse contexts.

This team tackled the deceptively difficult challenge of determining which meaning of a word is intended from context. They trained and evaluated Tiny Aya models across more than eighteen languages, observing strong cross-lingual transfer, with some configurations achieving performance competitive with substantially larger models. Their work also introduced

, including a publicly released dataset for cross-lingual word-sense disambiguation tasks.

In an unexpected direction, this team turned attention to programming languages rather than natural language. They explored what happens when traditional programming keywords are replaced with equivalents from other languages. The results revealed that the language used within code can meaningfully influence model behavior, sometimes improving performance and sometimes introducing unexpected side effects such as code leakage. As part of their

, the team reflects on these early findings and ongoing exploration at the intersection of multilingual representation learning and code generation.

,

Rather than evaluating what Tiny Aya says, this team explored what happens inside the model as it processes more than seventy languages. By training sparse autoencoders on Tiny Aya's internal representations, they found that most features are shared across languages, while a much smaller set specialize in particular scripts or languages. They also uncovered surprising differences in how densely different languages are represented internally, without finding evidence that these differences directly explain model quality. By openly releasing their interpretability tools and analyses, the project provides new infrastructure for studying how multilingual language models organize knowledge beneath the surface, opening new directions for multilingual interpretability research. Learn more about the work in their recently published

.

Throughout this journey, the dedication of our Expedition teams and the guidance of Cohere mentors made these breakthroughs possible. We extend our gratitude to all contributors whose passion and expertise brought these projects to life.

This global collaboration, spanning time zones, cultures, and working styles, proves that great ideas emerge anywhere with opportunity and support. Looking ahead, Expedition Tiny Aya is supporting the groundwork for a future where technology adapts to people, not vice versa. Through open-source datasets, benchmarks, and methodologies, we accelerate progress toward AI that serves as a bridge between languages, cultures, and communities, democratizing knowledge and opportunity worldwide.

The momentum behind Tiny Aya continues to grow. Alongside the open-source projects featured here, the core

was recently accepted to COLM 2026, while teams continue to produce their own papers, benchmarks, datasets, and open-source tools, including multiple winners of the recent

.

Expedition Tiny Aya is one of many initiatives within the Cohere Labs Open Science Community, a global network of researchers, students, developers, and practitioners collaborating to advance AI research in the open. Through research programs, mentorship, community events, and open-source projects, we aim to create opportunities for people from a wide range of backgrounds to contribute to the future of AI. If you're interested in community-driven research, we invite you to

Written By

Madeline Smith

Operations and Community Manager, Cohere Labs

Tags

Share

AI isn’t a shortcut.

It’s how business gets ahead.
