---
url: https://openai.com/index/introducing-gpt-5-5/
title: Introducing GPT‑5.5
site: openai-research
date: 2026-09-01
scraped_at: 2026-09-04T13:12:53+00:00
---

April 23, 2026

A new class of intelligence for real work

Learn about OpenAI’s latest model:

Terminal-Bench 2.0

75.1%

-

-

69.4%

68.5%

Expert-SWE (Internal)

68.5%

-

-

-

-

GDPval (wins or ties)

83.0%

82.3%

82.0%

80.3%

67.3%

OSWorld-Verified

75.0%

-

-

78.0%

-

Toolathlon

54.6%

-

-

-

48.8%

BrowseComp

84.4%

82.7%

89.3%

79.3%

85.9%

FrontierMath Tier 1–3

51.7%

47.6%

50.0%

43.8%

36.9%

FrontierMath Tier 4

35.4%

27.1%

38.0%

22.9%

16.7%

CyberGym

79.0%

-

-

73.1%

-

“The first coding model I’ve used that has serious conceptual clarity.”

“The first coding model I’ve used that has serious conceptual clarity.”

, Founder and CEO of Every, described GPT‑5.5 as “the first coding model I’ve used that has serious conceptual clarity.”

After launching an app, he spent days debugging a post-launch issue before bringing in one of his best engineers to rewrite part of the system. To test GPT‑5.5, he effectively rewound the clock: could the model look at the broken state and produce the same kind of rewrite the engineer eventually decided on? GPT‑5.4 could not. GPT‑5.5 could.

“It genuinely feels like I’m working with a higher intelligence, and there’s almost a sense of respect.”

“It genuinely feels like I’m working with a higher intelligence, and there’s almost a sense of respect.”

CEO of MagicPath, saw a similar step change when GPT‑5.5 merged a branch with hundreds of frontend and refactor changes into a main branch that had also changed substantially, resolving the work in one shot in about 20 minutes.

, an immunology professor and researcher at the Jackson Laboratory for Genomic Medicine, used GPT‑5.5 Pro to analyze a gene-expression dataset with 62 samples and nearly 28,000 genes, producing a detailed research report that not only summarized the findings but also surfaced key questions and insights—work he said would have taken his team months.

, assistant professor of mathematics at Adam Mickiewicz University in Poznań, Poland, used GPT‑5.5 in Codex to build an algebraic-geometry app from a single prompt in 11 minutes, visualizing the intersection of quadratic surfaces and converting the resulting curve into a Weierstrass model.

He later extended the app with more stable singularity visualization and exact coefficients that can be reused in further work. For him, the bigger shift is that Codex can now help implement custom mathematical visualization and computer-algebra workflows that previously required dedicated tools. Together, these examples show GPT‑5.5 turning expert intent into working research tools and analyses.

SWE-Bench Pro (Public) *

58.6%

57.7%

-

-

64.3%

54.2%

Terminal-Bench 2.0

82.7%

75.1%

-

-

69.4%

68.5%

Expert-SWE (Internal)

73.1%

68.5%

-

-

-

-

GDPval (wins or ties)

84.9%

83.0%

82.3%

82.0%

80.3%

67.3%

FinanceAgent v1.1

60.0%

56.0%

-

61.5%

64.4%

59.7%

Investment Banking Modeling Tasks (Internal)

88.5%

87.3%

88.6%

83.6%

-

-

OfficeQA Pro

54.1%

53.2%

-

-

43.6%

18.1%

OSWorld-Verified

78.7%

75.0%

-

-

78.0%

-

MMMU Pro (no tools)

81.2%

81.2%

-

-

-

80.5%

MMMU Pro (with tools)

83.2%

82.1%

-

-

-

-

BrowseComp

84.4%

82.7%

90.1%

89.3%

79.3%

85.9%

MCP Atlas**

75.3%

70.6%

-

-

79.1%

78.2%

Toolathlon

55.6%

54.6%

-

-

-

48.8%

Tau2-bench Telecom***

(original prompts)

98.0%

92.8%

-

-

-

-

GeneBench

25.0%

19.0%

33.2%

25.6%

-

-

FrontierMath Tier 1–3

51.7%

47.6%

52.4%

50.0%

43.8%

36.9%

FrontierMath Tier 4

35.4%

27.1%

39.6%

38.0%

22.9%

16.7%

BixBench

80.5%

74.0%

-

-

-

-

GPQA Diamond

93.6%

92.8%

-

94.4%

94.2%

94.3%

Humanity's Last Exam (no tools)

41.4%

39.8%

43.1%

42.7%

46.9%

44.4%

Humanity's Last Exam (with tools)

52.2%

52.1%

57.2%

58.7%

54.7%

51.4%

Capture-the-Flags challenge tasks (Internal)****

88.1%

83.7%

-

-

-

-

CyberGym

81.8%

79.0%

-

-

73.1%

-

Graphwalks BFS 256k f1

73.7%

62.5%

-

-

76.9%

-

Graphwalks BFS 1mil f1

45.4%

9.4%

-

-

41.2% (Opus 4.6)

-

Graphwalks parents 256k f1

90.1%

82.8%

-

-

93.6%

-

Graphwalks parents 1mil f1

58.5%

44.4%

-

-

72.0% (Opus 4.6)

-

OpenAI MRCR v2 8-needle 4K-8K

98.1%

97.3%

-

-

-

-

OpenAI MRCR v2 8-needle 8K-16K

93.0%

91.4%

-

-

-

-

OpenAI MRCR v2 8-needle 16K-32K

96.5%

97.2%

-

-

-

-

OpenAI MRCR v2 8-needle 32K-64K

90.0%

90.5%

-

-

-

-

OpenAI MRCR v2 8-needle 64K-128K

83.1%

86.0%

-

-

-

-

OpenAI MRCR v2 8-needle 128K-256K

87.5%

79.3%

-

-

59.2%

-

OpenAI MRCR v2 8-needle 256K-512K

81.5%

57.5%

-

-

-

-

OpenAI MRCR v2 8-needle 512K-1M

74.0%

36.6%

-

-

32.2%

-

ARC-AGI-1 (Verified)

95.0%

93.7%

-

94.5%

93.5%

98.0%

ARC-AGI-2 (Verified)

85.0%

73.3%

-

83.3%

75.8%

77.1%
