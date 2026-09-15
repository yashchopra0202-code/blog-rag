---
url: https://www.perplexity.ai/hub/blog/portable-computer-for-windows-is-here
title: Portable Computer for Windows is here
site: perplexity
date: 2026-09-14
scraped_at: 2026-09-15T09:06:02+00:00
---

Portable Computer for Windows keeps sensitive work local, runs recurring tasks and long workflows without using credits.

Contents

Last month, we brought the full power of Perplexity Computer to a local machine for the first time.

runs a local AI model on a user’s own hardware. It works across sensitive files and local tools without sending that work to the cloud or consuming credits.

Today, Portable Computer is available in the

. This adds Computer’s local agent harness and orchestrator to compatible Windows PCs, where people need powerful AI for complex tasks and long-running workflows.

With scheduled tasks and desktop tool connections, users can run recurring workflows and use AI with Windows tools on their own hardware. When a task needs current information or advanced reasoning, they can include results from Perplexity Search or 15+ frontier models.

We introduced Portable Computer in August for NVIDIA DGX Spark. This latest release extends Portable Computer to Windows PCs with supported eligible

and NVIDIA

Before that, Perplexity’s

brought Computer’s cloud agents to the Windows desktop, where they could work across local files, connected apps, and the web.

Portable Computer runs the model, agent harness, orchestrator, and scheduler entirely on the Windows device.

This keeps files, queries, and agent activity on the PC. When people run work on device, it doesn’t consume Computer credits, making long-running workflows more practical.

Portable makes it possible for teams to schedule tasks to run with a local model on their Windows device. They can set recurring workflows like analyses or file processing to run on their own hardware instead of doing it manually.

One example: A controller at a logistics company schedules Portable to reconcile freight invoices in a permitted folder each morning. Portable matches each invoice against the carrier's local rate sheets and flags duplicate charges, or rates that deviate from contract. Then it generates an exception queue showing the invoice, the discrepancy, and the recommended dispute action.

The invoice and rate data never leave the company's device.

Portable’s local orchestrator can work with Gmail, Outlook, Slack, and GitHub. Portable can also call Perplexity Search and run wide or deep research, then return the findings to the same task.

Portable connects to other desktop applications through local Model Context Protocol (MCP) servers running on the Windows device. This lets the local model use their tools and data as part of an automated workflow while keeping the work on device.

A designer, for example, could connect Portable to a locally installed application through its MCP server. The agent could use that application’s tools to create or revise a file while keeping the model, source files, and application interactions local.

This is broader than local file access. Portable can work with documents, spreadsheets, presentations, PDFs, code, and images stored in permitted folders, then use tools to act on that information.

Portable can bring current information and advanced reasoning into a local task when the work requires it. A user can ask for cited web results using Perplexity Search or work with one of 15+ frontier models for advanced reasoning.

When a task needs to send something from the device to the cloud, Portable first asks for the user’s permission before moving forward.

An engineer can ask Portable to review open pull requests against the local codebase and group them as ready to merge, needs review, blocked, or stale. After the engineer approves the summary and action items, Portable posts them to the team’s Slack channel and tags the DRI for each item.

Portable Computer for Windows is available to Pro and Max subscribers on both individual and enterprise plans through the existing Perplexity app for Windows. On-device inference requires an NVIDIA GeForce RTX or RTX PRO GPUs with at least 24GB of VRAM. Check out the

to learn more.

Download the

, then download the local model you want to use in one click after selecting it in the model dropdown.

Try

today.
