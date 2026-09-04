---
url: https://mistral.ai/news/more-control-over-connectors/
title: Bringing more control over your connectors
site: mistral
date: 
scraped_at: 2026-09-04T13:23:39+00:00
---

Engineering

June 24, 2026

By Mistral AI

4 min read

Thinking

Summary

Today, we are introducing several new capabilities in Connectors for a more secure experience integrating to external enterprise platforms. Starting now, you can use:

(GA) to set connector access per workspace and switch individual tools on or off across an org or workspace

(GA) to prevent impersonation in automated AI workloads that integrate with 3rd-party systems

(GA) allowing users to authenticate to a single connector with multiple accounts

(Public Preview) for end-to-end root cause analysis for MCP connectors

(GA) to reuse your connectors in developer interfaces

(Public Preview) allow for uninterrupted long-running tasks powered by all the tools you need

Async agents are moving into everyday work. For an agent to be trustworthy and useful inside an organization, it needs real enterprise data: CRM records, repositories, inboxes, knowledge bases. Connecting an agent to that data in a demo is easy. Running it in production is where most setups stall.

Production connectivity has a few non-negotiables. A connector should respect two sets of rules at once: the permissions already set in the source platform, and the controls your administrators set in Mistral Studio or Vibe. Automated work should run on behalf of a user or a service account, never impersonate the person who wrote it. When a connection breaks, you should be able to find out why. And an administrator should be able to decide, down to the individual tool, what is available in each part of the organization.

work at two levels: across your teams, and inside each connector.

let you give each team its own connector access. Your finance workspace can reach internal data sources with no open web access, while engineering gets developer tools and the internet. Same directory, different rules per team.

go a step deeper. Inside any connector, turn individual tools on or off for a whole org or one workspace. Block anything that writes data, or one specific action like

on a knowledge base. The connector stays connected; only the tools you approve can run.

handle identity. When you create a key, you choose whether it reaches only a workspace's shared connectors or your private ones too, so an automated job runs with exactly the access it needs. Paired with service accounts, automated work runs as a defined identity, never as the person who wrote it.

let one connector hold more than one login. Connect a personal and a work account to the same connector, set a default, and switch between them per task. Each account is stored and refreshed on its own, so an agent acts in the right one without you standing up a second connector.

tells you exactly where a connection breaks. Point it at an MCP server URL, add OAuth credentials if the server needs them, and run the check. It walks the connection through 11 steps, from reaching the server to opening the MCP session, and logs each one. A failure that used to mean guesswork, like a broken OAuth token exchange, shows up at the exact step it happens.

keep long and scheduled runs from breaking on auth. You declare the connectors a Workflow needs, and the accounts it should run with, right in the Workflow definition; Studio resolves those dependencies when you start a run. Personal credentials stay out of automated work, and a job won't fail halfway because a token expired. A nightly run can pull from a CRM, update a tracker, and read a knowledge base across the whole job without dropping a connection.

bring the same governed access to the coding agent. Type

to pick from local MCP servers and the workspace connectors your admins approved, choose which tools to enable, and start a task. Async agents can reach Outlook, Jira, Notion, Linear, and Confluence under the same rules you set everywhere else.

We're adding connectors continuously. The directory now covers more than 60 integrations, and when the platform you need isn't listed, a custom MCP connector fills the gap.

Knowledge, Data & AI

Atlassian

BigQuery

Box

Google Drive

Notion

SharePoint

Databricks

MDN

Microsoft Learn

Needle

Prisma Postgres

Snowflake

Supabase

Synapse

Machine Learning

DeepWiki

Hugging Face

Jina

Pinecone

Tavily

Communication & Scheduling

Gmail

Google Calendar

Outlook

Outlook Calendar

Slack

Brevo

Clockwise

Fireflies

Work & Customer Operations

Asana

Linear

Monday

Close

HubSpot

Intercom

Salesforce

ServiceNow

Payments & Financial Data

Stripe

PayPal

Square

Plaid

Morningstar

Kensho

Pigment

Analytics & Business Intelligence

Amplitude

Hex

Vantage

Developer Platforms & Infrastructure

GitHub

Cloudflare Developer Platform

Netlify

Sentry

Stytch

Automation & Integration

Apify

n8n

Workato

Zapier

Research, Scientific & Public Data

BioRender

Data.gouv

PubMed

Scholar Gateway

Content & Media Management

Bria

Bright

Cloudinary

Mermaid

Trivago

Website Publisher

Enterprise controls, Connector Credentials, and Connectors in Vibe Code are generally available now. Connectors Playground and Connectors in Workflows are in public preview. All of it is live in Studio.

0%
