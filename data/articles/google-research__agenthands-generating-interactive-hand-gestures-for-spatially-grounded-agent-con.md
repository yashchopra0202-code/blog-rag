---
url: https://research.google/blog/agenthands-generating-interactive-hand-gestures-for-spatially-grounded-agent-conversations-in-xr/
title: AgentHands: Generating interactive hand gestures for spatially grounded agent conversations in XR
site: google-research
date: 
scraped_at: 2026-09-04T13:15:22+00:00
---

August 25, 2026

Xun Qian, Research Scientist, and Ruofei Du, Interactive Perception & Graphics Lead, Google XR

AgentHands is an LLM-powered XR prototype that augments conversational agents with synchronized, expressive hand gestures to provide spatially grounded guidance, bridging the mental mapping gap and enhancing user engagement in physical tasks.

As AI assistants evolve from simple text interfaces to multimodal companions, we are seeing a shift toward more proactive, situated assistance. Recent innovations like

and

already allow users to discuss their physical surroundings in real time, often utilizing visual bounding box overlays to identify objects in a camera feed. While these overlays are highly effective for 2D screens, the transition to immersive platforms like

presents a unique challenge: how do we move beyond flat UI to create a truly embodied, spatially aware dialogue?

To bridge this gap, we introduce

, published at

, a research prototype that brings the power of co-speech gestures to the 3D world. In human communication, our hands do more than just point; they describe shapes, mimic actions, and emphasize points, all synchronized with our voice. By leveraging the spatial understanding capabilities of

(XR), AgentHands replicates this natural synergy. Following up our prior research in

and

, AgentHands further equips AI agents with expressive, synchronized hand gestures that transform abstract verbal instructions into intuitive, physical demonstrations, making conversations about your surroundings more natural and engaging.

To start, we conducted a formative study with XR and

(HCI) experts at Google to determine what makes a virtual hand “legible” in a 3D environment. We distilled these insights into a multi-dimensional taxonomy that defines how an agent should use its hands to ground a conversation within a user's physical space.

The core innovation of AgentHands is its ability to map the high-level reasoning of LLMs into precise, real-time physical motions that match the agent's “voice” and the user's XR environment. We introduce the following key steps to compose the AgentHands workflow.

The system begins with a lightweight object registration module. Using eye gaze and scene reconstruction, users can quickly “tag” items — like an orchid or a laptop — creating a spatial registry with 3D bounding boxes that the agent can reference.

We constructed a library of hand gesture behaviors across three semantic categories: a)

for referencing, b)

for depicting actions or forms, and c)

for conveying social cues and emotion.

When a user asks a question, the backend LLM generates a response that includes inline GestureEvents. Each event is attached to specific trigger words and encodes the primitives for a hand behavior following the taxonomy dimensions.

A local parser on the XR headset coordinates the

(TTS) playback with the animation engine. By using word-level timestamps, the agent’s hands perform co-speech gestures in perfect sync with the spoken words, providing clear, expressive spatial references.

By integrating these modules, AgentHands creates a seamless bridge between linguistic intent and physical action. The system transforms a standard LLM output into a rich, multimodal performance where the agent's generated responses are manifested through both speech and spatially accurate movement, allowing for complex instructions to be demonstrated exactly where they occur in the user's environment.

We demonstrated how these embodied gestures, paired with the spatial awareness of XR, enhance our understanding of our physical surroundings.

In an orchid-care scenario, the agent doesn’t just say “check the roots”; it moves its hands to the base of the plant and outlines the air roots while explaining their function.

For 3D printer operations, the agent can demonstrate the exact ''turn and click'' sequence needed to navigate control knobs and select files, making complex physical interface steps intuitive.

The agent can serve as a wellness coach that interacts with your physical choices. For instance, the agent can perform an interactive “warning” gesture by holding the user’s hand and a visual effect to caution the user against unhealthy behavior.

To evaluate the impact of these gestures, we conducted a within-subjects study (N = 12) comparing AgentHands to a speech-only baseline. Both conditions used the same researcher-scripted verbal content, ensuring the only difference was the presence of the embodied hands and their synchronized gestures. Participants completed two procedural tasks that balanced everyday care with technical operation.

The results confirmed that the combination of XR and co-speech gestures is highly effective for spatially grounded interactions. We analyzed the data across several key metrics of communication effectiveness.

AgentHands represents a step toward a future where AI systems aren’t just analyzing our world, but dynamically operating within it. By leveraging co-speech gestures and the spatial power of XR to ground conversation in physical movement, we can reduce the cognitive load of complex tasks and make spatial computing more accessible and human-centric.

As we continue to develop for the Android XR ecosystem, we are exploring ways to make these gestures even more personalized, adapting to a user’s dominant hand or learning their specific spatial routines, to create an even more seamless human-AI collaboration.

September 3, 2026

September 3, 2026

September 1, 2026
