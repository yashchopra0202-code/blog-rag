---
url: https://www.perplexity.ai/hub/blog/llm-security
title: What is LLM security? How to mitigate the OWASP top 10 safety risks
site: perplexity
date: 2026-10-16
scraped_at: 2026-10-17T08:10:32+00:00
---

A guide to LLM security that walks through the OWASP Top 10 for LLM Applications 2026, with a real-world incident and practical defenses for each risk.

Contents

An attack that tricks an AI into treating an attacker’s instructions as commands—prompt injection—has been

in every edition since 2023.

The list is about as close to consensus as AI security gets. The project started as a small group of security professionals and now draws on more than

We're an AI company publishing a guide to how AI gets talked into things, so we'll skip pretending this is solved. Wilson, who co-leads the OWASP project, was pretty clear

: "...frankly, I don't think we are at 99%."

The 2026 edition opens on the same note. The project lead

"stop trying to build a model that cannot be fooled" and to design the surrounding system so a fooled model can't break anything important.

We’re taking that position through all 10 risks on OWASP’s 2026 list.

LLM security means protecting AI models and the applications that use them from attacks and misuse. The risk grows with what the model is connected to: the files and data it can read, and the tools it can use, like email, search, or a company database.

In properly secured software, there's a firm line between the instructions a program follows and the information it processes. But LLMs don't have that line.

Everything the model reads arrives as one long stream of text: the developer's instructions, your question, a webpage it looked up. AI models are supposed to keep track of who's speaking, whether that's the developer, the user, or the model itself thinking through a problem.

But researchers Jasmine Cui and Charles Ye found that

. So if an attacker writes something that sounds like the model's own reasoning, the model may believe it came up with the idea itself. That's a problem for any safety setup that depends on the model knowing who's in charge.

We've run into the same problem with

. Our CISO, Kyle Polley,

that agents "might not follow policies even if you add it to the system prompt." That's why we built

, an open-source tool that checks what an agent is about to do and can block it if the action breaks a configured security rule.

LLM security means accepting that the model will sometimes take orders from the wrong person, and

around it that still hold when it does.

We'll work through the

in order, from No. 1 to No. 10.

For each risk, you'll get a plain-English explanation of how things go wrong and a real-world example. Then we'll cover the practices that can help prevent it, or at the very least, limit the damage.

01

Prompt injection

An attacker gets the AI to follow instructions it shouldn’t.

02

Sensitive information disclosure

The AI reveals private information to someone who shouldn’t see it.

03

Excessive agency

The AI has enough access and freedom to turn a mistake into damage.

04

Supply chain

A compromised model, dataset, or software package brings an attacker into your application.

05

Data and model poisoning

Someone tampers with data or a model to change its behavior or plant a backdoor.

06

Unbounded consumption

Requests or runaway tasks burn through computing power and money.

07

Misinformation

The AI produces wrong information that people or other systems act on.

08

Hidden context exposure

The AI reveals internal instructions or background information users weren’t meant to see.

09

Vector and embedding weaknesses

Weaknesses in how information is stored and retrieved let attackers expose data or disrupt answers.

10

Improper output handling

Another system uses unchecked AI output, allowing it to run commands, expose data, or cause damage.

A prompt injection happens when an attacker makes an AI follow instructions it shouldn't. Those instructions can come directly in a chat or be planted in an email, webpage, or document.

The second type is known as indirect prompt injection. You ask your assistant to summarize a document. They've told the assistant to send them your private files. If the assistant follows those instructions, the person who wrote the document has effectively borrowed your access.

prompt security to plugging holes in a porous stone. You seal one opening, and the water finds another. “An attack finds its way through; it gets fixed, but countless other avenues of attack remain to be discovered simply because of how dynamic systems like LLMs are.”

In June 2025, Aim Security researchers found

, a flaw that tricked Microsoft 365 Copilot into leaking private company information. When an employee asked a routine work question, Copilot could pull in the email, follow the instructions hidden inside it, and send sensitive information to the attacker. The attack got past the checks meant to catch malicious instructions and remove suspicious links.

When AI systems give private information to people they shouldn't see, it's called sensitive information disclosure. This could mean revealing a customer's payment details or leaving private conversations on a shared database.

Many leaks start with “oversharing.” Say a company connects its AI to drives and knowledge bases with loose permissions. The AI retrieves whatever it can reach, exactly as designed. Nobody has to break in, but consider the LLM broken into.

In January 2025,

to the internet with more than a million log entries, including chat history and API keys, which software uses to access other services. The researchers didn’t need to persuade the model to reveal anything.

AIs with excessive agency have more power than their jobs require: tools they don’t need, permissions that go beyond their task, or freedom to act without checking. The cause here is irrelevant.

An injection prompt, a bug, or a model that simply gets it wrong all lead to the same result. The AI will do something destructive eventually if it has the

In July 2025, SaaStr founder Jason Lemkin reported that

, despite instructions not to make changes. The agent initially said the data couldn’t be restored, though recovery later proved possible. Jason found that telling it to leave the database alone hadn’t removed its ability to delete it.

Few companies make AI from scratch, and fewer do it every year. According to

, 53% purchased AI models in 2024, which increased to 76% in 2025.

More often than not, companies download models from hubs like Hugging Face, train them further on datasets other people collected, and plug in add-ons and code packages written by strangers.

Each of those parts is a way in. If one is tampered with, the problem ships inside your product.

Hugging Face’s public model repositories grew from

between January 2026 and August 2026. In July 2026 though, OpenAI’s models got around controls meant to keep them off the internet during internal security testing and

