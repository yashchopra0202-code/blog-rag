---
url: https://www.anthropic.com/news/announcing-our-updated-responsible-scaling-policy
title: Announcing our updated Responsible Scaling Policy
site: anthropic-news
date: 
scraped_at: 2026-09-04T13:11:52+00:00
---

This update introduces a more flexible and nuanced approach to assessing and managing AI risks while maintaining our commitment not to train or deploy models unless we have implemented adequate safeguards. Key improvements include new capability thresholds to indicate when we will upgrade our safeguards, refined processes for evaluating model capabilities and the adequacy of our safeguards (inspired by

), and new measures for internal governance and external input. By learning from our implementation experiences and drawing on risk management practices used in other high-consequence industries, we aim to better prepare for the rapid pace of AI advancement.

As frontier AI models advance, they have the potential to bring about transformative benefits for our society and economy. AI could accelerate scientific discoveries, revolutionize healthcare, enhance our education system, and create entirely new domains for human creativity and innovation. However, frontier AI systems also present new challenges and risks that warrant careful study and effective safeguards.

In September 2023, we

our Responsible Scaling Policy, a framework for managing risks from increasingly capable AI systems. After a year of implementation and learning, we are now sharing a significantly updated version that reflects practical insights and accounts for advancing technological capabilities.

Although this policy focuses on catastrophic risks like the categories listed below, they are not the only risks that we monitor and prepare for. Our

sets forth our standards for the use of our products, including rules that prohibit using our models to spread misinformation, incite violence or hateful behavior, or engage in fraudulent or abusive practices. We continually refine our technical measures for enforcing our trust and safety standards at scale. Further, we conduct research to understand the broader

of our models. Our Responsible Scaling Policy complements our work in these areas, contributing to our understanding of current and potential risks.

As before, we maintain our core commitment: we will not train or deploy models unless we have implemented safety and security measures that keep risks below acceptable levels. Our RSP is based on the principle of proportional protection: safeguards that scale with potential risks. To do this, we use

, graduated sets of safety and security measures that become more stringent as model capabilities increase. Inspired by

these begin at ASL-1 for models that have very basic capabilities (for example, chess-playing bots) and progress through ASL-2, ASL-3, and so on.

In our updated policy, we have refined our methodology for assessing specific capabilities (and their associated risks) and implementing proportional safety and security measures. Our updated framework has two key components:

At present, all of our models operate under ASL-2 Standards, which reflect current industry best practices. Our updated policy defines two key Capability Thresholds that would require upgraded safeguards:

ASL-3 safeguards involve enhanced security measures and deployment controls. On the security side, this will include internal access controls and more robust protection of model weights. For deployment risks, we plan to implement a multi-layered approach to prevent misuse, including real-time and asynchronous monitoring, rapid response protocols, and thorough pre-deployment red teaming.

To contribute to effective implementation of the policy, we have established:

We have learned a lot in our first year with the previous RSP in effect, and are using this update as an opportunity to reflect on what has worked well and what makes sense to update in the policy. As part of this, we conducted our first review of how well we adhered to the framework and identified a small number of instances where we fell short of meeting the full letter of its requirements. These included procedural issues such as completing a set of evaluations three days later than scheduled or a lack of clarity on how and where we should note any changes to our placeholder evaluations. We also flagged some evaluations where we may have been able to elicit slightly better model performance through implementing standard techniques (such as chain-of-thought or best-of-N).

In all cases, we found these instances posed minimal risk to the safety of our models. We used the additional three days to refine and improve our evaluations; the different set of evaluations we used provided a more accurate assessment than the placeholder evaluations; and our evaluation methodology still showed we were sufficiently far from the thresholds. From this, we learned two valuable lessons to incorporate into our updated framework: we needed to incorporate more flexibility into our policies, and we needed to improve our process for tracking compliance with the RSP. You can read more

.

Since we first released the RSP a year ago, our goal has been to offer an example of a framework that others might draw inspiration from when crafting their own AI risk governance policies. We hope that proactively sharing our experiences implementing our own policy will help other companies in implementing their own risk management frameworks and contribute to the establishment of best practices across the AI ecosystem.

The frontier of AI is advancing rapidly, making it challenging to anticipate what safety measures will be appropriate for future systems. All aspects of our safety program will continue to evolve: our policies, evaluation methodology, safeguards, and our research into potential risks and mitigations.

Additionally, Co-Founder and Chief Science Officer Jared Kaplan will serve as Anthropic’s Responsible Scaling Officer, succeeding Co-Founder and Chief Technology Officer Sam McCandlish who held this role over the last year. Sam oversaw the RSP’s initial implementation and will continue to focus on his duties as Chief Technology Officer. As we work to scale up our efforts on implementing the RSP, we’re also opening a position for a Head of Responsible Scaling. This role will be responsible for coordinating the many teams needed to iterate on and successfully comply with the RSP.

If you would like to contribute to AI risk management at Anthropic,

! Many of our teams now contribute to risk management via the RSP, including:

