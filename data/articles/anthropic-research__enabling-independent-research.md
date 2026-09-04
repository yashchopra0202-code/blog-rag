---
url: https://www.anthropic.com/research/enabling-independent-research
title: Enabling independent research on how people use Claude
site: anthropic-research
date: 
scraped_at: 2026-09-04T13:09:02+00:00
---

Ensuring the transition to transformative AI goes well requires understanding its impact on people and society. Right now, data on real-world interactions with AI is concentrated in a handful of labs. We think it would be good if more data was made widely available—to researchers, policymakers, and the general public.

Researchers outside the labs have two options. They can draw on analyses the labs publish, which reflect real usage but often answer the lab’s questions, rather than their own. Or they can use public datasets, which they can study however they like, but skew toward more casual use, and may not reflect how most people actually use AI. Neither is sufficient for independent research on how AI is actually being used.

This spring, we piloted a program in which three external research institutions designed and ran their own studies on Claude usage data through

(formerly named ‘Clio’), the privacy-preserving tool our own teams use to analyze usage patterns across millions of Claude conversations. We hope to scale this program in the future, so we also conducted an additional privacy audit of all data shared with third-party researchers to verify that our privacy protections held (see

).

We believe this is the first time external researchers have run public independent studies on an AI company's own usage data. Below, we discuss what the external teams found, what we learned running the pilot, and what we are weighing as we decide how to expand the program more widely. We are also publicly releasing

.

We partnered with three research groups: the

at Stanford University, the

at the University of Oxford, and

, a non-profit organization that evaluates frontier AI models. Each group developed its own research questions and used Anthropic Insights to conduct privacy-preserving analysis of roughly 250,000 Claude.ai or Claude Code conversations from April-May 2026.

We wanted our external partners to have as much independence as possible, so our contractual review rights were limited to user privacy, information that could help people violate our usage policies, Anthropic’s confidential information, and research accuracy. Anthropic otherwise had no say in the content of the findings and the researchers are free to publish their results even if they are inconvenient for Anthropic. Below are some early results. We're excited about the directions, and about what others will find now that the data is public.

The

studied how humans collaborate with AI. They looked at what types of work people bring to AI, what roles humans retain in completing that work, and where human-AI collaboration breaks down. They found:

Read their full writeup

.

The

is studying how people feel while using Claude and how that relates to Claude’s behavior. Their early results indicate:

They are still completing their writeup. When it is public, we will add a link to it here.

is estimating real-world productivity gains from coding agents and how these increases in productivity change across model generations. Their analysis of Claude Code conversations is still underway, but early results suggest:

They are still completing their writeup. When it is public, we will add a link to it here.

Sharing usage data is largely unprecedented in AI, so this pilot was as much an experiment in running such a program as it was a way to enable third-party research in a privacy-preserving way. Protecting our users’ privacy and the researchers’ independence were both paramount, and we achieved both. Anthropic Insights is designed for this—researchers never accessed raw conversations, only aggregated outputs after the same legal and privacy review as our internal work. However, all of this made the pilot slow for an AI lab’s normal research speed and resource intensive to run. Both factors present a challenge to effectively scaling it. For more details on how we ran this pilot, see the

. Below we discuss what we learned and how we addressed the challenges that arose.

Some of our partners’ research questions overlapped with work being pursued internally. For example, METR’s proposal was similar to our economics research on “

.” We found this overlap valuable: it gave external researchers the chance to examine similar data and draw their own conclusions. Whether those align with ours is something we’ll follow as their study continues. We also connected METR with our Economics team and found that this connection improved both research teams’ work.

When using Anthropic Insights, a researcher writes a question such as, “What type of guidance is this person asking for?” and Claude answers it for every conversation in the study. The answers are then aggregated into categories; researchers only see final categories and the percentage of conversations that fall under each one. Because we are relying on Claude’s judgments, the tool is sensitive to a question’s wording; a poorly phrased one can place conversations into categories that misrepresent them. Because no one can read the underlying conversations, these errors are hard to catch.

Internally, we manage this by iterating on the questions many times over weeks. External partners couldn’t do that, since repeated privacy review before sharing each dataset would have made the study infeasible. Instead, we had them test their questions on WildChat, a public dataset of human-AI conversations where they could check the answers against the underlying conversations themselves. But WildChat skews toward casual and creative use, unlike Claude traffic, so some questions that performed well on WildChat produced misleading categories once applied to actual Claude conversations. We addressed this by providing guidance on how to interpret Anthropic Insight’s outputs (see

). Going forward, we are exploring how external researchers can develop their questions and categories more effectively in advance.

