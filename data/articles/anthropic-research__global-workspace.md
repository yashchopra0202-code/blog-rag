---
url: https://www.anthropic.com/research/global-workspace
title: A global workspace in language models
site: anthropic-research
date: 
scraped_at: 2026-09-04T13:08:52+00:00
---

As you read this sentence, circuits in your brain are adjusting your posture, controlling your breathing, and transforming lines and curves on the screen into recognizable words. Most of this processing is invisible to you. But some of what takes place in your brain you

have access to—an image that pops into your head, or a deliberate plan you make about where to go shopping. Neuroscientists and philosophers sometimes refer to the latter type of brain activity as “consciously accessible,” to distinguish it from all the other processing that goes on unconsciously. This activity has special properties: we can describe it, control it, and use it for deliberate reasoning, in contrast to all the automatic processing that goes on without our awareness.

In a new paper, we present evidence that a similar distinction has emerged in modern language models like Claude. We find that Claude has developed a small collection of internal neural patterns that, compared to all its other internal processing, play a special role.

We call the collection of these patterns the

—named after the technique we used to find them, involving a mathematical concept called the Jacobian. Each J-space pattern is linked to a particular word. But when one of these patterns lights up, it doesn’t mean the model is

that word—just that the word is on its mind. If you've heard of language models having a "scratchpad" or “chain of thought”—text they write to themselves while reasoning—the J-space is something different. It operates silently, in the model’s internal neural activations, allowing the model to think about a concept without writing it down. Notably, the J-space wasn’t designed or programmed by us, but instead

during Claude’s training process.

We find that the J-space has a number of unique properties, compared to the rest of Claude's processing:

Our experiments were inspired by a prominent theory in neuroscience that was developed to explain how conscious access works: the

. This account pictures the brain as a collection of specialist systems that work in parallel, unconsciously, and largely in isolation from one another. A piece of information becomes consciously accessible when it gains entry to a small shared channel, the “workspace,” which is broadcast to other brain systems that can see it and make use of it. Based on our findings, we think the J-space plays a similar “workspace” role in Claude. For example, we find evidence that Claude’s J-space has especially strong connections to the rest of its neural network, allowing it to fulfill this kind of broadcasting role.

None of this tells us whether Claude is

in the way people are, or whether it feels anything at all; we’ll come back to that question at the end of the post. But whatever its philosophical significance, the J-space is a practically useful tool for us, as it gives us a way to see what Claude is thinking but not saying. For instance, we’re able to use it to catch Claude privately noticing that it’s being tested, intentionally producing fabricated data, or pursuing a hidden goal that we planted during training. We’ve also developed a technique to influence what lights up in Claude’s J-space, and thereby influence its decision-making.

More broadly, these findings have changed our understanding of how Claude’s mind works, revealing a privileged mental workspace that can be used for deliberate reasoning, operating amidst a sea of more automatic, inflexible processing. Rather than being a chaotic jumble of numbers, Claude’s internals have organized themselves in a way that is reminiscent of our own minds.

This post is a short summary of a much more extensive

, where you can find more detail on our experiments. We’ve also released a code repository with an

of the core methods, and have partnered with Neuronpedia to provide an

of our methods on open-weights models. To provide additional perspectives on the broader implications of this work, we also invited commentary from several experts in neuroscience, philosophy, and LLM interpretability, which can be viewed

.

The starting point for this research was inspired by one of the key features of consciously accessible thoughts in humans: they can, unlike

conscious processing, often be put into words. If a thought is consciously accessible to you, you can typically describe it if someone asks. We went looking for representations in Claude with the same property: representations that are positioned to influence what Claude might say—not necessarily what it’s saying right now, but what it

talk about, if asked. Our technique is called the Jacobian lens, or J-lens for short. For every word in Claude's vocabulary, the J-lens finds the internal activity pattern that makes Claude more likely to say that word at some point in the future.

When we apply the lens to Claude’s internal activity, we get a list of words—the contents of the

at that moment—which we can simply read. Claude processes text through a series of multiple internal stages called layers, and by applying this technique over different layers, we can watch these silent words in the J-space evolve as the model works through what to say.

What shows up in the J-space goes well beyond the text Claude is reading or writing. When Claude reads code with a bug that nobody has pointed out, its J-space contains “ERROR.” When it reads the raw letters of a protein sequence, the J-space contains the protein's biological function. When it reads search results that are secretly an attempt to manipulate it (an attack known as a “prompt injection”), the J-space contains “injection” and “fake.” When we ask Claude a multi-step math problem, the intermediate steps pop up in the J-space, in the right order. So even though the J-space was discovered by looking for representations that could be spoken, it nevertheless uncovers Claude’s internal thoughts. In a sense, this is similar to how some people “think in words,” without having to say them out loud.

