---
url: https://blogs.nvidia.com/blog/open-world-models-physical-ai/
title: Into the Omniverse: How Open World Models Push the Frontier of Physical AI
site: nvidia
date: 2026-08-06
scraped_at: 2026-09-04T21:18:21+00:00
---

Share This Article

X

Facebook

LinkedIn

Copy link

In July, NVIDIA joined more than 200 companies and organizations in signing “

,” an open letter arguing that AI leadership will be measured not by any single frontier model but by whether an open ecosystem reaches every sector.

, which anyone can download, inspect, modify and run on their own infrastructure, are what make that possible. Nowhere is that more crucial than in

, where every deployment is a specialization problem.

Physical AI has to understand and predict consequences, not just appearances.

To make this possible, w

learn how physical environments behave, what may happen next and which following actions make sense. They can generate physically grounded world and action data, simulate future states and provide a foundation that teams can specialize for a robot, autonomous vehicle or vision AI system.

Open world models are already being used to generate training data, test policies and specialize physical AI systems.

brings these capabilities together in an open model family, with leading benchmark results and adoption across robotics, autonomous vehicles and vision AI.

And

libraries, part of NVIDIA Agent Toolkit, provides prebuilt capabilities for building simulation-ready worlds that physical AI teams can use to train, test and validate systems before real-world deployment.

The data behind physical AI is difficult and expensive to collect at the scale required. Rare events and long-tail scenarios can be especially difficult to reproduce safely and repeatedly.

World models enable:

More useful data by learning physical relationships from large-scale multimodal scenarios.

More diverse environments that vary in weather, lighting, objects and trajectories.

A better foundation to build on and adapt to a particular robot, vehicle, sensor configuration, task or operating environment.

A general model hasn’t seen a team’s particular robot, sensors or operating environment. Closing that gap requires access to model weights, a license that permits adaptation and the tools needed for post-training.

NVIDIA Cosmos world foundation models are available under the Linux Foundation’s OpenMDW 1.1 license, enabling teams to post-train models on their own data and hardware. Specialization is where openness becomes a practical technical requirement.

Specializing a model is only part of the workflow. Teams also need environments to generate data, run simulations and test behavior.

Omniverse libraries help developers build simulation-ready environments, while

provides the open framework for composing, reusing and exchanging complex 3D data across

, simulations and

workflows. Together, Omniverse and OpenUSD cut the duplicated work that can otherwise pile up every time assets, sensor configurations or environmental conditions change.

NVIDIA Cosmos 3 — a frontier open physical AI foundation

built on a

architecture — combines vision reasoning, world generation and action prediction, letting developers use one model family to understand scenes, generate synthetic data, simulate future states and build specialized

.

Developers can use Cosmos 3 as a

, as a physics-grounded world simulator that predicts future world states and generates large-scale synthetic data, or as the backbone for world action models, instead of assembling and maintaining a separate model for each capability.

The family includes Cosmos 3 Super (64B) for high-fidelity world modeling, Cosmos 3 Nano (16B) for efficient reasoning and post-training, and

(4B) for on-device vision reasoning and robot policy deployment. Lightweight enough to run on edge GPUs, Cosmos 3 Edge can be deployed across NVIDIA RTX GPUs, NVIDIA DGX systems and NVIDIA Jetson, including Jetson Thor platforms.

Across benchmark evaluations, Cosmos 3 ranks No. 1 on

for open weights text-to-image and image-to-video generation, on

for world generation and in the image-to-video category of

. For robot policy, it ranks No. 1 on

. Cosmos 3 Super is also the highest-ranked open model on

for vision understanding.

In addition to Cosmos, NVIDIA’s physical AI stack includes

for robotics,

for autonomous vehicles and

for vision AI.

Across industries, developers are building on NVIDIA Cosmos for physical AI applications: Doosan Robotics, LG Electronics, Samsung Electronics and Skild AI in robotics; Li Auto, Xiaomi and Afari in autonomous vehicles; and

,

,

,

and

for

powering industrial AI and smart spaces applications.

The

extends this work by bringing together world model builders, AI developers and physical AI leaders to contribute models, research and evaluation methods. NVIDIA recently

, where robotics and manufacturing leaders intend to join and develop open world models for factories, logistics, agriculture, construction, healthcare and transportation.

Together, these implementations and collaborations are establishing open world models as an adaptable foundation for physical AI across robots, autonomous vehicles and vision AI systems.

Learn more about world models, OpenUSD and physical AI development by exploring these resources:

the open

and datasets on

and

.

the

for full architecture details and evaluations.

the

.

to the

.

about the

.

October 20-22
