---
url: https://mistral.ai/news/robostral-navigate/
title: Robostral Navigate: single-camera AI navigation | Mistral AI
site: mistral
date: 
scraped_at: 2026-09-04T13:23:27+00:00
---

Introducing

Robostral Navigate

Thinking

Summary

Robostral Navigate is an 8B model that enables robots to autonomously navigate complex environments using only a single RGB camera, achieving 76.6% success on unseen R2R-CE benchmarks—outperforming multi-sensor approaches while being more efficient. Built entirely in-house with simulated data and token-efficient techniques, it generalizes across robot types and adapts to real-world obstacles unseen during training. The model combines pointing-based navigation with reinforcement learning for continuous improvement, paving the way for unified embodied AI in robotics.

Today we're introducing Robostral Navigate, our first model built for embodied navigation. It's an 8B model that takes RGB images and a plain-language instruction and moves a robot through an environment:

To perform such tasks, other models often employ depth sensors, LiDAR, or several cameras working together. Robostral Navigate uses only one ordinary RGB camera and no depth sensors, yet still achieves 76.6% on R2R-CE (Room-to-Room in Continuous Environments) validation unseen, the benchmark for following instructions in environments held out of training. Consequently, it beats the best single-camera approach by 9.7 points and the best system using depth or multiple cameras by 4.5 points, despite using neither.

Our model is designed for robotic navigation, enabling robots to autonomously navigate complex environments, including offices, residential and commercial buildings, and outdoor settings.

This technology unlocks numerous applications across manufacturing, delivery, logistics, and hospitality, making it one of the most in-demand capabilities for our customers today. Give Robostral Navigate one instruction and it completes the entire task on its own, moving through a live space full of people and obstacles it was never shown, capable of adapting to any setting.

State-of-the-art performance on R2R-CE

on validation seen

on validation unseen

Operates from a single RGB camera, with no LiDAR or depth sensors

8B model, built in-house and trained entirely in simulation

Runs on wheeled, legged, and flying robots, and generalizes across robot sizes

Robust to differences in camera intrinsics

Token-efficient training via prefix-caching

Success Rate

Oracle Success Rate

Success weighted by path length

Navigation Error

Given a task and a history of observations, Robostral Navigate predicts where the robot should move next via

: it infers the image coordinates of the target location in the robot's current camera view, together with the desired orientation upon arrival. Unlike commands relying on metric displacements, pointing makes the policy naturally robust to changes in camera intrinsics and world scale.

However, this method cannot handle cases where the target location lies outside the current field of view. When pointing does not apply, the model falls back to displacements in the robot's local coordinate frame, such as:

Robostral Navigate is built entirely in-house and does not rely on existing open-source VLMs.

The model is initialized from our vision-language model specialized for grounding tasks such as pointing, counting, and object localization. Navigation emerges as a natural extension of these capabilities: once it understands where things are, it learns how to move.

We built an efficient data generation pipeline entirely in simulation. This enabled rapid iteration on the data, resulting in a dataset of approximately

.

A key ingredient of Robostral Navigate is an efficient training algorithm based on prefix-caching. Using a tree-based attention-masking strategy, our method compresses an entire episode into a single sequence, enabling training on all time steps in a single forward pass while preventing information leakage between time steps.

Compared to training with one sample per time step, our approach reduces the number of training tokens by

while preserving all of the learning signals. In practice, this method

We leverage our knowledge of post-training LLMs at scale, using online reinforcement learning, to boost the performance of Robostral Navigate. After the supervised training stage, we further improve the model's performance using CISPO, an online reinforcement learning algorithm. This enables the model to learn from trial and error, recover from failures, and acquire exploratory behaviors, effectively mitigating the distribution shift issue of vanilla behavior cloning. This alone improved the success rate by 3.2%. We are not seeing any plateauing, so we are confident that more training and more experiments will continue to push this number up.

Robostral Navigate is only the first step toward a unified embodied agent.

We believe navigation is a foundational capability for general-purpose robotics. By combining large-scale simulation, efficient training, and strong grounding priors, Robostral Navigate demonstrates that state-of-the-art embodied navigation can be achieved with a compact model and a single RGB camera.

Start your journey to embodied frontier AI,

.

The release of our navigation models marks a significant step forward, but our journey is far from over. Our ambition is to enable robots to autonomously navigate complex environments—offices, homes, commercial buildings, and outdoor spaces—and there's a lot more work to do. We are actively expanding our robotics team and looking for talented research scientists and engineers who share our ambition.

If you're interested in joining us on our mission to bring seamless navigation to robots everywhere, we welcome your applications

Read the

for the full architecture, training setup, and benchmark results.

Report

0%