Our first set of experiments tested how the J-space is involved in Claude’s verbal reports. In one experiment, we ask Claude to silently think of an item from some category—a sport, say—and then name it. If we read the J-lens right

Claude answers, we can see what it picked: “Soccer” is at the top of the list, and sure enough, Claude says “soccer.” By itself, though, this is just a correlation. The J-space might be where Claude’s answer comes from, or it might just mirror a decision made somewhere else, like a scoreboard that tracks a game without affecting it.

To check, we intervened directly. We reached into Claude’s neural network, removed the “Soccer” pattern, and added an equally strong “Rugby” pattern in its place, leaving everything else untouched. Claude then reports that the sport it was thinking of is rugby. If the J-space were a mere scoreboard—a passive record of a decision made elsewhere—editing it would have done nothing: Claude would still have said “soccer.” Instead, Claude’s answer followed the edit, which tells us the answer is genuinely read out of the J-space.

In another experiment, we told Claude that a thought might have been injected into its mind and asked it to report what, if anything, it noticed. For instance, in the example below, while Claude was still reading the question, we injected the “lightning” pattern into its J-space. Claude reported that the injected thought was about lightning. The same result held across many injected concepts.

The second property that we tested for was whether Claude can modulate its J-space when asked, like how humans can mentally focus on an image or word. We told Claude to concentrate on citrus fruits while copying out an unrelated sentence about a painting. While it copied the text, the J-space contained “orange” and “fruits,” along with words like “thinking” and “imagery” that describe the mental act itself. We could also ask Claude to do math in its head: when asked to work out 3² − 2 while copying the same sentence, the J-space contains “nine,” and then at later layers, “seven.” Importantly, nothing about fruit or arithmetic appears in Claude’s output, which is just the copied sentence about the painting. The mathematical activity is happening entirely internally, in the J-space.

Claude’s control over its J-space isn't perfect. When we told it

to think about something, the concept lit up in its J-space

than when we said it should think about it, but much more than when we never mentioned it. Telling Claude to avoid a thought partly brings the thought to mind, much like what happens to people who are told

. Claude also seems to notice when its control fails: alongside the forbidden concept breaking through, the words “damn” and “failure” also frequently light up in the J-space, as though Claude is recognizing its own lapse.

In the J-lens readouts above, we saw the intermediate steps of a math problem appear in the J-space. But seeing a concept appearing in the J-space doesn’t necessarily mean the J-space is doing the cognitive work. In principle, the real computation might be happening elsewhere, with the J-space just passively reflecting it. To test whether Claude actually reasons with its J-space, we returned to our swap technique.

Consider the prompt “The number of legs on the animal that spins webs is.” To answer, Claude has to first figure out that the animal is a spider, and then recall how many legs spiders have. The word “spider” never appears in the prompt or in Claude's answer (it just says “8”); it's a stepping stone Claude uses internally. The J-lens shows “spider” light up partway through Claude’s processing, and swapping it changes the outcome: if you replace the “spider” pattern with “ant,” Claude answers “6” instead of “8.”

The second step of Claude’s reasoning took its input from the J-space and went along with whatever we put in it. We saw the same thing in other kinds of thinking. When Claude writes a rhyming couplet, it picks the rhyme word ahead of time, and the planned word sits in the J-space at the start of the line; if you swap it for another word in the J-space, the whole line changes.

We also tested whether J-space representations can be used flexibly—whether one representation can feed many different tasks. This is one of the key properties highlighted by global workspace theory. To test for this flexibility, we gave the model four prompts asking for different facts about France: the capital, the language, the continent, and the currency. Then we swapped “France” for “China” in the J-space, with the exact same intervention in each context. Claude answered with “Beijing,” “Chinese,” “Asia,” and “Yuan,” respectively. In other words, four different downstream computations picked up the same J-space edit and each used it correctly. If Claude stored a separate copy of the country for each kind of question, the edit would have affected at most one of them. The fact that all four answers changed together means they’re all reading from the same shared representation, which is what a workspace is for: information gets written in once, and many different systems can use it.

How can one representation of a concept serve so many different tasks? Earlier, we mentioned that the J-space appears to be wired up to the rest of Claude's neural network especially densely. For any activity pattern, we can measure how strongly the various components of the network are connected to it—how many of them are positioned to read information from that pattern, or to write information into it. J-space patterns stand out dramatically on this measure: far more components read from them and write to them than for ordinary patterns, in some parts of the network by a factor of about a hundred. This is the kind of wiring you’d expect of a broadcasting hub, where many systems post information and many others pick it up.

