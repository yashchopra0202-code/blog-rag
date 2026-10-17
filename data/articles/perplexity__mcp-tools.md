---
url: https://www.perplexity.ai/hub/blog/mcp-tools
title: What Are MCP Tools and How Do AI Models Use Them?
site: perplexity
date: 2026-10-14
scraped_at: 2026-10-17T08:10:43+00:00
---

Learn what MCP tools are, how AI models find and call them through MCP servers, and how to use them safely.

Contents

MCP tools are functions an AI model can call to perform a task outside the conversation. For example, search your notes or query a database. Each tool sits on an MCP (Model Context Protocol) server and has a name and a short description that help the model decide when to use it.

The term "MCP tool" is used in other ways too. In everyday use, people say "MCP tools" when they mean MCP servers (the applications that offer tools) or the directories that list those servers. MCP Tools is also the name of a command-line program for listing and calling the tools on an MCP server.

This guide is about the protocol functions, not servers, directories, or command lines. It explains what a tool consists of, the kinds of tools servers offer, and how tools differ from resources, prompts, and function calling. It then walks through the steps a model takes to use a tool, and closes with the most common problems related to their use.

An MCP tool is a function that lets AI models complete tasks with other software applications. For instance, my AI agents and workflows use MCP tools to draft emails in Gmail (

), create Trello cards (

), and pull live search results from DataForSEO (

), to name just a few.

Software apps often offer multiple MCP tools on their MCP servers. For example, the Trello MCP server currently has 14 MCP tools that enable AI models to read and update boards, lists, checklists, cards, and more.

And because MCP standardizes how tools are described and offered, any AI app that supports the protocol can use the same MCP tool.

Every MCP tool comes with three things:

Some tools add extra metadata: a display name, a description of the results they return (an output schema), and annotations about how the tool behaves.

The AI model never sees the code behind a tool. It works from what the tool says about itself, so a vague name or description leads the model to pick the wrong tool.

MCP tools fall into four groups by what they do:

Besides MCP tools, an MCP server can offer two other types of building blocks, which the protocol calls primitives: resources and prompts.

For example, GitHub's official MCP server offers:

The difference is what each one does and who decides when to use one: you, the AI app you're working in (e.g., Perplexity), or the AI model running inside that app.

An AI model uses an MCP tool in five steps: discovery, tool selection, invocation, results, and error handling. Your AI app passes everything between the model and the server.

Say you ask your AI app to check your Trello "This week" list and draft an email to your editor with an update. Here's what happens end to end:

The key point is that the model chooses tools from their descriptions alone, and your AI app does all the talking to servers.

Problems with MCP tools come down to four things: how many tools are connected, how they're named and described, how much data they return, and which servers they come from.

Here's what each problem looks like and what helps:

Every tool definition sits in the model's context window before you've asked anything, and tool selection gets worse as the list grows.

Connect only the servers a task needs, and turn off unused tools where your AI app allows it. Example: GitHub's MCP server lets you enable only the groups of tools (toolsets) you need.

The model calls the wrong tool, or the right one with the wrong inputs, because two descriptions sound alike or one says too little.

Provide clear, specific names and descriptions, ideally with an example of when to use the tool. If a server's tools keep misfiring, MCP Inspector, the official testing tool, shows exactly what each tool says about itself.

Two servers each offer a tool called

, and there's no telling which one a call is meant for.

Prefix tool names with the server's name. Example: Trello's server (

).

A tool returns more than the task needs, such as a whole email thread with its formatting, and crowds the model's context.

Use tools that offer compact formats. Example: Gmail's

tool description recommends plain-text format "to prevent context exhaustion."

A careless or malicious server could use tool calls to pull data out of your conversation.

Connect servers only from sources you trust, and keep approvals on for tools that change things or send data out.

MCP tools need your approval because, without it, the AI model could make changes you didn't intend or share sensitive data with a server you don't control.

A misread request or a vaguely described tool can trigger the wrong action. Every call also sends some of your information to a server.

That's why the protocol expects AI apps to keep a person in the loop, with the ability to deny any tool call.

Here's a practical way to sort tools by how much checking they need:

Perplexity works with MCP tools in both directions: it can use tools from MCP servers you connect, and it offers its own tools to other AI apps.

No, MCP isn't just tool calling. Tool calling is how the model asks for a tool, and MCP is how the AI app finds tools and routes each call to the server that runs it.

Tool calling (also called function calling) is the AI model's part of the job: the model sees a list of tools and replies with a request to run one. With tool calling alone, each AI app has to define and run every tool itself.

MCP lets tools live on servers, so any AI app that supports MCP can offer them to its model and send the model's requests to the right server.

No, MCP won't replace APIs, because

MCP tools often sit on top of existing APIs, and when the model calls a tool, the MCP server typically makes an API request.

MCP tools work in AI assistants such as Claude, ChatGPT, and Perplexity, and in development tools such as Visual Studio Code and Cursor. The

names these and notes that many other apps do too.

No. The AI model doesn't need to support MCP because your AI app handles the protocol. It connects to servers, passes their tools to the model, and sends the model's tool requests back to the right server. The model needs only to support function calling.

No, MCP is still under active development. Its maintainers released a

in July 2026 and published an

in August 2026, which includes work to let servers reveal their tools gradually as a conversation narrows.
