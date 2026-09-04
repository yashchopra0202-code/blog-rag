---
url: https://www.microsoft.com/en-us/research/blog/flint-a-visualization-language-for-the-ai-era/
title: Flint: A visualization language for the AI era
site: microsoft-research
date: 2026-07-08
scraped_at: 2026-09-04T13:21:57+00:00
---

Published

By

Share this page

Creating a good chart requires many design decisions: how dates should be parsed, whether a scale should start at zero, how values should be formatted, how much room labels need, and which colors make the data easier to read. Modern visualization libraries such as Vega-Lite, Apache ECharts, and Chart.js expose these controls, but there is a trade-off: Short specifications that rely on system defaults often produce uninspiring charts, while polished visualizations require detailed specifications with purposely chosen parameters that are often verbose, fragile, and error-prone.

This trade-off becomes sharper as large language models (LLMs) and AI agents take on more visualization work. Agents are especially prone to errors when they must manage complex, low-level specification details, and the resulting fragile code can be difficult for people to inspect, repair, or reuse. Ideally, we need something in between: a compact specification that agents can produce reliably, people can edit directly, and a system can compile into a well-designed chart.

To address this challenge, we introduce

, a visualization intermediate language for AI-driven chart creation. Flint helps AI agents create expressive, attractive charts from simple, human-editable chart specs. Instead of requiring verbose low-level parameters for scales, axes, spacing, and layout, the Flint compiler derives optimized chart settings from the data, semantic types, chart type, and encodings. The same Flint spec can render through multiple backends, including Vega-Lite, Apache ECharts, and Chart.js.

Figure 2 illustrates the how the Flint compiler turns a compact chart specification into a refined heatmap.

To produce a high-quality heatmap, traditionally, we need to explicitly tell the system with low-level chart properties about how to process the period field, how to properly label MonthYear values, size individual heatmap cells, and choose a color scale that appropriately represents positive and negative newUsers values. Without these configurations, visualization libraries must guess from field names and raw values, which can lead to charts that are technically valid but potentially misleading. While they are important, hard-coding these details can be difficult and error-prone, and they make specification fragile and hard for users to understand or adapt.

In Flint, these low-level details are systematically managed, where the compiler infers them from high-level data and chart specifications. Here, the

captures semantic types and optional metadata, and the

defines the chart type and maps fields to visual channels such as x, y, color, size, or facet. From this information, the compiler derives the parsing rules, scales, axes, aggregations, formatting, color schemes, layout, and generates the backend-native specification, which is used to render the final polished visualization. This frees users from explicitly setting fragile and error-prone low-level details.

Furthermore, because the intermediate representation is separate from any single rendering library, Flint can target backends with very different APIs and programming models. Users can keep the same compact chart intent while compiling to Vega-Lite, ECharts, or Chart.js, and choose the backend whose capabilities best fit the visualization.

Discover how Microsoft is learning from other domains to advance evaluation and testing as a pillar of AI governance.

Flint is well suited to LLM-based chart generation because semantic types are often easier for models to infer than the full set of low-level visualization parameters. Field names, value patterns, and common data knowledge can help an agent recognize whether a column represents a date, price, percentage, country, ranking, or correlation. Once those meanings are explicit, the compiler can handle many design decisions that would otherwise appear as brittle, library-specific code.

In our research study, we compared Flint with DirectVL, a baseline that asks the model to directly generate full (more complex) Vega-Lite specifications in a LLM self-evaluation pipeline. Across three tested models based on testing data from Tidy Tuesdays, Flint received higher overall LLM-judge scores: 16.27 vs. 15.91 with GPT-5.1, 16.16 vs. 15.60 with GPT-5-mini, and 15.91 vs. 15.34 with GPT-4.1. In fact, Flint has been so powerful and reliable that it is now used to power

, a Microsoft Research project for AI-assisted data analysis and visualization.

To make Flint easy for your agents to access, we also release

, a Model Context Protocol (MCP) server that allows agents to create, validate, and render charts inside a chat or coding environment. MCP calls can embed data inline or read configured local files, and the server can open an interactive chart view so users can inspect and refine the results.

Flint is open source and ready to use:

Flint points toward a shared semantic layer for visualization, where people and AI agents can work with compact chart intent while a compiler handles the careful low-level details. We invite the community to explore the project and build on it.

Senior Researcher

Senior Data Visualization Engineer

Sr. Technical Program Manager

Senior Principal Research Manager

Technical Fellow & Corporate Vice President
