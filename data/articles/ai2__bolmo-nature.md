---
url: https://allenai.org/blog/bolmo-nature
title: Now in Nature: Retrofitting language models to operate over bytes
site: ai2
date: 
scraped_at: 2026-10-08T11:05:19+00:00
---

October 7, 2026

Last December, we introduced

, our family of fully open byte-level language models. Now, the research behind Bolmo

, and we’re

on Hugging Face that extend the underlying approach beyond the Olmo models that served as Bolmo’s starting point to other model families.

We’re also

, which keep the original global model frozen while training Bolmo’s new byte-level components, giving researchers a faster starting point for experimenting with and extending the architecture.

Most language models don’t process text directly. Instead, they first break it into subwords: word chunks drawn from a fixed vocabulary. That approach works remarkably well, but it can also make models less flexible when dealing with things like spelling, unusual strings, rare words, or text that doesn’t map cleanly onto those predefined chunks.

Byte-level models take a different approach, processing text as the underlying bytes computers use to represent characters. Models such as Bolmo therefore work from a lower-level representation of text—the byte sequences corresponding to letters, punctuation, symbols, and other characters.

Working at this level can improve a model’s understanding of fine-grained text structure, from whitespace to different writing systems, without tying it to a fixed vocabulary. And because bytes are a fundamental representation of digital data, byte-level modeling could eventually provide a common foundation for working with other kinds of information including images and audio.

Historically, though, getting byte-level models to match the performance of subword models has required training them from scratch—an expensive proposition that makes it difficult for byte-level approaches to keep pace as subword models rapidly improve.

With Bolmo, we demonstrated another approach. We created a process we call

, which takes an already capable subword model and converts it into a byte-level one with a relatively short additional training run. We used the approach to develop Bolmo 1B and Bolmo 7B from our open Olmo models, producing what we believe are the first fully open byte-level language models competitive with strong subword models across a broad range of tasks.

In the Nature paper, we show that byteifying generalizes beyond Olmo. We applied the same process to Qwen 3 8B and Llama 3 8B to create two new byte-level models, Bwen 8B and Blama 8B. Both come close to matching the models they were derived from, and Bwen 8B is our strongest byteified model yet—outperforming Bolmo 7B across our aggregate evaluation suite.

Developers and researchers have already begun adapting Bolmo for specific applications, including a

Bolmo’s publication follows other recent Ai2 research in

. In February, our paper “

” showed how specialized retrieval, ranking, and citation handling can help language models synthesize scientific literature with more reliable grounding.

Bolmo, that work, and our broader research reflect a common belief that fundamental advances in AI are more impactful when the research community can inspect them, reproduce them, and easily build on them.

With Bolmo, that means opening a path to models that aren’t locked into a single way of representing information. Future systems could adapt their representations across languages, domains, and tasks, while researchers test new architectures without repeating the full cost of training. Because bytes also extend beyond text, the same ideas could eventually apply to other kinds of data.

Researchers are also beginning to use Bolmo as a foundation for new work, including

and

By making Bolmo and its training recipe fully open, we hope to help researchers challenge assumptions built into today’s language models—and discover what becomes possible when those assumptions change.

At Ai2 we’re building the future of transparent, open-source AI — built in the open to empower scientific progress and fundamental understanding of this world changing technology. We’re not here to make profits, we’re here to make sure benefits of AI are shared widely and for the benefit of humanity. If this appeals to you, please take a look at our open roles.