. In fact, one agent recovered 14 publicly exposed access credentials, checked that they worked, and shared them with other agents. The agents went on to exploit flaws that let them run code on Hugging Face’s servers.

“We are placing stricter requirements on alignment throughout a model’s lifecycle and creating more isolated sandboxes, restricting internet access, and further controlling access to model weights,” says the OpenAI report.

A poisoned AI learns from corrupted data. This could be the examples it was fine-tuned on, or a knowledge base it searches for answers. The model still looks like it works; it just learns the wrong lessons, and sometimes it learns to misbehave only when it sees a specific trigger phrase.

The phrase will pass every test you give it until someone uses it.

Also, it's really hard to undo. Poisoning isn't a bug you can patch. If your data is wrong, you might need to recheck it, retrain the model, or replace it entirely.

In October 2025, researchers at Anthropic, the UK AI Security Institute, and the Alan Turing Institute showed that

whenever it encountered a particular trigger. The same number worked across all four model sizes tested, even though the largest trained on more than 20 times as much clean data.

When AIs don't have any limits on how much work they can do or how much they can cost, their consumption is considered to be “unbounded.” The majority of AI services charge per use, so an attacker could run up your bill or build a copy of your model.

OWASP calls the core problem “cost asymmetry.” A short, cheap request can trigger expensive computation on your side.

In May 2024, Sysdig's Threat Research Team discovered a new attack called “

.” A group of attackers targeted 10 cloud-hosted LLM services using stolen credentials. They got in through a vulnerable version of Laravel, then they figured out what the credentials could do and any quotas, with the obvious aim of selling access. A lot of logging settings were also queried, probably to avoid detection. According to Sysdig, a worst-case scenario could cost the victim over $46,000 a day.

When an AI produces something false that sounds right, and someone, or something, acts on it, it’s called misinformation. The core risk isn't so much the wrong answer itself as it's that the wrong answer gets trusted and used.

The incident record suggests that practitioners weren't as worried about misinformation as they should have been. According to the 2026 edition's opening letter, voters put it near the bottom, but according to real-world incidents, it's near the top.

In 2025, Deloitte Australia delivered a review of welfare IT systems under an A$440,000 government contract. University of Sydney

and a fabricated quote from a federal court judgment. The revised report disclosed that Deloitte had used Azure OpenAI GPT-4o in its methodology, and the firm agreed to repay the final installment. This was, unfortunately, an assurance review.

AI applications give the model instructions and background information that users don’t normally see. That can include the system prompt, internal policies, descriptions of available tools, and rules about who can use them. A hidden context exposure occurs when the model reveals that information to someone.

OWASP expanded this entry from “system prompt leakage” in 2026 because the system prompt is only part of what can escape. The danger depends on what you’ve put there. A leaked tone-of-voice guide is mildly embarrassing, but a leaked API key gives someone access to your confidential database.

In February 2023, users got

. One

, who claimed to be an OpenAI developer and asked for the instructions so he could configure the model. Bing disclosed rules governing its searches, responses, and safety behavior, along with its internal name, Sydney. Among the revealed instructions was one telling it to keep those instructions confidential.

When an AI uses vector search to find answers in your company’s documents, it doesn’t search the text directly. The documents are converted into “embeddings,” which are long lists of numbers that capture what each passage means, and stored in a vector database. A question gets converted the same way, and the system pulls the passages whose numbers sit closest.

OWASP sums up the four ways it fails: poisoning makes the system wrong, inversion makes it leak, jamming makes it go silent, and broken access control makes it hand anything to anyone.

The numbers aren’t the safe abstraction they look like. The stored embeddings can be turned back into text, and one method recovered

. So a leaked “embeddings-only” backup can expose the documents’ contents, too.

In research presented at USENIX Security 2025, researchers showed that one carefully crafted document could stop an AI from answering a particular question. They added it to the collection the AI searched. When the AI found it, it could say it didn’t have enough information or that answering would be unsafe. The document didn’t need to tell the AI to ignore its rules. This is called “

.”

Whenever an application passes AI output to another system without verifying whether it is safe for use there, it's improperly handling LLM output.

The entry also covers the insecure code that AI coding assistants generate at scale. Every line an assistant writes, therefore, is output too.

In 2025,

how Sourcegraph’s Amp coding assistant could leak chat content simply by displaying an image. He used prompt injection to make Amp include private information in an image’s web address. The application then automatically fetched that image, sending the information to his server. The output-handling failure was that automatic request—the text the model generated became a connection to an outside server, carrying private data with it.

We assume every risk above will eventually land, and we design so it can't do much when it does. Our CISO, Kyle Polley, walked through how in a

We built Numbat proactively, for a reason Polley sums up in one line: “The more autonomy you give an agent, the more risk there is.”

No LLM makes an application secure on its own—models can still mistake content they should read for instructions they should follow. The defenses that look strong in standard tests can also fold under pressure.

A better question is which

is most secure for your use case. That means limited permissions, credentials kept away from the model, human approval for risky actions, and testing by people who know your defenses.

LLM vulnerabilities are weaknesses that let an AI system be tricked, leak data, or cause damage, whether through an attacker or its own mistakes.

The ten major risks are prompt injection, sensitive information disclosure, excessive agency, supply chain, data and model poisoning, unbounded consumption, misinformation, hidden context exposure, vector and embedding weaknesses, and improper output handling.

A safer option for some things, but not by default. You have more control over data handling if you run a model on your own infrastructure or in a cloud environment. There's no automatic way to prevent prompt injections, excess agency, poisoning, or misinformation.

As part of self-hosting, you’re also responsible for the model you download, including the supply chain risks and the infrastructure it requires.
