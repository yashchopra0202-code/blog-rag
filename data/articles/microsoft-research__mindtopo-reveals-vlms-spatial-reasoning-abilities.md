---
url: https://www.microsoft.com/en-us/research/blog/mindtopo-reveals-vlms-spatial-reasoning-abilities/
title: MindTopo reveals VLMs’ spatial reasoning abilities
site: microsoft-research
date: 2026-08-12
scraped_at: 2026-09-04T13:21:05+00:00
---

Published

By

Share this page

Can AI determine whether two rooms remain connected after a wall is added? Can it recognize whether an animal is inside a fence, distinguish a true knot from a tangled loop, or rearrange several ropes without allowing them to pass through one another?

These questions concern 3D topology, a form of spatial understanding based not on exact distances, angles, or shapes, but on structural relationships that persist as objects bend, stretch, or deform. Connectivity, enclosure, ordering, and knottedness are examples of topological properties. These properties are a foundational layer of human spatial understanding in Cognitive Science, yet they remain largely absent from how multimodal AI systems are evaluated.

In a new research study, we introduce

, a benchmark designed to evaluate whether multimodal large language models possess this kind of topological intuition. Our findings reveal a substantial gap between recognizing topology in a static image and maintaining an innate understanding of that topology while planning and acting. Current models can sometimes identify a connected path, enclosed region, or knot in a single scene, but that understanding often breaks down once the model must manipulate the scene through a sequence of actions.

Most spatial evaluations for multimodal models focus on Euclidean properties such as distance, direction, size, and relative position. Inspired by Piaget and other cognitive literature’s classification of topological ability, MindTopo organizes its tasks around the following five categories:

Each category is evaluated at two cognitive levels. In reasoning tasks, a model examines one or more rendered scenes and answers a question about their topological structure: whether two points in a maze are connected, whether the sheep are inside the fence, whether a rope is truly knotted. In planning tasks, the model interacts with a simulated environment and selects actions that must create, preserve, or remove a particular relation, such as rotating pipe segments, drawing a separating path, rearranging blocks, trapping a moving agent, or untangling ropes. The environments enforce legal actions, so a model cannot solve a rope puzzle by passing one strand through another.

All scenes are generated from controlled simulators, which provide exact ground truth and adjustable difficulty. That control makes it possible to separate two failure modes that otherwise look alike: a model that fails because a scene is visually complex, and a model that fails because it cannot maintain the underlying relationship as objects move.

Across a broad set of proprietary and open-weight models, performance was consistently stronger on static reasoning than on interactive planning, and both remained well below human performance. The contrast was especially clear when success depended on preserving a relationship across many actions.

The error patterns help locate the problem. Static mistakes usually began with perception, such as missing a wall, opening, or crossing. Planning mistakes appeared after the scene had been understood. Models followed a locally plausible move without tracking its later consequences, lost the task over multiple turns, or proposed an action that violated the environment’s dynamics.

Stay connected to the research community at Microsoft.

We also tested whether image and video generation could help models maintain an understanding of topological relationships. Image generation sometimes helped when the relevant relation was visible in a single frame, but it remained unreliable across a sequence of crossings or moves. Video rollouts frequently altered topology or violated task dynamics. Visual simulation appeared useful only to the extent that it preserved structural constraints over time.

MindTopo is intended as a controlled diagnostic for this gap. Robots, accessibility tools, and interactive assistants must understand not only where objects are, but also what remains connected, enclosed, ordered, or knotted as actions unfold. Closing that gap may require models that carry an explicit topological state, or world models whose predictions preserve topology by construction.

Student

Student

PhD Student

Student

PhD Student

Technical Fellow & Corporate Vice President

Assistant Professor of Computer Science

Postdoc

Assistant Professor of Computer Science

Assistant Professor
