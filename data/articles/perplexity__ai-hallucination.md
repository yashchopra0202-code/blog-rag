---
url: https://www.perplexity.ai/hub/blog/ai-hallucination
title: How to Spot AI Hallucinations: 7 Red Flags
site: perplexity
date: 2026-09-01
scraped_at: 2026-09-04T21:16:26+00:00
---

Learn seven signs of AI hallucinations, why models invent facts, and a five-minute checklist for verifying citations, claims, dates, and sources.

Reliable AI answers connect claims to evidence. Hallucinations can create the appearance of that connection through polished writing, but the precise details and citations will fail under inspection.

Take a hypothetical answer that cites the World Economic Forum’s “2026 Enterprise AI Accuracy Index” and claims that 68% of AI-generated reports contain a factual error. The organization is real. The report and statistic are invented. It sounds researched because the language is precise and anchored by a credible attribution.

An AI hallucination happens when a model fills in the blanks with information that’s false, unsupported, or inconsistent with the rest of its answer. Some errors are obvious, such as a citation to a paper that doesn’t exist. Others hide in otherwise credible-looking answers: a date is off by a year or the explanation begins with a false premise.

Language models build answers by estimating which words are most likely to come next, based on patterns learned during training. With enough context and reliable information, that process can produce remarkably useful answers. But when context is limited or reliable sources are hard to find, the model can fill a gap with something that only

plausible.

That risk increases with obscure or recent topics, ambiguous prompts, conflicting information, and questions built on false assumptions. When the available evidence runs out, the response may continue in the same confident, coherent voice.

How models are evaluated matters, too. Many benchmarks emphasize whether a model produces the correct answer, giving less attention to whether it recognizes when a question is unanswerable or the evidence is insufficient.

suggests that even leading language models still struggle to recognize when they don’t have enough information to give a reliable answer. When it doesn’t reliably flag uncertainty, it may produce a plausible-sounding answer instead of asking for clarification.

Hallucination remains possible across generative AI systems, which makes it hard to name one platform as the worst offender. Results change depending on the task, the model version, and whether the system can check current sources.

The impact of a hallucination depends on where the answer goes next. A made-up detail in a brainstorm may waste a few minutes. A fabricated legal citation, medication dose, financial figure, or security instruction can lead to a much more serious mistake. NIST calls these outputs “

” and identifies them as a risk that requires context-appropriate testing, monitoring, and controls, especially where errors could cause significant harm.

Brainstorming or early exploration

A weak idea sends the work in the wrong direction

Verify any factual details before using them.

Published or shared factual content

Readers receive an incorrect statistic, quotation, or attribution

Complete the

and open every important citation.

Time-sensitive research

Old prices, laws, features, or leadership information shape the answer

Confirm the claim with a current primary source.

Legal, medical, financial, or security decisions

An error causes harm, loss, or liability

Review the original evidence, add independent corroboration, and involve a qualified expert.

When an AI answer seems unreliable, start with three things: traceability, consistency, and currency. Follow the claim back to its source, check that the details line up, and make sure the information is current enough for the question.

Traceability

The source cannot be verified

Search the exact title, then check the publisher, author record, or digital object identifier (DOI).

Traceability

The source is real but misused

Find the exact quotation, statistic, or conclusion and read its surrounding context.

Traceability

An exact number has no clear origin

Trace it to the original study and check the sample, timeframe, and method.

Consistency

Real details have been combined incorrectly

Separate the claim into entity, action, and date or version; verify each part.

Consistency

The answer accepts a questionable premise

Confirm that the report, event, person, or product exists.

Consistency

Rewording changes the core facts

Ask again using neutral language, then compare the verifiable details.

Currency

A current claim relies on old information

Check when the source was updated and find the latest primary source.

Traceability starts with the receipts. If a claim matters, you should be able to find the source and confirm it says the same thing.

A citation cannot support an answer if the source itself cannot be confirmed. The URL may be broken for a temporary reason, so one failed link is not proof of a hallucination. The stronger warning sign is a source that leaves no trace: the publisher has no record of the article, the digital object identifier (DOI) resolves to a different paper, or the named author has no documented connection to the work.

Models can invent convincing titles, authors, journals, and reports, often with just enough detail to look legitimate.

Search the exact title in quotation marks. Check the publisher’s archive and the author’s publication record. For academic work, enter the DOI at

and make sure it takes you to the cited paper.

A working citation does not prove that the sentence beside it is accurate. A source may be credible and relevant yet fail to contain the quoted language, reported figure, or conclusion the answer attributes to it. It may also support a narrower finding than the answer suggests.

This is a false-attribution problem, not a source-existence problem: the evidence is real, but the connection between the evidence and the claim is wrong.

: Open the cited page and locate the exact statistic, quotation, or conclusion. Read the surrounding context, then ask whether the source supports the claim as written, not merely the general topic.

Exact details have a way of sounding researched. A figure such as “36.4%” implies a measurement, a dataset, and a method. The more exact the claim, the easier it should be to trace back to a documented measurement.

Pay close attention to percentages, survey results, prices, rankings, revenue figures, and study findings presented with numerical precision. A reliable source should make clear who collected the information, when they collected it, what population or dataset they used, and how they calculated the result.

Trace the number to its original source. Confirm the date, sample or dataset, methodology, and the figure itself. If the source reports a different scope, timeframe, or calculation, the AI answer may be overstating what the data shows.

A reliable answer should hold together when its individual parts are checked. A claim can fail because the facts have been assembled incorrectly, not because every individual fact is false.

An answer can use facts that are individually real and still describe something that never happened. A model may assign a real quote to the wrong researcher, attach a feature from one product release to another, or combine a company announcement with a leadership change that occurred months later.

These are relationship errors. The names, dates, products, and sources may all be legitimate; the problem is that they do not belong together in the way the answer claims.

Split the claim into its essential parts: the person or organization, the event or feature, and the date or version. Verify each part separately, then confirm that the original source connects them.

Models often follow the direction set by a prompt. A false premise can set the entire response on the wrong track. Rather than challenge a nonexistent report, imagined event, or incorrect assumption, a model may build an answer around it. The result may be detailed and coherent, even though its starting point was wrong.

Pull out the main assumption and verify it on its own. Confirm that the report, event, person, or product exists before evaluating what the answer says about it.

Rewording a question can change the style, level of detail, or examples in an answer. The core facts should remain stable.

If one version names a different author, date, total, or citation, the model may be filling in missing information rather than drawing from a reliable source. Different wording should not change verifiable facts. When it does, treat the mismatch as a lead to investigate rather than proof that either response is false.

Ask the same factual question again using neutral language. Compare only the details that can be verified, then check those details against an independent source.

Current questions need current evidence. Information can be historically accurate and no longer usable for a current decision.

Product features, laws, prices, leadership roles, and research findings can change quickly. An answer based on older information may sound polished and include real facts while missing an important update.

This is especially easy to overlook when the source itself is credible. A credible source still needs to be recent enough for the question at hand.

See when the source was published and last updated, then confirm the claim with a current primary source such as official documentation, a government database, a company announcement, or the original research.

You do not need to verify every sentence before deciding whether an AI answer is useful. Start with the claims that carry the most weight, then work through the five checks below.

Highlight the statistics, quotations, dates, named sources, product capabilities, recommendations, and high-stakes guidance.

Open the linked sources. Confirm that each source exists and matches the title, author, publisher, and date in the answer.

Find the exact detail in the source. Check that the source supports the claim’s wording, scope, and level of certainty.

Prefer primary evidence: original research, official documentation, government records, court filings, company announcements, or source data. For time-sensitive claims, confirm that nothing newer has changed the answer.

Rephrase the question without assumptions. Compare only verifiable details across the two answers, then independently check any conflicts or new claims.

Perplexity

and links claims to sources in the answer. Those citations give readers a direct path to inspect the evidence, including whether a source exists, supports the claim beside it, and is recent enough for the question. Citations make verification easier; they do not remove the need to review consequential claims.

For questions that use web search, Perplexity presents numbered citations that link back to the sources used in the response. That makes it easier to apply the first two red flags in this guide: verify that a source exists, then check that it supports the associated claim.

Because search quality depends on more than retrieving links, Perplexity designed a two-stage post-training process. The first stage develops product behaviors such as following instructions, using tools, maintaining consistency, and recognizing when reliable evidence is unavailable; the second uses harder search tasks to improve evidence use and tool efficiency.

For verifiable tasks, Perplexity evaluates factual accuracy alongside citation quality and other product requirements. For open-ended requests such as rewriting or planning, evaluation instead focuses on whether the model followed instructions, preserved meaning, and completed the requested task. This distinction matters because a fluent answer can be well written without being factually reliable.

More retrieval is not automatically better. Perplexity’s

describes training search agents to solve multi-step questions while balancing answer quality with tool-use efficiency. The goal is to gather enough evidence to support the answer without adding unnecessary steps that can introduce errors or distract from the question.

. Current retrieval, post-training, structured evaluation, and disciplined search reduce the risk of hallucination. Visible citations make the remaining uncertainty easier to inspect, and ongoing feedback helps the system improve.

Trust an AI answer only as far as you can trace its most important claims back to solid evidence. For decisions with real consequences, open the sources, read beyond the quoted line, and ask a qualified expert to weigh in when needed.

Yes. Any current generative AI system can produce an inaccurate or unsupported answer. Risk changes with the model version, task, prompt, source access, and testing method. A model may handle familiar facts well and struggle with recent or obscure information.

Better prompts help lower the risk by adding context, defining terms, and removing faulty assumptions. They work best alongside reliable sources, citations, verification, and human review. Even a carefully written prompt cannot guarantee a factual response.

Yes. The stakes rise when an unsupported answer influences healthcare, law, finance, cybersecurity, education, or another consequential decision. A made-up brainstorming detail may waste a few minutes; a fabricated dosage or legal citation can cause much more serious harm.

Start with details that are both easy to verify and capable of changing the answer: citations, quotations, statistics, dates, names, and current claims. Give extra attention to any fact that could influence an important decision.