Some categories in our partners’ Anthropic Insights outputs surfaced violations of our Acceptable Use Policy or Terms of Service—for instance a category of people seeking guidance on a prohibited activity. We think the public should know about misuse of our platform, so we shared most of these violations. The exceptions were categories that described

users got around our safeguards rather than

they attempted. Less than 5% of categories and conversations were affected in each study, and in each case we told researchers which clusters we had altered or removed and why. As a standard practice, when Anthropic Insights surfaces such violations, we share the aggregated data with our Safeguards team for their review. This is also an important process for our work with external researchers moving forward.

Understanding AI’s effects on society is too big a job for AI companies alone. Real oversight needs external researchers asking their own questions of real-world usage data and publishing what they find independently.

This pilot was an experiment: could external researchers conduct independent studies on our platform without compromising our users’ privacy? The effort was more challenging than we expected, and we learned many lessons, but so far the answer seems to be yes. Our partners pursued research we would not have thought to design ourselves, and each told us something new about AI’s real-world impacts. This is a promising first step, but there is far more to do.

The next step is for us to determine whether we can scale this program, both in what kinds of studies we can support given the constraints described above, and in how many we can run at once. We are starting slowly to ensure privacy, safety, and research quality. We want to gauge interest and understand what researchers would want to study. If you are a researcher and access to Anthropic Insights would let you pursue work you cannot do today, please fill out

.

The full appendix is

. It describes how we ran the program, including how we chose our three partners, the research primer we wrote to explain the program’s goals and what Anthropic Insights can do, and how each project moved from proposal to study design to analysis. It also includes details of our collaboration agreements, which explicitly say our partners are free to publish findings even when they are inconvenient for Anthropic. Furthermore, we cover the third-party privacy audit of this data, conducted by Imperial College London, and the privacy threat model we hold all released data to. We also include guidance on interpreting the data we are releasing from our partners’ Anthropic Insights research studies.

Kunal Handa led the project, collaborated with the partners on their research proposals, drafted research guidance and the contract, ran partners’ Anthropic Insights studies, helped build the technical infrastructure supporting partners’ research, contributed to the internal review of the Anthropic Insights outputs, and wrote the blog post. Miranda Zhang coordinated the partnerships and communications, and contributed to all parts of the work. Gabriel Nicholas coordinated the third-party privacy audit, internal review of Anthropic Insights’ outputs, and contributed to all parts of the work. Miles McCain wrote the guidance on interpreting Anthropic Insights outputs, developed technical infrastructure to support partners’ research, contributed to the internal review of the Anthropic Insights outputs, and provided feedback on the blog post and privacy threat model. Ryan Heller contributed technical infrastructure to support partners’ research. Saffron Huang contributed to the internal review of the Anthropic Insights outputs and provided key feedback and discussion. Thomas Millar and Suzanne Wang contributed technical infrastructure to support partners’ research and to the internal review of the Anthropic Insights outputs. Shan Carter, Mo Julapalli, Matt Kearney, Sarah Pollack, and Judy Shen contributed to the internal review of the Anthropic Insights’ outputs. Matthew Jagielski contributed to the privacy threat model. Shaoyi Zhang contributed technical infrastructure to support partners’ research. Heather Whitney, Ankur Rathi, Aisling Keenan, and David Saunders provided legal and privacy guidance throughout the project. Jake Eaton and Sylvie Carr contributed to the framing and writing of the blog post. Jack Clark and Michael Stern provided valuable guidance, support, and discussion throughout the process. Deep Ganguli provided detailed guidance, organizational support, and feedback throughout all stages of the project.

Additionally, we thank Miriam Chaum, Ishita Dasgupta, Esin Durmus, Adam Farina, Zoe Hitzig, Jerry Hong, Devin Kuokka, Hendson Lin, Maxim Massenkoff, Peter McCrory, Maryam Quasto, Nitarshan Rajkumar, Amie Rotherham, Divya Siddarth, Taylor Sorensen, Jerome Swannack, Alex Tamkin, Molly Villagra, Scott White, and Charles Yang for their helpful ideas, discussion, feedback, and support.

For their partnership in this program, we thank Vishakh Padmakumar, Yijia Shao, Jennifer Wang, Diyi Yang, and Dora Zhao from the Social and Language Technologies Lab at Stanford, Tsvetomira Dumbalska, Hannah Rose Kirk, and Christopher Summerfield from the Human Information Processing Lab at Oxford, and Joel Becker (now at Anthropic), Daniel Paleka, and Parker Whitfill from METR.

For conducting the third-party privacy audit, we thank Zexi Yao, Bozhidar Stevanoski, Peter Romov, Euodia Dodd, Xiaoxue Yang, and Nataša Krčo.

