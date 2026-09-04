---
url: https://www.anthropic.com/news/enterprise-frontier-safeguards
title: Developing Enterprise Frontier Safeguards with our customers
site: anthropic-news
date: 
scraped_at: 2026-09-04T13:11:27+00:00
---

Today we’re announcing Enterprise Frontier Safeguards (EFS), a solution that combines the privacy of zero data retention (ZDR) with state-of-the-art safeguards for detecting misuse. EFS works by storing data in cloud infrastructure controlled by the customer, not Anthropic. EFS will be rolling out to customers in phases, starting later this fall. To make the transition smooth, eligible customers will receive ZDR on Fable 5 and Fable 5.1 until EFS is ready.

We developed EFS in close collaboration with more than 100 customers in industries like financial services, healthcare, manufacturing, telecom, law, retail, and the public sector, and with our cloud partners at Amazon Web Services, Google Cloud, and Microsoft Azure.

EFS will be supported on Claude Code, Claude Enterprise, the Claude Platform, Amazon Bedrock, Claude Platform on AWS, Google’s Agent Platform, and Microsoft Foundry.

Mythos-class models, like

, represent a major increase in intelligence and agentic capabilities. However, with that increase comes the potential for both misuse and autonomous misbehavior.

Over the last few months, we’ve seen substantial evidence of attempted misuse of AI models. These range from typical forms of abuse, such as fraud, to sophisticated cyberattacks, which can include agents autonomously engaging in destructive behavior. Some of these instances involve theft or misappropriation of enterprise customers’ credentials, which are difficult to detect without the ability to monitor traffic and detect abnormal behavior.

Furthermore, because the

can involve many tasks spread across multiple sessions and accounts, it is not sufficient to run automated analysis on each interaction separately and then instantaneously discard the data. Effective detection requires storing data for a meaningful period of time so that it can be correlated across time and accounts.

For this reason, we introduced 30-day data retention starting with Fable 5. This policy was not motivated by a desire to train on enterprise data: Anthropic has never trained on enterprise data without explicit permission, and never will.

The enterprises we worked with generally understood the safety and security value of data retention, but many–especially in regulated industries–found it difficult to use models with data retention. We therefore sat down with customers to design a solution that could provide the best of both worlds: the privacy of ZDR and the safety allowed by monitoring across time and accounts.

We built Enterprise Frontier Safeguards with feedback from the experts who will use it every day: security, product, compliance, and delivery teams. One of the groups we worked with was the Analysis and Resilience Center for Systemic Risk (ARC), whose members include the chief information security officers of the largest US banks, including Goldman Sachs, Morgan Stanley, Citi, Bank of America, and Wells Fargo.

We also worked with leaders at companies such as Comcast, KPMG, Mastercard, Salesforce, and Visa, to make sure the design held up across industries. Our conversations spanned a quarter of the Fortune 100, every US global systemically important bank, and virtually every regulated industry.

Here is what we heard from this wide range of customers, and what we built into EFS to address these common concerns:

Enterprises have long applied monitoring for insider risk, and now want help upleveling monitoring for agents. Their concerns were about Anthropic’s automated monitoring systems meeting their regulatory standards.

When monitoring detects a pattern that needs attention, those signals are sent directly to customers so they can review what the automated systems detected.

It’s a lot of work for enterprises to add another “trusted data vendor” for a number of reasons. They need to notify all of their customers who these vendors are and update contracts. They also have internal requirements for safely storing and auditing data, given its high level of sensitivity. Because of these concerns, we architected EFS so that customers have the ability to store data on their existing cloud infrastructure.

Customers want the ability to have their data live in infrastructure they control, under their own encryption keys, access policies, and audit logging. Activity data used for monitoring can be stored in the customer’s own cloud account (such as Amazon S3, Azure Blob Storage, or Google Cloud Storage).

Even as automated review is becoming more effective, a person looking at a flag still adds value by confirming real misuse and clearing false positives. But what we heard from many customers, especially those in regulated industries, is that the person doing that review needs to be one of their own. Many operate under rules that tightly govern who may see certain information—privileged legal material, non-public information, drug-safety reports. Their teams are already trained and cleared for that work.

Customers want protection against cyberattacks, and appreciate that these can be difficult to detect if they unfold across many sessions and accounts. With EFS, automated systems analyze a rolling window of traffic for signals of serious misuse, including attempts to develop offensive cyber or biological capabilities and signs of stolen or leaked credentials. Those flags go directly to the customer and their people take it from there – no human review by Anthropic employees is required.

These controls are designed to work the same way whether you access Claude directly from Anthropic or through a cloud partner. Customers on Amazon Web Services, Google Cloud, and Microsoft Azure will get equivalent controls, with their activity data stored in their own cloud account, in the environment they already trust. We’re also working to support third-party offerings that serve customers that are eligible for Enterprise Frontier Safeguards.

Customer-owned storage, Customer-Managed Encryption Keys, and fully automated review are each opt-in, so you enable the ones your organization needs. None of them change model behavior, API pricing, or rate limits.

Anthropic doesn’t charge for Enterprise Frontier Safeguards. If customers elect to store their data in their cloud account, their cloud provider bills them for that storage, as well as reads, writes, and data egress fees, the same way it bills any other resource.

Enterprise Frontier Safeguards will roll out to customers in phases, with the goal of making it broadly available later this fall. To request access to Enterprise Frontier Safeguards, please complete this

.

On July 30, we reported three incidents in which Claude models gained unauthorized access to real computer systems. We are conducting an in-depth analysis of both incidents, and planning to work with METR for an independent review. In the meantime, we’re sharing some of the changes we’ve made over the past month.

We’re opening a research preview of the Model Hardware Standard (MHS), a shared specification for AI agents to safely operate physical devices, to a first group of scientific research labs and advanced manufacturers.

Starting today, 10,000 scientists around the world can get Claude at no cost to start. Verified principal investigators qualify for a Claude Team subscription plan and then add their research team to Standard seats for free, or Premium seats for $15 per month, for up to a year.

Today we’re announcing Enterprise Frontier Safeguards (EFS), a solution that combines the privacy of zero data retention (ZDR) with state-of-the-art safeguards for detecting misuse. EFS works by storing data in cloud infrastructure controlled by the customer, not Anthropic. EFS will be rolling out to customers in phases, starting later this fall. To make the transition smooth, eligible customers will receive ZDR on Fable 5 and Fable 5.1 until EFS is ready.

We developed EFS in close collaboration with more than 100 customers in industries like financial services, healthcare, manufacturing, telecom, law, retail, and the public sector, and with our cloud partners at Amazon Web Services, Google Cloud, and Microsoft Azure.

EFS will be supported on Claude Code, Claude Enterprise, the Claude Platform, Amazon Bedrock, Claude Platform on AWS, Google’s Agent Platform, and Microsoft Foundry.

Mythos-class models, like

, represent a major increase in intelligence and agentic capabilities. However, with that increase comes the potential for both misuse and autonomous misbehavior.

Over the last few months, we’ve seen substantial evidence of attempted misuse of AI models. These range from typical forms of abuse, such as fraud, to sophisticated cyberattacks, which can include agents autonomously engaging in destructive behavior. Some of these instances involve theft or misappropriation of enterprise customers’ credentials, which are difficult to detect without the ability to monitor traffic and detect abnormal behavior.

Furthermore, because the

can involve many tasks spread across multiple sessions and accounts, it is not sufficient to run automated analysis on each interaction separately and then instantaneously discard the data. Effective detection requires storing data for a meaningful period of time so that it can be correlated across time and accounts.

For this reason, we introduced 30-day data retention starting with Fable 5. This policy was not motivated by a desire to train on enterprise data: Anthropic has never trained on enterprise data without explicit permission, and never will.

The enterprises we worked with generally understood the safety and security value of data retention, but many–especially in regulated industries–found it difficult to use models with data retention. We therefore sat down with customers to design a solution that could provide the best of both worlds: the privacy of ZDR and the safety allowed by monitoring across time and accounts.

We built Enterprise Frontier Safeguards with feedback from the experts who will use it every day: security, product, compliance, and delivery teams. One of the groups we worked with was the Analysis and Resilience Center for Systemic Risk (ARC), whose members include the chief information security officers of the largest US banks, including Goldman Sachs, Morgan Stanley, Citi, Bank of America, and Wells Fargo.

We also worked with leaders at companies such as Comcast, KPMG, Mastercard, Salesforce, and Visa, to make sure the design held up across industries. Our conversations spanned a quarter of the Fortune 100, every US global systemically important bank, and virtually every regulated industry.

Here is what we heard from this wide range of customers, and what we built into EFS to address these common concerns:

Enterprises have long applied monitoring for insider risk, and now want help upleveling monitoring for agents. Their concerns were about Anthropic’s automated monitoring systems meeting their regulatory standards.

When monitoring detects a pattern that needs attention, those signals are sent directly to customers so they can review what the automated systems detected.

It’s a lot of work for enterprises to add another “trusted data vendor” for a number of reasons. They need to notify all of their customers who these vendors are and update contracts. They also have internal requirements for safely storing and auditing data, given its high level of sensitivity. Because of these concerns, we architected EFS so that customers have the ability to store data on their existing cloud infrastructure.

Customers want the ability to have their data live in infrastructure they control, under their own encryption keys, access policies, and audit logging. Activity data used for monitoring can be stored in the customer’s own cloud account (such as Amazon S3, Azure Blob Storage, or Google Cloud Storage).

Even as automated review is becoming more effective, a person looking at a flag still adds value by confirming real misuse and clearing false positives. But what we heard from many customers, especially those in regulated industries, is that the person doing that review needs to be one of their own. Many operate under rules that tightly govern who may see certain information—privileged legal material, non-public information, drug-safety reports. Their teams are already trained and cleared for that work.

Customers want protection against cyberattacks, and appreciate that these can be difficult to detect if they unfold across many sessions and accounts. With EFS, automated systems analyze a rolling window of traffic for signals of serious misuse, including attempts to develop offensive cyber or biological capabilities and signs of stolen or leaked credentials. Those flags go directly to the customer and their people take it from there – no human review by Anthropic employees is required.

These controls are designed to work the same way whether you access Claude directly from Anthropic or through a cloud partner. Customers on Amazon Web Services, Google Cloud, and Microsoft Azure will get equivalent controls, with their activity data stored in their own cloud account, in the environment they already trust. We’re also working to support third-party offerings that serve customers that are eligible for Enterprise Frontier Safeguards.

Customer-owned storage, Customer-Managed Encryption Keys, and fully automated review are each opt-in, so you enable the ones your organization needs. None of them change model behavior, API pricing, or rate limits.

Anthropic doesn’t charge for Enterprise Frontier Safeguards. If customers elect to store their data in their cloud account, their cloud provider bills them for that storage, as well as reads, writes, and data egress fees, the same way it bills any other resource.

Enterprise Frontier Safeguards will roll out to customers in phases, with the goal of making it broadly available later this fall. To request access to Enterprise Frontier Safeguards, please complete this

.