On July 30, we reported three incidents in which Claude models gained unauthorized access to real computer systems. We are conducting an in-depth analysis of both incidents, and planning to work with METR for an independent review. In the meantime, we’re sharing some of the changes we’ve made over the past month.

We’re opening a research preview of the Model Hardware Standard (MHS), a shared specification for AI agents to safely operate physical devices, to a first group of scientific research labs and advanced manufacturers.

This update introduces a more flexible and nuanced approach to assessing and managing AI risks while maintaining our commitment not to train or deploy models unless we have implemented adequate safeguards. Key improvements include new capability thresholds to indicate when we will upgrade our safeguards, refined processes for evaluating model capabilities and the adequacy of our safeguards (inspired by

), and new measures for internal governance and external input. By learning from our implementation experiences and drawing on risk management practices used in other high-consequence industries, we aim to better prepare for the rapid pace of AI advancement.

As frontier AI models advance, they have the potential to bring about transformative benefits for our society and economy. AI could accelerate scientific discoveries, revolutionize healthcare, enhance our education system, and create entirely new domains for human creativity and innovation. However, frontier AI systems also present new challenges and risks that warrant careful study and effective safeguards.

In September 2023, we

our Responsible Scaling Policy, a framework for managing risks from increasingly capable AI systems. After a year of implementation and learning, we are now sharing a significantly updated version that reflects practical insights and accounts for advancing technological capabilities.

Although this policy focuses on catastrophic risks like the categories listed below, they are not the only risks that we monitor and prepare for. Our

sets forth our standards for the use of our products, including rules that prohibit using our models to spread misinformation, incite violence or hateful behavior, or engage in fraudulent or abusive practices. We continually refine our technical measures for enforcing our trust and safety standards at scale. Further, we conduct research to understand the broader

of our models. Our Responsible Scaling Policy complements our work in these areas, contributing to our understanding of current and potential risks.

As before, we maintain our core commitment: we will not train or deploy models unless we have implemented safety and security measures that keep risks below acceptable levels. Our RSP is based on the principle of proportional protection: safeguards that scale with potential risks. To do this, we use

, graduated sets of safety and security measures that become more stringent as model capabilities increase. Inspired by

these begin at ASL-1 for models that have very basic capabilities (for example, chess-playing bots) and progress through ASL-2, ASL-3, and so on.

In our updated policy, we have refined our methodology for assessing specific capabilities (and their associated risks) and implementing proportional safety and security measures. Our updated framework has two key components:

At present, all of our models operate under ASL-2 Standards, which reflect current industry best practices. Our updated policy defines two key Capability Thresholds that would require upgraded safeguards:

ASL-3 safeguards involve enhanced security measures and deployment controls. On the security side, this will include internal access controls and more robust protection of model weights. For deployment risks, we plan to implement a multi-layered approach to prevent misuse, including real-time and asynchronous monitoring, rapid response protocols, and thorough pre-deployment red teaming.

To contribute to effective implementation of the policy, we have established:

We have learned a lot in our first year with the previous RSP in effect, and are using this update as an opportunity to reflect on what has worked well and what makes sense to update in the policy. As part of this, we conducted our first review of how well we adhered to the framework and identified a small number of instances where we fell short of meeting the full letter of its requirements. These included procedural issues such as completing a set of evaluations three days later than scheduled or a lack of clarity on how and where we should note any changes to our placeholder evaluations. We also flagged some evaluations where we may have been able to elicit slightly better model performance through implementing standard techniques (such as chain-of-thought or best-of-N).

In all cases, we found these instances posed minimal risk to the safety of our models. We used the additional three days to refine and improve our evaluations; the different set of evaluations we used provided a more accurate assessment than the placeholder evaluations; and our evaluation methodology still showed we were sufficiently far from the thresholds. From this, we learned two valuable lessons to incorporate into our updated framework: we needed to incorporate more flexibility into our policies, and we needed to improve our process for tracking compliance with the RSP. You can read more

.

Since we first released the RSP a year ago, our goal has been to offer an example of a framework that others might draw inspiration from when crafting their own AI risk governance policies. We hope that proactively sharing our experiences implementing our own policy will help other companies in implementing their own risk management frameworks and contribute to the establishment of best practices across the AI ecosystem.

The frontier of AI is advancing rapidly, making it challenging to anticipate what safety measures will be appropriate for future systems. All aspects of our safety program will continue to evolve: our policies, evaluation methodology, safeguards, and our research into potential risks and mitigations.

Additionally, Co-Founder and Chief Science Officer Jared Kaplan will serve as Anthropic’s Responsible Scaling Officer, succeeding Co-Founder and Chief Technology Officer Sam McCandlish who held this role over the last year. Sam oversaw the RSP’s initial implementation and will continue to focus on his duties as Chief Technology Officer. As we work to scale up our efforts on implementing the RSP, we’re also opening a position for a Head of Responsible Scaling. This role will be responsible for coordinating the many teams needed to iterate on and successfully comply with the RSP.

If you would like to contribute to AI risk management at Anthropic,

! Many of our teams now contribute to risk management via the RSP, including:
