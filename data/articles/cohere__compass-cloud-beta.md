---
url: https://cohere.com/blog/compass-cloud-beta
title: Compass is coming to the cloud
site: cohere
date: 
scraped_at: 2026-09-26T08:57:33+00:00
---

is Cohere’s retrieval platform for developers building AI applications with their enterprise data. It surfaces the most relevant information from your company’s corpus for use in retrieval-augmented generation (RAG), search, and agentic workflows. Now, Compass is entering private beta as a managed offering -

Compass was built for builders. It provides the retrieval foundation that developers can freely configure around their data and workflow requirements. Instead of assembling and operating the stack themselves, teams access Compass through its APIs, MCP server, or

to shape their desired end user experience.

Until now, Compass has principally powered retrieval for

, Cohere's enterprise agent workspace, including its document libraries and MCP ecosystem. We have also shipped Compass into highly secure, self-hosted environments for partners in regulated industries whose workloads cannot be offloaded to SaaS.

Customer demand for a managed option has been clear and consistent: teams want Compass' best-in-class retrieval capabilities, but many do not want the operational overhead that comes with self-hosting.

We’ve listened to those calls. Compass Cloud expands Compass to a broader market. It lets Cohere manage the full pipeline

model inference, so that our customers can focus even more on building. In parallel, self-hosted deployments remain available for privacy-constrained projects.

We're working with a limited number of enterprise teams as beta partners. Interested?

Search and retrieval have improved, but enterprise performance is no longer defined by relevance and latency for a single query. As retrieval becomes key supporting infrastructure for generative AI and agents, three developments are changing the requirements:

Compass exists to address each of these: 1) by providing relevant, governed context for generative workloads; 2) supporting both agentic and conventional search applications; and 3) consolidating the core retrieval stack into an integrated enterprise platform.

Compass packages document processing and retrieval into one configurable service. Teams can access a single interface instead of integrating and operating separate services.

Access out-of-the-box connectors for your file sharing and cloud storage workspaces, such as SharePoint, OneDrive, and Google Drive. Quickly access the content you need with Compass’ near-universal data compatibility — multilingual, multimodal, and file format-agnostic.

Turn complex documents into searchable, structured data. Compass transforms multimodal enterprise files into AI-ready content, applying the right parsing strategy to each document and using vision processing only where it adds value, reducing unnecessary model usage.

Capture meaning and exact terminology. Compass generates dense and sparse representations together, so search can match both semantic intent and domain-specific language across text and multimodal content.

Keep your source files, parsed content, and embeddings as separate records, so a new embedding model can be adopted without crawling and uploading the same content again. At search time, they sit in one index with their metadata, reducing the need to keep each system in sync.

Combine search strategies in one request. Semantic, sparse, and keyword search can run independently or together, balancing recall and precision. Permissions are enforced during retrieval rather than left to the application.

Send stronger evidence to the model. Cohere’s best-in-class reranker identifies the most relevant passages from a broad candidate set, reducing irrelevant context and the tokens required for generation.

Enforce multi-tenant access control and document-level permissions during retrieval, so applications don’t have to filter results themselves. In Compass, retention policies expire content automatically and prevent deleted documents from being resynced.

The core objective of Compass is simple: improve the relevance of information surfaced for enterprise knowledge applications, be that a RAG pipeline or an autonomous agent. That quality is rooted in Cohere's best-in-class search and document-processing models together with Compass's hybrid search: lexical, sparse, and dense retrieval, then rerank.

The figure below is one instance of the accuracy gain over traditional or standalone search infrastructure on a representative financial-industry RAG workload: embed a query, retrieve presentation materials from an index, and score the top results. On High Finance, a Cohere-built investment-banking benchmark, Compass achieved a 14-16 point improvement on Azure Search (from 64.8 to 81.1). A gap of this size can be the difference between an unsatisfactory answer and a great one for the end user.

Users can upgrade their search performance with Compass Cloud in two key ways, depending on how they want to integrate retrieval into their application:

Agentic retrieval is an emerging approach at the intersection of large language models and information retrieval. Rather than relying on a single query-and-response retrieval step, an agent can decide what to look for, search for relevant information, evaluate the results, and refine its search before answering.

This is especially useful for tasks that cannot be resolved with a single lookup. With the Compass MCP server, agents can progressively narrow the retrieval corpus, reducing unnecessary context and making complex retrieval tasks faster and more token-efficient.

We’re opening this private beta for teams building retrieval-heavy and agentic applications.

Beta participants get hands-on support from the engineering team, early access to the cloud deployment, and direct influence on the roadmap.

We’re also running a live session on

on

with Cohere’s engineering and product leadership on where enterprise search goes next.

Written By

Cohere Team

Tags

AI isn’t a shortcut.

It’s how business gets ahead.