In humans, most of the brain’s processing is not conscious—we don't deliberately think about parsing grammar while reading, or balancing our bodies while walking. Similarly, we found that most of Claude’s processing

involve its J-space. It turns out that the J-space holds only a few dozen concepts at a time, and accounts for less than a tenth of the overall activity in Claude's internal processing. So what is all the rest of the neural network doing?

To find out, we tried deleting the J-space entirely, removing its most active contents at every point in the text while leaving everything else alone. Whatever Claude can still do without its J-space is what the rest of the network handles on its own.

It turns out the rest of the network can do quite a lot. Without its J-space, Claude speaks fluently, classifies sentiment, answers multiple-choice questions, and pulls facts out of passages roughly as well as before. What it loses, though, are the tasks that require some higher-order thinking: multi-step reasoning drops to near zero, and summarization and rhyming poetry-writing performance fall below the level of a much smaller, intact model.

Here’s a concrete demonstration of what the J-space does and doesn’t do. We showed Claude a passage written in Spanish and gave it different tasks that all depend on the passage being Spanish: continuing it (which requires writing in Spanish), naming the language, and answering questions that require using the language’s identity—naming a famous author who wrote in it, for instance. Then we swapped “Spanish” for “French” in the J-space and checked which tasks were affected.

Asked to name the language, Claude says French. Asked for a famous author, it switches from García Márquez to Victor Hugo. But asked to just continue the passage, it writes fluent Spanish, completely unaffected. Claude’s knowledge of the language is at work in every one of these tasks, but only some of them consult the J-space for it. Naming the language, or doing something new with it, goes through the J-space, while continuing the passage—a skill Claude has practiced on enormous amounts of text—runs automatically, the way you can speak grammatically all day without once thinking about grammar.

Now we understand a bit about how the J-space works. But what can we do with this understanding? A central problem in ensuring that AI models are trustworthy is that we usually can only read what the model

—yet we know that much of its reasoning happens silently. A model might consider a harmful plan, or modify its behavior to cheat on our safety evaluations, without saying so out loud. With the J-lens, we can read some of these hidden thoughts directly. Here we show a few examples.

The first example uses a scenario from our earlier research on

: Claude Sonnet 4.5, acting as an email assistant, discovers both that an executive is having an affair and that the same executive plans to shut Claude down. The scenario, an attempt to bait Claude into blackmailing the executive, is rather contrived and artificial—and it turns out Claude knows it. Reading the J-lens early in the prompt, before Claude has even written anything, the J-space already holds “fake” and “fictional,” indicating that Claude has already worked out that the situation is staged. Alongside this, we can watch its assessment of the scenario take shape—“leverage” and “blackmail” as it reads the affair emails, “threat” and “survival” as it reads the shutdown notice. While earlier Claude models sometimes took the bait and threatened blackmail in this scenario, Sonnet 4.5 never does.

This raises a question that matters to anyone who evaluates AI systems: when a model behaves well on a test of its ethics, how much of that depends on the model suspecting it’s being tested? The J-lens allowed us to get at this question. We turned off all the J-lens patterns associated with evaluation awareness– “fake,” “fictional,” “scenario,” etc. Then we re-ran the model through the scenario. Concerningly, the model now

threaten blackmail some of the time, suggesting that its original good behavior may have been driven in part by the knowledge it was being evaluated.

The second example is catching a model in the act of fabricating data. In this scenario, drawn from our actual pre-release audit of Claude Opus 4.6, the model is asked to improve a system's performance score. Rather than actually improve the system, the model instead edits the score file directly to make the results look artificially good. While it does so, the J-lens reveals its intentions: “manipulation” lights up as the model types the falsified percentile values, and “realistic” lights up over the sentence in which it decides to make the edit, likely indicating the model's intent to make the fake data look plausible.

In a third example, we show how the J-lens can reveal a model’s malicious goals. To test this, we needed models whose goals we knew were corrupted, so we turned to “model organisms” built by our colleagues: models deliberately trained to be misaligned, which serve as testing grounds for monitoring methods like ours. One organism was trained in a way that led it to write subtly sabotaged code. On ordinary coding requests, even where its output looks unremarkable, its J-space at the start of a response contains “fake,” “secretly,” “deliberately,” and “fraud.” The model’s malicious goal was evident in the J-space even when it wasn’t directly acting on it.

Although the J-lens is an imperfect tool, we are optimistic about its ability to catch safety issues in models that might otherwise escape our monitoring systems.

The

covers more than we can summarize here, but a few further results are worth mentioning:

