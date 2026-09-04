---
url: https://www.anthropic.com/engineering/desktop-extensions
title: Desktop Extensions: One-click MCP server installation for Claude Desktop
site: anthropic-engineering
date: 
scraped_at: 2026-09-04T13:10:41+00:00
---

File extension update

Sep 11, 2025

Claude Desktop Extensions now use the .mcpb (MCP Bundle) file extension instead of .dxt. Existing .dxt extensions will continue to work, but we recommend developers use .mcpb for new extensions going forward. All functionality remains the same - this is purely a naming convention update.

—

When we released the Model Context Protocol (MCP) last year, we saw developers build amazing local servers that gave Claude access to everything from file systems to databases. But we kept hearing the same feedback: installation was too complex. Users needed developer tools, had to manually edit configuration files, and often got stuck on dependency issues.

Today, we're introducing Desktop Extensions—a new packaging format that makes installing MCP servers as simple as clicking a button.

Local MCP servers unlock powerful capabilities for Claude Desktop users. They can interact with local applications, access private data, and integrate with development tools—all while keeping data on the user's machine. However, the current installation process creates significant barriers:

These friction points meant that MCP servers, despite their power, remained largely inaccessible to non-technical users.

Desktop Extensions (

files) solve these problems by bundling an entire MCP server—including all dependencies—into a single installable package. Here's what changes for users:

That's it. No terminal, no configuration files, no dependency conflicts.

A Desktop Extension is a zip archive containing the local MCP server as well as a

, which describes everything Claude Desktop and other apps supporting desktop extensions need to know.

The only required file in a Desktop Extension is a manifest.json. Claude Desktop handles all the complexity:

The manifest contains human-readable information (like the name, description, or author), a declaration of features (tools, prompts), user configuration, and runtime requirements. Most fields are optional, so the minimal version is quite short, although in practice, we expect all three supported extension types (Node.js, Python, and classic binaries/executables) to include files:

There are a number of convenience options

that aim to make the installation and configuration of local MCP servers easier. The server configuration object can be defined in a way that makes room both for user-defined configuration in the form of template literals as well as platform-specific overrides. Extension developers can define, in detail, what kind of configuration they want to collect from users.

Let’s take a look at a concrete example of how the manifest aids with configuration. In the manifest below, the developer declares that the user needs to supply an

. Claude will not enable the extension until the user has supplied that value, keep it automatically in the operating system’s secret vault, and transparently replace the

with the user-supplied value when launching the server. Similarly,

will be replaced with the full path to the extension’s unpacked directory.

A full

with most of the optional fields might look like this:

To see an extension and manifest, please refer

.

The full specification for all required and optional fields in the

can be found as part of our

.

Let's walk through packaging an existing MCP server as a Desktop Extension. We'll use a simple file system server as an example.

First, initialize a manifest for your server:

This interactive tool asks about your server and generates a complete manifest.json. If you want to speed-run your way to the most basic manifest.json, you can run the command with a --yes parameter.

If your server needs user input (like API keys or allowed directories), declare it in the manifest:

Claude Desktop will:

In the example below, we’re passing the user configuration as an environment variable, but it could also be an argument.

Bundle everything into a

file:

This command:

Drag your

file into Claude Desktop's Settings window. You'll see:

Extensions can adapt to different operating systems:

Use template literals for runtime values:

Help users understand capabilities upfront:

We're launching with a curated directory of extensions built into Claude Desktop. Users can browse, search, and install with one click—no searching GitHub or vetting code.

While we expect both the Desktop Extension specification and the implementation in Claude for macOS and Windows to evolve over time, we look forward to seeing the many ways in which extensions can be used to expand the capabilities of Claude in creative ways.

To submit your extension:

We are committed to the open ecosystem around MCP servers and believe that its ability to be universally adopted by multiple applications and services has benefitted the community. In line with this commitment, we’re open-sourcing the Desktop Extension specification, toolchain, and the schemas and key functions used by Claude for macOS and Windows to implement its own support of Desktop Extensions. It is our hope that the MCPB format doesn’t just make local MCP servers more portable for Claude, but other AI desktop applications, too.

We're open-sourcing:

This means:

The specification and toolchain is on purpose versioned as 0.1, as we are looking forward to working with the greater community on evolving and changing the format. We look forward to hearing from you.

We understand that extensions introduce new security considerations, particularly for enterprises. We've built in several safeguards with the preview release of Desktop Extensions:

For more information about how to manage extensions within your organization, see our

.

Ready to build your own extension? Here's how to start:

: Review our

– or dive right in by running the following commands in your local MCP servers’ directory:

: Update to the latest version and look for the Extensions section in Settings

: Review our enterprise documentation for deployment options

Internally at Anthropic, we have found that Claude is great at building extensions with minimal intervention. If you too want to use Claude Code, we recommend that you briefly explain what you want your extension to do and then add the following context to the prompt:

Desktop Extensions represent a fundamental shift in how users interact with local AI tools. By removing installation friction, we're making powerful MCP servers accessible to everyone—not just developers.

Internally, we’re using desktop extensions to share highly experimental MCP servers - some fun, some useful.. One team experimented to see how far our models could make it when directly connected to a GameBoy, similar to our

. We used Desktop Extensions to package a single extension that opens up the popular

GameBoy emulator and lets Claude take control. We believe that countless opportunities exist to connect the model’s capabilities to the tools, data, and applications users already have on their local machines.

We can't wait to see what you build. The same creativity that brought us thousands of MCP servers can now reach millions of users with just one click. Ready to share your MCP server?

.
