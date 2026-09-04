---
url: https://ai.meta.com/blog/introducing-muse-image-muse-video-msl/
title: Introducing Muse Image and Muse Video
site: meta-ai
date: 
scraped_at: 2026-09-04T13:19:26+00:00
---

We’re excited to launch Muse Image and preview Muse Video, the first media generation models developed by Meta Superintelligence Labs.

Muse Image is our most advanced image generation model yet: it follows instructions faithfully, edits with precision, and composes from multiple references. It also brings agentic tool use capabilities and integrates with Muse Spark. Muse Video, built on the same pretraining base, delivers exceptional visual fidelity with native audio support.

Muse Image is available today across the Meta AI app and on

, Instagram Stories in the US, and WhatsApp in limited countries, and is coming soon to Facebook. Muse Video is coming soon to creators and Meta AI.

Muse Image: Agentic Image Generation

Instead of directly mapping prompts to images, Muse Image operates as an agent: it invokes search and coding tools to improve accuracy, self-refines its own generations, and improves through scaling test-time compute. Muse Image also integrates with Muse Spark, allowing the two models to share tools and plan jointly for powerful agentic media generation.

Tool Use

We provide Muse Image with access to tools to enhance its agentic capabilities.

During reinforcement learning, Muse Image learns to write and execute code that produces accurate plots and QR codes, and condition on rendered figures to improve the accuracy of generated images. Muse Spark and Muse Image also integrate to use the combination of code and media generation to create animated GIFs, websites with embedded images, and interactive visual games.

Muse Image learns to search the web to ground generated images in factual and real-time information and visual references. Enabling search improves factual accuracy on knowledge-intensive prompts, particularly those involving current events and real-world facts.

Muse Image improves with search tool use. Win rate from internal ablation.

Self-Refinement

Muse Image reflects on and improves upon its own work within its chain of thought. This self-refining behavior can take different forms: a local edit to the current image draft when a small detail is off, a new image generation from scratch when larger parts are wrong, or a different tactic like tool use for more factually accurate generation. We didn’t design this behavior. Instead, it emerged during RL training simply because self-refinement produced better images and therefore higher reward.

Muse Image improves with emergent self-refinement. Win rate from internal ablation.

Test-Time Compute Scaling

Like language models, Muse Image improves the more it thinks at inference time. With more test-time compute, the model reasons more, uses more tool calls, and uses more self-refinement steps to improve its generations. Increasing reasoning strength (and thus test-time compute) improves human-preference Elo scores and shows an approximately log-linear scaling relationship. Notably, this compute spans two very different kinds of work — text tokens for reasoning, visual tokens for generation — yet quality is a function of the combined total compute.

We find that using the token budget judiciously matters just as much for effective test-time scaling. Best-of-N (BoN), where the model generates several images and keeps the best, improves quality early but saturates quickly. Spending that same compute on deliberate reasoning scales considerably better. Reasoning and tool use compound when combined. Tools let the model reach beyond what it already knows, whether by searching for references it lacks or writing code to get precise details right, filling gaps that reasoning alone can’t.

Muse Image improves with scaling test-time compute. Elo from internal ablation.

Image Editing

Muse Image edits images with precision, changing exactly what the user asks for. It can follow a variety of instructions as our examples show.

Restore this image

Edit this to clear up the fog and reveal the beautiful valley below

Change the flower so the petals form a rainbow gradient

Can you change this image to be '$3.00 ALL DAY', change the no free parking text to instead say 'FREE PARKING ON WEEKENDS' and change the phone number to be 555-5555

Zoom out slightly to share the chaos the dog has seen, giving context to its sheepish look

Muse Image maintains coherence across editing turns, supporting iterative refinement and open-ended brainstorming toward a target result.

Here is my living room

Can you imagine it in Japandi style?

I like this image but please use the lamp and the cabinet under it from the first image.

Great. Can you make a before-after picture of my first image and the last one?

Make an image of this cat

and this dog

as best friends having a picnic on a sunny day. Vintage 35mm style

Now show this exact picnic image as a framed photo hanging on the wall of a cozy cafe. We see a table and two empty chairs right in front of this wall.

Show the front of the cafe with its name and match the vibe of the cafe from the earlier photo. We should be able to see the framed photo from the window too.

Design this cafe's paper menu using its exact name, and add a 'The Picnic Special' item with a tiny illustration of the same cat and dog from the photo.

Place this menu

on the table from the close up empty table image we made earlier

Multi-Reference Image Composition

Muse Image can compose elements from many input reference images in the prompt, including people, objects, clothing, styles, and environments. It supports interleaving text and images inline in prompts for complex image compositions.

Make an image of

riding this bike

and wearing

while passing by

sitting on a park bench. Make it look like a drawing

in the style of this image.

Change the color of my living room

to this pattern

on the wall. Then add

on the coffee table, 2

on the credenza and a large super flat wall mounted 65 inch tv, with the following image on the screen

. Then add

sitting on the couch wearing

,

and

with no socks.

Image Benchmarks