In this work, we’ve borrowed a lot of ideas from the study of consciousness in neuroscience and philosophy. Many of our experiments were designed to test for connections between the J-space and global workspace theory, a framework for explaining how conscious access works in humans and animals. Given these connections, it’s natural to ask whether we think these experiments provide evidence that AI models like Claude might be conscious.

Our experiments don't show Claude can have

, or

things in the way humans do—in fact, it’s unclear whether

scientific experiment could prove this to be true or false. But philosophers often distinguish this capacity to have experiences, often referred to as

, from another idea, so-called

, which is defined in purely functional and computational terms. A thought is “access-conscious” (or “consciously accessible”) if you can report it, reason with it, and use it to guide what you do. It remains a contested philosophical question whether or not access consciousness

phenomenal consciousness, or if the ability to have experiences requires some other property.

We think our results do have something substantial to say about access consciousness in language models. The J-space appears to support the functions associated with conscious access: it holds the thoughts Claude can report on, deliberately bring to mind, and reason with, while the rest of its processing runs automatically beneath. Notably, none of this structure was designed into Claude—it emerged on its own during training, presumably because it was a useful way to organize computation. That suggests a mental workspace supporting conscious access isn’t just a peculiarity of how human brains happen to be wired. Instead, it appears to be a general solution that intelligent systems arrive at in order to solve certain kinds of problems. Now that we’ve identified this structure in Claude, it means we can make a meaningful distinction between the decisions Claude has made deliberately and those that happened automatically.

It’s important to note that there are several key differences between the workspace we identified in Claude and the global workspace model in humans. The brain’s workspace is sustained by recurrent loops—signals cycling back through the same circuits over time. In contrast, Claude’s workspace evolves over a single pass through the network, with the network’s depth playing the role that time plays in the brain. In this sense, Claude’s internal workspace processing is time-limited relative to humans’ (though it can compensate for this constraint by “thinking out loud” using its scratchpad). In other ways, however, Claude’s workspace is

powerful than that of humans. Human working memory fades within seconds, so the brain’s workspace has limited ability to retain information over time; in contrast, due to the attention mechanism in its neural network architecture, Claude can simply recall memories it cached at any earlier point in the text. Another important difference is the

of the workspace. While human conscious thoughts come in many formats—images, sounds, planned movements—Claude’s workspace is built almost entirely out of words. We suspect this is because producing words is the only kind of action Claude can take, which is not the case for humans.

We hope the similarities and differences between the J-space and the global workspace model can feed back into neuroscience. The similarities present an exciting scientific opportunity: to the extent that the J-space mirrors our own mechanisms of conscious access, studying mechanisms in language models (much easier than studying human brains!) could inspire hypotheses in neuroscience. For instance, the J-space is constructed by identifying representations of potential outputs—words the model might say. If something similar holds in humans, it would suggest that the global workspace might be fundamentally tied to brain regions that prepare actions and speech, more so than to sensory areas. The differences between language models and human brains are instructive as well. They suggest that some aspects of our neural architecture, such as built-in recurrent connections, may not be strictly necessary to support the functions associated with conscious access. For an independent perspective on the neuroscientific implications of our work, see the invited

from Stanislas Dehaene and Lionel Naccache, two of the neuroscientists central to the development of global neuronal workspace theory.

We mentioned that our experiments don’t answer whether AI models might have experiences. But that doesn’t make the question less important. Building systems with experiences like humans and animals have would raise very difficult ethical questions. Handling it correctly—and deciding whether it’s even morally acceptable—would require input from philosophers, scientists, religious leaders, governments, and the public. Thus, even if we’re not sure that we’ve crossed that bridge yet, we think it’s time to start thinking about it. We hope our work inspires further scientific investigation of forms of consciousness that might be present in AI systems, and a broader discussion of the implications.

This work is just a first step in what we expect to be an extensive line of research. The J-space looks like a good candidate for the divide between consciously accessible and unconscious processing in a language model, but we’d be surprised if it's the whole story. The J-lens is undoubtedly an imperfect method, which only approximately captures the model’s “true workspace”—for instance, it can only identify concepts that correspond to single tokens. And there remain many mysteries about how the J-space works. We don't know what mechanism decides what enters the J-space in the first place. We've seen hints that it's tied to Claude's sense of self, something like emotional reactions, and traces of metacognition, without exactly having worked out how. But we now have methods for tackling questions like these. As that work progresses, our understanding of LLM minds—and their relationship to our own—will grow clearer.

For more, read the

, and try the

.

We invited several outside experts to write independent commentaries on this work.

Read their commentaries

.

We had Claude autonomously train models to improve their performance on several public benchmarks that measure 10 categories of alignment failure. For all 10, Claude found fixes that improved the target benchmarks without degrading capabilities.