We had Claude autonomously train models to improve their performance on several public benchmarks that measure 10 categories of alignment failure. For all 10, Claude found fixes that improved the target benchmarks without degrading capabilities.

In this post, we share two results that show how Claude can help life scientists increase the pace of their research.

Here, we identify a few examples of behavioral tendencies in current frontier models and show how they can produce unexpected systemic failures, in hopes of starting a conversation about mitigating these risks.

Ensuring the transition to transformative AI goes well requires understanding its impact on people and society. Right now, data on real-world interactions with AI is concentrated in a handful of labs. We think it would be good if more data was made widely available—to researchers, policymakers, and the general public.

Researchers outside the labs have two options. They can draw on analyses the labs publish, which reflect real usage but often answer the lab’s questions, rather than their own. Or they can use public datasets, which they can study however they like, but skew toward more casual use, and may not reflect how most people actually use AI. Neither is sufficient for independent research on how AI is actually being used.

This spring, we piloted a program in which three external research institutions designed and ran their own studies on Claude usage data through

(formerly named ‘Clio’), the privacy-preserving tool our own teams use to analyze usage patterns across millions of Claude conversations. We hope to scale this program in the future, so we also conducted an additional privacy audit of all data shared with third-party researchers to verify that our privacy protections held (see

).

We believe this is the first time external researchers have run public independent studies on an AI company's own usage data. Below, we discuss what the external teams found, what we learned running the pilot, and what we are weighing as we decide how to expand the program more widely. We are also publicly releasing

.

We partnered with three research groups: the

at Stanford University, the

at the University of Oxford, and

, a non-profit organization that evaluates frontier AI models. Each group developed its own research questions and used Anthropic Insights to conduct privacy-preserving analysis of roughly 250,000 Claude.ai or Claude Code conversations from April-May 2026.

We wanted our external partners to have as much independence as possible, so our contractual review rights were limited to user privacy, information that could help people violate our usage policies, Anthropic’s confidential information, and research accuracy. Anthropic otherwise had no say in the content of the findings and the researchers are free to publish their results even if they are inconvenient for Anthropic. Below are some early results. We're excited about the directions, and about what others will find now that the data is public.

The

studied how humans collaborate with AI. They looked at what types of work people bring to AI, what roles humans retain in completing that work, and where human-AI collaboration breaks down. They found:

Read their full writeup

.

The

is studying how people feel while using Claude and how that relates to Claude’s behavior. Their early results indicate:

They are still completing their writeup. When it is public, we will add a link to it here.

is estimating real-world productivity gains from coding agents and how these increases in productivity change across model generations. Their analysis of Claude Code conversations is still underway, but early results suggest:

They are still completing their writeup. When it is public, we will add a link to it here.

Sharing usage data is largely unprecedented in AI, so this pilot was as much an experiment in running such a program as it was a way to enable third-party research in a privacy-preserving way. Protecting our users’ privacy and the researchers’ independence were both paramount, and we achieved both. Anthropic Insights is designed for this—researchers never accessed raw conversations, only aggregated outputs after the same legal and privacy review as our internal work. However, all of this made the pilot slow for an AI lab’s normal research speed and resource intensive to run. Both factors present a challenge to effectively scaling it. For more details on how we ran this pilot, see the

. Below we discuss what we learned and how we addressed the challenges that arose.

Some of our partners’ research questions overlapped with work being pursued internally. For example, METR’s proposal was similar to our economics research on “

.” We found this overlap valuable: it gave external researchers the chance to examine similar data and draw their own conclusions. Whether those align with ours is something we’ll follow as their study continues. We also connected METR with our Economics team and found that this connection improved both research teams’ work.

When using Anthropic Insights, a researcher writes a question such as, “What type of guidance is this person asking for?” and Claude answers it for every conversation in the study. The answers are then aggregated into categories; researchers only see final categories and the percentage of conversations that fall under each one. Because we are relying on Claude’s judgments, the tool is sensitive to a question’s wording; a poorly phrased one can place conversations into categories that misrepresent them. Because no one can read the underlying conversations, these errors are hard to catch.

Internally, we manage this by iterating on the questions many times over weeks. External partners couldn’t do that, since repeated privacy review before sharing each dataset would have made the study infeasible. Instead, we had them test their questions on WildChat, a public dataset of human-AI conversations where they could check the answers against the underlying conversations themselves. But WildChat skews toward casual and creative use, unlike Claude traffic, so some questions that performed well on WildChat produced misleading categories once applied to actual Claude conversations. We addressed this by providing guidance on how to interpret Anthropic Insight’s outputs (see

). Going forward, we are exploring how external researchers can develop their questions and categories more effectively in advance.