Muse Image holds the No. 2 spot on Arena for text-to-image, single-image editing, and multi-image editing as measured by human preference Elo rankings at the time of writing.

Arena Elo rankings as of July 5, 2026.

Arena Elo rankings as of July 5, 2026.

Arena Elo rankings as of July 5, 2026.

Previewing Muse Video

Alongside the release of Muse Image, we’re sharing an early preview of Muse Video. It offers competitive performance in prompt adherence, visual fidelity, and temporal consistency. We’re investing in areas with current performance gaps, such as audio-video synchronization and physically accurate fast motion. Muse Video is coming soon to creators and in Meta AI.

A baby panda tumbling head over heels down a small grassy slope

A handmade paper-cutout / construction-paper collage stop-motion animation explaining Bernoulli's principle, calm warm male narrator with a clear natural voice and relaxed, well-enunciated pacing, 16:9. Layered textured cut paper, subtle paper grain, soft drop shadows, gentle flat lighting, warm pastel palette, slight stop-motion jitter, light paper-rustle foley, soft acoustic background music kept low under the voice. Visuals: a cut-paper title 'Bernoulli's Principle', then a proper cambered AIRFOIL cross-section …

first person point of view strolling along the edge of a small half-frozen pond in a snowy suburban park at night, snow-dusted reeds and cattails along the bank, fresh snow falling gently. Warm orange lamplight reflects softly on the dark open water. Serene and peaceful, with quiet nature sounds: the faint trickle of unfrozen water, a soft breeze through the reeds, distant snow-muffled stillness, and gentle footsteps in the snow. Natural handheld walking camera, cinematic, meditative.

A man juggles three oranges, adds a fourth, drops them all, and takes a bow anyway. Warm natural morning light, gentle slow-motion. A single continuous ~10-second moment with a clear beginning, turn, and payoff. AUDIO: quiet room tone with crisp foley. Photorealistic, natural lighting and physics, believable real-world footage. Not a cartoon, not stylized.

Handheld vertical 9:16 UGC-style ad: REC icon visible, a woman in her cluttered kitchen films herself with natural autofocus, slow-motion shot of steam curling off her Brivo kettle as she pours; she grins, 'Okay this Brivo kettle is actually insane, boils in like a minute!'; AUDIO: diegetic pour and steam-hiss plus her voice in sync under soft lo-fi music; bright neutral palette, neutral accurate white balance, clean true-to-white highlights, natural skin tones, no yellow or amber cast; premium high-end commercial look

A mother duck leads a line of exactly FIVE ducklings toward a curb; the fifth and smallest duckling struggles at the step, then hops up to rejoin the others. There are exactly five ducklings in total — the same five throughout the entire video — never add, remove, duplicate or change the number of ducklings; keep all five visible and consistent from start to finish. Cozy indoor lamplight, authentic home-video look, slightly imperfect handheld framing with natural shake. A single continuous ~10-second moment with a clear beginning …

A baby otter floating on its back, holding a smooth pebble on its belly

A slick, aspirational cinematic TV commercial for Blush Fizz, a sparkling lemonade brand. Opens with a top-down slow rotation of the glass bottle then a side tracking shot as it's poured in slow motion with citrus pulp and effervescent bubbles swirling upward. AUDIO: diegetic — the fizzy pour, faint citrus zest crackle, and light glass-clink foley, crisp and in sync, rising into a bright pastel-pop music bed; a confident voiceover says, 'Blush Fizz. Sip the light side.' Soft pastel pink and mint palette, neutral accurate white balance with clean true-to-white highlights and no …

a close-up with a subtle handheld sway of a single podcast host speaking into a large studio microphone, wearing headphones, in a cozy podcast studio with warm lighting and acoustic foam on the wall. The host says, 'hey chat, controversial take incoming, but the alphabet has been in the wrong order this entire time and we all just accepted it. Why is Q sitting right next to R? Who decided this? I demand answers.' On the wall behind them are two posters reading 'Reform The ABCs' and 'Why Is Q Next To R'. Deadpan-intense, slightly unhinged, comedic, realistic.

On Arena, Muse Video ranks No. 3 in human-preference Elo for text-to-video at the time of writing.

Arena Elo rankings as of July 5, 2026

Content Seal

To help people verify whether an image is AI-generated, Muse Image includes Content Seal, our invisible watermarking system. Images created by Muse Image in the Meta AI app and on

carry a hidden provenance signal that stays intact — even when cropped, compressed, resized, or screenshotted. We plan to extend Content Seal to video soon. We’re previewing a

that lets you check whether an image carries a Content Seal watermark, providing an initial way to help you better understand if an image was made with Meta AI.

Muse Image in Meta Products

Muse Image connects deeply with the Meta ecosystem. Our ongoing investments in image and video generation will further enable creators and businesses to generate dynamic content across Meta products.

Marketing assets for small businesses

Personalized presets directly in Instagram

Our latest updates delivered to your inbox

to our newsletter to keep up with Meta AI news, events, research breakthroughs, and more.

Resources

Meta AI

AI Research

Resources

About

Meta © 2026