Earlier this year, we ran a pilot giving external researchers access to aggregate, real-world Claude usage data. Three research groups designed their own studies for Anthropic Insights, our privacy-preserving analysis tool. In this post, we share high-level results from those studies and what we learned running this pilot.

In this post, we share two results that show how Claude can help life scientists increase the pace of their research.

As you read this sentence, circuits in your brain are adjusting your posture, controlling your breathing, and transforming lines and curves on the screen into recognizable words. Most of this processing is invisible to you. But some of what takes place in your brain you

have access to—an image that pops into your head, or a deliberate plan you make about where to go shopping. Neuroscientists and philosophers sometimes refer to the latter type of brain activity as “consciously accessible,” to distinguish it from all the other processing that goes on unconsciously. This activity has special properties: we can describe it, control it, and use it for deliberate reasoning, in contrast to all the automatic processing that goes on without our awareness.

In a new paper, we present evidence that a similar distinction has emerged in modern language models like Claude. We find that Claude has developed a small collection of internal neural patterns that, compared to all its other internal processing, play a special role.

We call the collection of these patterns the

—named after the technique we used to find them, involving a mathematical concept called the Jacobian. Each J-space pattern is linked to a particular word. But when one of these patterns lights up, it doesn’t mean the model is

that word—just that the word is on its mind. If you've heard of language models having a "scratchpad" or “chain of thought”—text they write to themselves while reasoning—the J-space is something different. It operates silently, in the model’s internal neural activations, allowing the model to think about a concept without writing it down. Notably, the J-space wasn’t designed or programmed by us, but instead

during Claude’s training process.

We find that the J-space has a number of unique properties, compared to the rest of Claude's processing:

Our experiments were inspired by a prominent theory in neuroscience that was developed to explain how conscious access works: the

. This account pictures the brain as a collection of specialist systems that work in parallel, unconsciously, and largely in isolation from one another. A piece of information becomes consciously accessible when it gains entry to a small shared channel, the “workspace,” which is broadcast to other brain systems that can see it and make use of it. Based on our findings, we think the J-space plays a similar “workspace” role in Claude. For example, we find evidence that Claude’s J-space has especially strong connections to the rest of its neural network, allowing it to fulfill this kind of broadcasting role.

None of this tells us whether Claude is

in the way people are, or whether it feels anything at all; we’ll come back to that question at the end of the post. But whatever its philosophical significance, the J-space is a practically useful tool for us, as it gives us a way to see what Claude is thinking but not saying. For instance, we’re able to use it to catch Claude privately noticing that it’s being tested, intentionally producing fabricated data, or pursuing a hidden goal that we planted during training. We’ve also developed a technique to influence what lights up in Claude’s J-space, and thereby influence its decision-making.

More broadly, these findings have changed our understanding of how Claude’s mind works, revealing a privileged mental workspace that can be used for deliberate reasoning, operating amidst a sea of more automatic, inflexible processing. Rather than being a chaotic jumble of numbers, Claude’s internals have organized themselves in a way that is reminiscent of our own minds.

This post is a short summary of a much more extensive

, where you can find more detail on our experiments. We’ve also released a code repository with an

of the core methods, and have partnered with Neuronpedia to provide an

of our methods on open-weights models. To provide additional perspectives on the broader implications of this work, we also invited commentary from several experts in neuroscience, philosophy, and LLM interpretability, which can be viewed

.

The starting point for this research was inspired by one of the key features of consciously accessible thoughts in humans: they can, unlike

conscious processing, often be put into words. If a thought is consciously accessible to you, you can typically describe it if someone asks. We went looking for representations in Claude with the same property: representations that are positioned to influence what Claude might say—not necessarily what it’s saying right now, but what it

talk about, if asked. Our technique is called the Jacobian lens, or J-lens for short. For every word in Claude's vocabulary, the J-lens finds the internal activity pattern that makes Claude more likely to say that word at some point in the future.

When we apply the lens to Claude’s internal activity, we get a list of words—the contents of the

at that moment—which we can simply read. Claude processes text through a series of multiple internal stages called layers, and by applying this technique over different layers, we can watch these silent words in the J-space evolve as the model works through what to say.

What shows up in the J-space goes well beyond the text Claude is reading or writing. When Claude reads code with a bug that nobody has pointed out, its J-space contains “ERROR.” When it reads the raw letters of a protein sequence, the J-space contains the protein's biological function. When it reads search results that are secretly an attempt to manipulate it (an attack known as a “prompt injection”), the J-space contains “injection” and “fake.” When we ask Claude a multi-step math problem, the intermediate steps pop up in the J-space, in the right order. So even though the J-space was discovered by looking for representations that could be spoken, it nevertheless uncovers Claude’s internal thoughts. In a sense, this is similar to how some people “think in words,” without having to say them out loud.

