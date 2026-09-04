---
url: https://stability.ai/news-updates/introducing-stable-virtual-camera-multi-view-video-generation-with-3d-camera-control
title: Introducing Stable Virtual Camera: Multi-View Video Generation with 3D Camera Control
site: stability
date: Mar 18
scraped_at: 2026-09-04T21:11:22+00:00
---

Introducing Stable Virtual Camera, currently in research preview. This multi-view diffusion model transforms 2D images into immersive 3D videos with realistic depth and perspective—without complex reconstruction or scene-specific optimization.

The model generates 3D videos from a single input image or up to 32, following user-defined camera trajectories as well as 14 other dynamic camera paths, including 360°, Lemniscate, Spiral, Dolly Zoom, Move, Pan, and Roll.

Stable Virtual Camera is available for research use under a

. You can read the paper

download the weights on

, and access the code on

.

Today, we're releasing Stable Virtual Camera, currently in research preview. This multi-view diffusion model transforms 2D images into immersive 3D videos with realistic depth and perspective—without complex reconstruction or scene-specific optimization. We invite the research community to explore its capabilities and contribute to its development.

A virtual camera is a digital tool used in filmmaking and 3D animation to capture and navigate digital scenes in real-time. Stable Virtual Camera builds upon this concept, combining the familiar control of traditional virtual cameras with the power of generative AI to offer precise, intuitive control over 3D video outputs.

Unlike traditional 3D video models that rely on large sets of input images or complex preprocessing, Stable Virtual Camera generates novel views of a scene from one or more input images at user specified camera angles. The model produces consistent and smooth 3D video outputs, delivering seamless trajectory videos across dynamic camera paths.

The model is available for research use under a

. You can read the paper

, download the weights on

, and access the code on

.

Stable Virtual Camera offers advanced capabilities for generating 3D videos, including:

Supports user-defined camera trajectories as well as multiple dynamic camera paths, including: 360°, Lemniscate (∞ shaped path), Spiral, Dolly Zoom In, Dolly Zoom Out, Zoom In, Zoom Out, Move Forward, Move Backward, Pan Up, Pan Down, Pan Left, Pan Right, and Roll.

Generates 3D videos from just one input image or up to 32.

: Capable of producing videos in square (1:1), portrait (9:16), landscape (16:9), and other custom aspect ratios without additional training.

: Ensures 3D consistency in videos up to 1,000 frames, enabling seamless loops and smooth transitions, even when revisiting the same viewpoints.

Stable Virtual Camera achieves state-of-the-art results in novel view synthesis (NVS) benchmarks, outperforming models like ViewCrafter and CAT3D. It excels in both large-viewpoint NVS, which emphasizes generation capacity, and small-viewpoint NVS, which prioritizes temporal smoothness.

Stable Virtual Camera is trained with a fixed sequence length as a multi-view diffusion model, taking a set number of input and target views (M-in, N-out).

Stable Virtual Camera is trained as a multi-view diffusion model with a fixed sequence length, using a set number of input and target views (M-in, N-out). During sampling, it functions as a flexible generative renderer, accommodating variable input and output lengths (P-in, Q-out). This is achieved through a two-pass procedural sampling process—first generating anchor views, then rendering target views in chunks to ensure smooth and consistent results.

For a deeper dive into the model’s architecture and performance, you can read the full research paper

.

In its initial version, Stable Virtual Camera may produce lower-quality results in certain scenarios. Input images featuring humans, animals, or dynamic textures like water often lead to degraded outputs. Additionally, highly ambiguous scenes, complex camera paths that intersect objects or surfaces, and irregularly shaped objects can cause flickering artifacts, especially when target viewpoints differ significantly from the input images.

Stable Virtual Camera is free to use for research purposes under a

You can read the

and download the weights on

and code on

.

To stay updated on our progress, follow us on

,

, and join our

.

Introducing Stable Virtual Camera, currently in research preview. This multi-view diffusion model transforms 2D images into immersive 3D videos with realistic depth and perspective—without complex reconstruction or scene-specific optimization.

The model generates 3D videos from a single input image or up to 32, following user-defined camera trajectories as well as 14 other dynamic camera paths, including 360°, Lemniscate, Spiral, Dolly Zoom, Move, Pan, and Roll.

Stable Virtual Camera is available for research use under a

. You can read the paper

download the weights on

, and access the code on

.

Today, we're releasing Stable Virtual Camera, currently in research preview. This multi-view diffusion model transforms 2D images into immersive 3D videos with realistic depth and perspective—without complex reconstruction or scene-specific optimization. We invite the research community to explore its capabilities and contribute to its development.

A virtual camera is a digital tool used in filmmaking and 3D animation to capture and navigate digital scenes in real-time. Stable Virtual Camera builds upon this concept, combining the familiar control of traditional virtual cameras with the power of generative AI to offer precise, intuitive control over 3D video outputs.

Unlike traditional 3D video models that rely on large sets of input images or complex preprocessing, Stable Virtual Camera generates novel views of a scene from one or more input images at user specified camera angles. The model produces consistent and smooth 3D video outputs, delivering seamless trajectory videos across dynamic camera paths.

The model is available for research use under a

. You can read the paper

, download the weights on

, and access the code on

.

Stable Virtual Camera offers advanced capabilities for generating 3D videos, including:

Supports user-defined camera trajectories as well as multiple dynamic camera paths, including: 360°, Lemniscate (∞ shaped path), Spiral, Dolly Zoom In, Dolly Zoom Out, Zoom In, Zoom Out, Move Forward, Move Backward, Pan Up, Pan Down, Pan Left, Pan Right, and Roll.

Generates 3D videos from just one input image or up to 32.

: Capable of producing videos in square (1:1), portrait (9:16), landscape (16:9), and other custom aspect ratios without additional training.

: Ensures 3D consistency in videos up to 1,000 frames, enabling seamless loops and smooth transitions, even when revisiting the same viewpoints.

Stable Virtual Camera achieves state-of-the-art results in novel view synthesis (NVS) benchmarks, outperforming models like ViewCrafter and CAT3D. It excels in both large-viewpoint NVS, which emphasizes generation capacity, and small-viewpoint NVS, which prioritizes temporal smoothness.

Stable Virtual Camera is trained with a fixed sequence length as a multi-view diffusion model, taking a set number of input and target views (M-in, N-out).

Stable Virtual Camera is trained as a multi-view diffusion model with a fixed sequence length, using a set number of input and target views (M-in, N-out). During sampling, it functions as a flexible generative renderer, accommodating variable input and output lengths (P-in, Q-out). This is achieved through a two-pass procedural sampling process—first generating anchor views, then rendering target views in chunks to ensure smooth and consistent results.

For a deeper dive into the model’s architecture and performance, you can read the full research paper

.

In its initial version, Stable Virtual Camera may produce lower-quality results in certain scenarios. Input images featuring humans, animals, or dynamic textures like water often lead to degraded outputs. Additionally, highly ambiguous scenes, complex camera paths that intersect objects or surfaces, and irregularly shaped objects can cause flickering artifacts, especially when target viewpoints differ significantly from the input images.

Stable Virtual Camera is free to use for research purposes under a

You can read the

and download the weights on

and code on

.

To stay updated on our progress, follow us on

,

, and join our

.