Some categories in our partners’ Anthropic Insights outputs surfaced violations of our Acceptable Use Policy or Terms of Service—for instance a category of people seeking guidance on a prohibited activity. We think the public should know about misuse of our platform, so we shared most of these violations. The exceptions were categories that described

users got around our safeguards rather than

they attempted. Less than 5% of categories and conversations were affected in each study, and in each case we told researchers which clusters we had altered or removed and why. As a standard practice, when Anthropic Insights surfaces such violations, we share the aggregated data with our Safeguards team for their review. This is also an important process for our work with external researchers moving forward.

Understanding AI’s effects on society is too big a job for AI companies alone. Real oversight needs external researchers asking their own questions of real-world usage data and publishing what they find independently.

This pilot was an experiment: could external researchers conduct independent studies on our platform without compromising our users’ privacy? The effort was more challenging than we expected, and we learned many lessons, but so far the answer seems to be yes. Our partners pursued research we would not have thought to design ourselves, and each told us something new about AI’s real-world impacts. This is a promising first step, but there is far more to do.

The next step is for us to determine whether we can scale this program, both in what kinds of studies we can support given the constraints described above, and in how many we can run at once. We are starting slowly to ensure privacy, safety, and research quality. We want to gauge interest and understand what researchers would want to study. If you are a researcher and access to Anthropic Insights would let you pursue work you cannot do today, please fill out

.

The full appendix is

. It describes how we ran the program, including how we chose our three partners, the research primer we wrote to explain the program’s goals and what Anthropic Insights can do, and how each project moved from proposal to study design to analysis. It also includes details of our collaboration agreements, which explicitly say our partners are free to publish findings even when they are inconvenient for Anthropic. Furthermore, we cover the third-party privacy audit of this data, conducted by Imperial College London, and the privacy threat model we hold all released data to. We also include guidance on interpreting the data we are releasing from our partners’ Anthropic Insights research studies.

Kunal Handa led the project, collaborated with the partners on their research proposals, drafted research guidance and the contract, ran partners’ Anthropic Insights studies, helped build the technical infrastructure supporting partners’ research, contributed to the internal review of the Anthropic Insights outputs, and wrote the blog post. Miranda Zhang coordinated the partnerships and communications, and contributed to all parts of the work. Gabriel Nicholas coordinated the third-party privacy audit, internal review of Anthropic Insights’ outputs, and contributed to all parts of the work. Miles McCain wrote the guidance on interpreting Anthropic Insights outputs, developed technical infrastructure to support partners’ research, contributed to the internal review of the Anthropic Insights outputs, and provided feedback on the blog post and privacy threat model. Ryan Heller contributed technical infrastructure to support partners’ research. Saffron Huang contributed to the internal review of the Anthropic Insights outputs and provided key feedback and discussion. Thomas Millar and Suzanne Wang contributed technical infrastructure to support partners’ research and to the internal review of the Anthropic Insights outputs. Shan Carter, Mo Julapalli, Matt Kearney, Sarah Pollack, and Judy Shen contributed to the internal review of the Anthropic Insights’ outputs. Matthew Jagielski contributed to the privacy threat model. Shaoyi Zhang contributed technical infrastructure to support partners’ research. Heather Whitney, Ankur Rathi, Aisling Keenan, and David Saunders provided legal and privacy guidance throughout the project. Jake Eaton and Sylvie Carr contributed to the framing and writing of the blog post. Jack Clark and Michael Stern provided valuable guidance, support, and discussion throughout the process. Deep Ganguli provided detailed guidance, organizational support, and feedback throughout all stages of the project.

Additionally, we thank Miriam Chaum, Ishita Dasgupta, Esin Durmus, Adam Farina, Zoe Hitzig, Jerry Hong, Devin Kuokka, Hendson Lin, Maxim Massenkoff, Peter McCrory, Maryam Quasto, Nitarshan Rajkumar, Amie Rotherham, Divya Siddarth, Taylor Sorensen, Jerome Swannack, Alex Tamkin, Molly Villagra, Scott White, and Charles Yang for their helpful ideas, discussion, feedback, and support.

For their partnership in this program, we thank Vishakh Padmakumar, Yijia Shao, Jennifer Wang, Diyi Yang, and Dora Zhao from the Social and Language Technologies Lab at Stanford, Tsvetomira Dumbalska, Hannah Rose Kirk, and Christopher Summerfield from the Human Information Processing Lab at Oxford, and Joel Becker (now at Anthropic), Daniel Paleka, and Parker Whitfill from METR.

For conducting the third-party privacy audit, we thank Zexi Yao, Bozhidar Stevanoski, Peter Romov, Euodia Dodd, Xiaoxue Yang, and Nataša Krčo.