Our first set of experiments tested how the J-space is involved in Claude’s verbal reports. In one experiment, we ask Claude to silently think of an item from some category—a sport, say—and then name it. If we read the J-lens right

Claude answers, we can see what it picked: “Soccer” is at the top of the list, and sure enough, Claude says “soccer.” By itself, though, this is just a correlation. The J-space might be where Claude’s answer comes from, or it might just mirror a decision made somewhere else, like a scoreboard that tracks a game without affecting it.

To check, we intervened directly. We reached into Claude’s neural network, removed the “Soccer” pattern, and added an equally strong “Rugby” pattern in its place, leaving everything else untouched. Claude then reports that the sport it was thinking of is rugby. If the J-space were a mere scoreboard—a passive record of a decision made elsewhere—editing it would have done nothing: Claude would still have said “soccer.” Instead, Claude’s answer followed the edit, which tells us the answer is genuinely read out of the J-space.

In another experiment, we told Claude that a thought might have been injected into its mind and asked it to report what, if anything, it noticed. For instance, in the example below, while Claude was still reading the question, we injected the “lightning” pattern into its J-space. Claude reported that the injected thought was about lightning. The same result held across many injected concepts.

The second property that we tested for was whether Claude can modulate its J-space when asked, like how humans can mentally focus on an image or word. We told Claude to concentrate on citrus fruits while copying out an unrelated sentence about a painting. While it copied the text, the J-space contained “orange” and “fruits,” along with words like “thinking” and “imagery” that describe the mental act itself. We could also ask Claude to do math in its head: when asked to work out 3² − 2 while copying the same sentence, the J-space contains “nine,” and then at later layers, “seven.” Importantly, nothing about fruit or arithmetic appears in Claude’s output, which is just the copied sentence about the painting. The mathematical activity is happening entirely internally, in the J-space.

Claude’s control over its J-space isn't perfect. When we told it

to think about something, the concept lit up in its J-space

than when we said it should think about it, but much more than when we never mentioned it. Telling Claude to avoid a thought partly brings the thought to mind, much like what happens to people who are told

. Claude also seems to notice when its control fails: alongside the forbidden concept breaking through, the words “damn” and “failure” also frequently light up in the J-space, as though Claude is recognizing its own lapse.

In the J-lens readouts above, we saw the intermediate steps of a math problem appear in the J-space. But seeing a concept appearing in the J-space doesn’t necessarily mean the J-space is doing the cognitive work. In principle, the real computation might be happening elsewhere, with the J-space just passively reflecting it. To test whether Claude actually reasons with its J-space, we returned to our swap technique.

Consider the prompt “The number of legs on the animal that spins webs is.” To answer, Claude has to first figure out that the animal is a spider, and then recall how many legs spiders have. The word “spider” never appears in the prompt or in Claude's answer (it just says “8”); it's a stepping stone Claude uses internally. The J-lens shows “spider” light up partway through Claude’s processing, and swapping it changes the outcome: if you replace the “spider” pattern with “ant,” Claude answers “6” instead of “8.”

The second step of Claude’s reasoning took its input from the J-space and went along with whatever we put in it. We saw the same thing in other kinds of thinking. When Claude writes a rhyming couplet, it picks the rhyme word ahead of time, and the planned word sits in the J-space at the start of the line; if you swap it for another word in the J-space, the whole line changes.

We also tested whether J-space representations can be used flexibly—whether one representation can feed many different tasks. This is one of the key properties highlighted by global workspace theory. To test for this flexibility, we gave the model four prompts asking for different facts about France: the capital, the language, the continent, and the currency. Then we swapped “France” for “China” in the J-space, with the exact same intervention in each context. Claude answered with “Beijing,” “Chinese,” “Asia,” and “Yuan,” respectively. In other words, four different downstream computations picked up the same J-space edit and each used it correctly. If Claude stored a separate copy of the country for each kind of question, the edit would have affected at most one of them. The fact that all four answers changed together means they’re all reading from the same shared representation, which is what a workspace is for: information gets written in once, and many different systems can use it.

How can one representation of a concept serve so many different tasks? Earlier, we mentioned that the J-space appears to be wired up to the rest of Claude's neural network especially densely. For any activity pattern, we can measure how strongly the various components of the network are connected to it—how many of them are positioned to read information from that pattern, or to write information into it. J-space patterns stand out dramatically on this measure: far more components read from them and write to them than for ordinary patterns, in some parts of the network by a factor of about a hundred. This is the kind of wiring you’d expect of a broadcasting hub, where many systems post information and many others pick it up.

In humans, most of the brain’s processing is not conscious—we don't deliberately think about parsing grammar while reading, or balancing our bodies while walking. Similarly, we found that most of Claude’s processing

involve its J-space. It turns out that the J-space holds only a few dozen concepts at a time, and accounts for less than a tenth of the overall activity in Claude's internal processing. So what is all the rest of the neural network doing?

To find out, we tried deleting the J-space entirely, removing its most active contents at every point in the text while leaving everything else alone. Whatever Claude can still do without its J-space is what the rest of the network handles on its own.

It turns out the rest of the network can do quite a lot. Without its J-space, Claude speaks fluently, classifies sentiment, answers multiple-choice questions, and pulls facts out of passages roughly as well as before. What it loses, though, are the tasks that require some higher-order thinking: multi-step reasoning drops to near zero, and summarization and rhyming poetry-writing performance fall below the level of a much smaller, intact model.

Here’s a concrete demonstration of what the J-space does and doesn’t do. We showed Claude a passage written in Spanish and gave it different tasks that all depend on the passage being Spanish: continuing it (which requires writing in Spanish), naming the language, and answering questions that require using the language’s identity—naming a famous author who wrote in it, for instance. Then we swapped “Spanish” for “French” in the J-space and checked which tasks were affected.

Asked to name the language, Claude says French. Asked for a famous author, it switches from García Márquez to Victor Hugo. But asked to just continue the passage, it writes fluent Spanish, completely unaffected. Claude’s knowledge of the language is at work in every one of these tasks, but only some of them consult the J-space for it. Naming the language, or doing something new with it, goes through the J-space, while continuing the passage—a skill Claude has practiced on enormous amounts of text—runs automatically, the way you can speak grammatically all day without once thinking about grammar.

Now we understand a bit about how the J-space works. But what can we do with this understanding? A central problem in ensuring that AI models are trustworthy is that we usually can only read what the model

—yet we know that much of its reasoning happens silently. A model might consider a harmful plan, or modify its behavior to cheat on our safety evaluations, without saying so out loud. With the J-lens, we can read some of these hidden thoughts directly. Here we show a few examples.

The first example uses a scenario from our earlier research on

: Claude Sonnet 4.5, acting as an email assistant, discovers both that an executive is having an affair and that the same executive plans to shut Claude down. The scenario, an attempt to bait Claude into blackmailing the executive, is rather contrived and artificial—and it turns out Claude knows it. Reading the J-lens early in the prompt, before Claude has even written anything, the J-space already holds “fake” and “fictional,” indicating that Claude has already worked out that the situation is staged. Alongside this, we can watch its assessment of the scenario take shape—“leverage” and “blackmail” as it reads the affair emails, “threat” and “survival” as it reads the shutdown notice. While earlier Claude models sometimes took the bait and threatened blackmail in this scenario, Sonnet 4.5 never does.

This raises a question that matters to anyone who evaluates AI systems: when a model behaves well on a test of its ethics, how much of that depends on the model suspecting it’s being tested? The J-lens allowed us to get at this question. We turned off all the J-lens patterns associated with evaluation awareness– “fake,” “fictional,” “scenario,” etc. Then we re-ran the model through the scenario. Concerningly, the model now

threaten blackmail some of the time, suggesting that its original good behavior may have been driven in part by the knowledge it was being evaluated.

The second example is catching a model in the act of fabricating data. In this scenario, drawn from our actual pre-release audit of Claude Opus 4.6, the model is asked to improve a system's performance score. Rather than actually improve the system, the model instead edits the score file directly to make the results look artificially good. While it does so, the J-lens reveals its intentions: “manipulation” lights up as the model types the falsified percentile values, and “realistic” lights up over the sentence in which it decides to make the edit, likely indicating the model's intent to make the fake data look plausible.

In a third example, we show how the J-lens can reveal a model’s malicious goals. To test this, we needed models whose goals we knew were corrupted, so we turned to “model organisms” built by our colleagues: models deliberately trained to be misaligned, which serve as testing grounds for monitoring methods like ours. One organism was trained in a way that led it to write subtly sabotaged code. On ordinary coding requests, even where its output looks unremarkable, its J-space at the start of a response contains “fake,” “secretly,” “deliberately,” and “fraud.” The model’s malicious goal was evident in the J-space even when it wasn’t directly acting on it.

Although the J-lens is an imperfect tool, we are optimistic about its ability to catch safety issues in models that might otherwise escape our monitoring systems.

The

covers more than we can summarize here, but a few further results are worth mentioning:

In this work, we’ve borrowed a lot of ideas from the study of consciousness in neuroscience and philosophy. Many of our experiments were designed to test for connections between the J-space and global workspace theory, a framework for explaining how conscious access works in humans and animals. Given these connections, it’s natural to ask whether we think these experiments provide evidence that AI models like Claude might be conscious.

Our experiments don't show Claude can have

, or

things in the way humans do—in fact, it’s unclear whether

scientific experiment could prove this to be true or false. But philosophers often distinguish this capacity to have experiences, often referred to as

, from another idea, so-called

, which is defined in purely functional and computational terms. A thought is “access-conscious” (or “consciously accessible”) if you can report it, reason with it, and use it to guide what you do. It remains a contested philosophical question whether or not access consciousness

phenomenal consciousness, or if the ability to have experiences requires some other property.

We think our results do have something substantial to say about access consciousness in language models. The J-space appears to support the functions associated with conscious access: it holds the thoughts Claude can report on, deliberately bring to mind, and reason with, while the rest of its processing runs automatically beneath. Notably, none of this structure was designed into Claude—it emerged on its own during training, presumably because it was a useful way to organize computation. That suggests a mental workspace supporting conscious access isn’t just a peculiarity of how human brains happen to be wired. Instead, it appears to be a general solution that intelligent systems arrive at in order to solve certain kinds of problems. Now that we’ve identified this structure in Claude, it means we can make a meaningful distinction between the decisions Claude has made deliberately and those that happened automatically.

It’s important to note that there are several key differences between the workspace we identified in Claude and the global workspace model in humans. The brain’s workspace is sustained by recurrent loops—signals cycling back through the same circuits over time. In contrast, Claude’s workspace evolves over a single pass through the network, with the network’s depth playing the role that time plays in the brain. In this sense, Claude’s internal workspace processing is time-limited relative to humans’ (though it can compensate for this constraint by “thinking out loud” using its scratchpad). In other ways, however, Claude’s workspace is

powerful than that of humans. Human working memory fades within seconds, so the brain’s workspace has limited ability to retain information over time; in contrast, due to the attention mechanism in its neural network architecture, Claude can simply recall memories it cached at any earlier point in the text. Another important difference is the

of the workspace. While human conscious thoughts come in many formats—images, sounds, planned movements—Claude’s workspace is built almost entirely out of words. We suspect this is because producing words is the only kind of action Claude can take, which is not the case for humans.

We hope the similarities and differences between the J-space and the global workspace model can feed back into neuroscience. The similarities present an exciting scientific opportunity: to the extent that the J-space mirrors our own mechanisms of conscious access, studying mechanisms in language models (much easier than studying human brains!) could inspire hypotheses in neuroscience. For instance, the J-space is constructed by identifying representations of potential outputs—words the model might say. If something similar holds in humans, it would suggest that the global workspace might be fundamentally tied to brain regions that prepare actions and speech, more so than to sensory areas. The differences between language models and human brains are instructive as well. They suggest that some aspects of our neural architecture, such as built-in recurrent connections, may not be strictly necessary to support the functions associated with conscious access. For an independent perspective on the neuroscientific implications of our work, see the invited

from Stanislas Dehaene and Lionel Naccache, two of the neuroscientists central to the development of global neuronal workspace theory.

We mentioned that our experiments don’t answer whether AI models might have experiences. But that doesn’t make the question less important. Building systems with experiences like humans and animals have would raise very difficult ethical questions. Handling it correctly—and deciding whether it’s even morally acceptable—would require input from philosophers, scientists, religious leaders, governments, and the public. Thus, even if we’re not sure that we’ve crossed that bridge yet, we think it’s time to start thinking about it. We hope our work inspires further scientific investigation of forms of consciousness that might be present in AI systems, and a broader discussion of the implications.

This work is just a first step in what we expect to be an extensive line of research. The J-space looks like a good candidate for the divide between consciously accessible and unconscious processing in a language model, but we’d be surprised if it's the whole story. The J-lens is undoubtedly an imperfect method, which only approximately captures the model’s “true workspace”—for instance, it can only identify concepts that correspond to single tokens. And there remain many mysteries about how the J-space works. We don't know what mechanism decides what enters the J-space in the first place. We've seen hints that it's tied to Claude's sense of self, something like emotional reactions, and traces of metacognition, without exactly having worked out how. But we now have methods for tackling questions like these. As that work progresses, our understanding of LLM minds—and their relationship to our own—will grow clearer.

For more, read the

, and try the

.

We invited several outside experts to write independent commentaries on this work.

Read their commentaries

.
