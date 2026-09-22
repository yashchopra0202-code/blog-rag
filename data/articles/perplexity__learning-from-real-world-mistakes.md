---
url: https://www.perplexity.ai/hub/blog/learning-from-real-world-mistakes
title: Learning from Real-World Mistakes
site: perplexity
date: 2026-09-21
scraped_at: 2026-09-22T08:56:24+00:00
---

Post-training a Perplexity Computer model with user corrections and tool errors.

Contents

How users interact with our products in the real world is a valuable source for model training. The data is abundant, reflects the actual distribution of user tasks, and captures user corrections and tool failures that synthetic environments may miss.

A common way to learn from real-world data is rejection sampling fine-tuning: judge each session’s outcome, keep the successful ones, and train the model to imitate them. But a successful outcome does not mean every step was correct, so imitating the whole trajectory risks reinforcing bad intermediate behaviors in addition to good ones. Discarding unsuccessful sessions also loses critical evidence of where the model falls short.

We combine rejection sampling fine-tuning with hint-guided self-distillation to learn from both successful and unsuccessful sessions. A hint is a short corrective instruction grounded in information the model already had when it made the mistake. Useful steps from successful sessions remain imitation targets, while grounded hints turn avoidable mistakes into correction targets. In live use, the later trained checkpoint reduced tool-call failures by 21.2% relative to an earlier trained checkpoint.

User corrections and tool errors add supervision about what went wrong along the way, on top of whether the task ultimately succeeded. We apply this stage after reinforcement learning in synthetic environments to help close the gap between those environments and real-world use.

Synthetic tasks let us create controlled problems with outcomes that are easy to verify, but they are typically limited to a single prompt and can only cover the scenarios we explicitly design.

In contrast, users in real-world sessions bring diverse instructions, context, and tool combinations into sessions that unfold over multiple turns of interaction. Such real-world usage naturally yields two valuable signals of mistakes: user corrections reveal where the agent failed to deliver what they wanted, and tool errors show where its actions broke down in real environments. Our sampling pipeline respects users’ privacy and training choices by excluding sessions with personally identifiable information (PII) and from users who have opted out.

Real-world data therefore gives us failure cases that a synthetic environment may not expose and often comes with where the failure occurred already baked in.

When training on real-world data, standard

(RFT) selects successful sessions based on their final outcomes, without explicitly using user and tool feedback to distinguish good intermediate actions from bad ones. An agent may recover from a bad tool call or correct a mistake after user feedback and still deliver the right output at the end.

Discarding failed sessions also limits sample efficiency. A session that never reaches a good result could still reveal a clear, avoidable mistake as useful training signals.

We address these limitations by separating two decisions: which sessions contain behavior worth imitating, and which turns contain mistakes worth correcting. The data pipeline makes these decisions separately, then assigns model turns one of three treatments:

As a result, successful sessions can supply both imitation and correction targets, while unsuccessful sessions supply only correction targets. All remaining turns, including system, user, and tool output, stay as context.

The imitation part uses the standard RFT. The corrective part uses

(OPSD): the same model acts as teacher and student, with the teacher given privileged information. Here, that privileged information is a short hint explaining an avoidable mistake. We train the student to match the teacher’s next-token predictions without being handed the hint.

Both parts matter. Correction-only training can expose a shortcut: teacher and student can agree by ignoring context rather than learning the correction. The CE term anchors training to useful behavior, helping discourage agreement that comes from ignoring context.

The post-trained student then becomes a model option in Computer. Fresh sessions from live use pass through the same eligibility and privacy filters before entering another round of the training pipeline.

Next, we walk through a concrete example that contains both imitation and correction.

Consider an eventual successful session where the user asks for a comparison of asyncio changes in Python 3.13 using official documentation. Our tool documentation states that

returns a list of hits, each with a url field.

The model first runs a valid search for one version as part of gathering evidence for the comparison, which is a good behavior to imitate.

However, the next code-execution call incorrectly treats that list as a dictionary. The code tool returns

. Because the return type was documented before the call, it is a mistake the model should have been able to avoid. A hint with the right call can be generated to correct that action.

The training pipeline has four stages: select sessions and judge their outcomes, identify mistakes and create hints from user feedback and tool errors, generate next-token probabilities from both the teacher and the student, and train the model with a combined CE and KL loss.

The sampling pipeline draws from a training-eligible subset of real-world Computer sessions served by

. Training opt-outs and the pipeline’s PII-related exclusions are applied before selecting examples for this workflow.

The initial screening process selects for candidates rated 4 or 5 on a five-point task-difficulty scale by an LLM judge and splits them into 2 groups:

Two LLM judges then assess the final delivery against the user’s request; both judges must return a positive verdict to label the session as “successful”. For cases that deliver artifacts, the outcome stage can reconstruct and inspect the delivery, falling back to its text-based judgments if that stage fails. Sessions classified as incomplete, such as work waiting on the user, are excluded.

This step identifies potential sources of learning signals; however, not every error is attributable to the model, as some arise from ambiguous instructions or infrastructure failures. Later annotation determines which candidate mistakes are actually avoidable and suitable for training.

Consider a sample session in the user-feedback group, where the user asks, “How do I find my w3 on paychex”. The model treats “w3” as a typo for W-2, searches for W-2 instructions, and explains how to find that form. The user’s follow-up, “I meant the W-3 transmittal form,” identifies the mistake, even if the session ultimately succeeds.

The complaint helps locate the mistake, but the root cause is the earlier decision to reinterpret “w3” as W-2. The original request makes the mistake avoidable: the model could have preserved W-3 or asked for clarification. It turns out that the last assistant turn before the complaint is the root cause only about half of the time.

Our annotation pipeline maps cause and effect systematically within each user-feedback session. The annotator first screens for a missed requirement or an intention supported by earlier context. Three LLM judges then identify the responsible turns, requiring at least two to agree on a given turn. Sometimes an earlier statement explicitly establishes the requirement. In other cases, no single prior statement does so, but multiple pieces of the preceding conversation jointly make the intended behavior inferable. This design lets them connect a complaint to an earlier root mistake instead of attributing it solely to the last answer.

Before accepting a hint, the pipeline also checks that its corrective claims follow from information available before the marked turn. These checks are intended to reduce hindsight bias, where a new preference revealed in the complaint is treated as something the model should already have known.

In this example, the hint tells the model to search for the W-3 transmittal form on Paychex rather than W-2, or ask which form the user means if the request is ambiguous. The correction targets the earlier interpretation and search decision, not just the final answer. The original turn remains unchanged; the annotation adds

and a nonempty

Consider another session in the tool-error group with a search call where the agent searches with

, but the tool rejects it because the allowed values are “day,” “week,” or “month”. This is a clear schema violation.

The tool-error path uses deterministic rules for known mistakes and model judgment for ambiguous cases. An error message alone is also not enough to blame the model; a judged correction must point to something the model could have known from the tool schema, system instructions, or earlier conversation.

Here, the hint names the failed call, includes the validation error, and instructs the model to use an allowed value or omit the field if it is optional.

Once a turn is marked, the trainer runs the same GLM 5.2 checkpoint twice: once as the teacher and once as the student. The teacher sees the hint; the student does not.

Both passes use teacher forcing, where we feed the model the recorded session instead of letting it choose new tokens. The forward pass still produces a full next-token distribution at each step, but it is always conditioned on the fixed prefix from the recording, not on rollout tokens.

For the search example, the same model assigns much higher probability to “month” and less to “year” when given the hint. Training uses this distributional shift as a soft target.

The teacher’s predictions are detached, or stop-gradient: they supply a target but do not receive an update through the teacher pass. After the student’s pass, one optimizer step updates the shared model.

CE loss treats the recorded tokens selected for imitation as ground-truth targets and penalizes the model for assigning them low probabilities. This creates a hard imitation target.

At token position

, let

be the student’s probability of token

in the full vocabulary

. The recorded next token in the response or tool call is

, the one-hot target distribution is

Cross-entropy measures how well the student predicts that recorded token. With a one-hot target, it reduces to the negative log-probability assigned to

The CE mask

is

where the token should be imitated and

otherwise. Summing over the selected positions gives the imitation loss.

KL loss instead uses the teacher’s full next-token probability distribution

as a soft correction target. The teacher’s context includes the current hint and any earlier hints retained in that training segment; the student’s context is always hint-free.

The KL mask

is

where the token should be corrected and

otherwise; the CE and KL masks do not overlap. At these positions, forward KL penalizes disagreement between the teacher and student across the full vocabulary:

Both terms share one denominator rather than being normalized separately. This denominator counts the total tokens selected for imitation across the global training batch. The weight

controls the contribution of corrective training relative to imitation.

This shared normalization fits our training infrastructure’s single-denominator interface and recovers the standard SFT loss when

, simplifying baseline comparisons. Because CE tokens are much more abundant than KL tokens, using a shared denominator also avoids giving individual KL tokens disproportionately large weights in batches with few marked tokens.

Applied to the earlier examples, the turns containing the W-3/W-2 mix-up and the invalid search call receive KL. Other unmarked assistant content in a successful session still receives CE. Other assistant content in an unsuccessful session is retained as context but receives neither CE nor KL.

Our evaluations answer two separate questions. First, does a hint actually help the model correct an error when the hint is present? Second, does training help the model avoid that error later, without the hint? The first tests whether hints provide useful training signals. The second tests whether the model learns from them.

We test the first question before the training runs to make sure that hints can indeed steer the model away from the mistakes.

We regenerated marked user-feedback turns with and without a hint, using the same GLM-5.2 base model at temperature zero. A blind judge sees the later complaint, but neither the hint nor which condition produced the answer.

In the W-3 example, the hint shifts next-token probability toward “3” and away from “2” after the prefix “W-”.

On a larger 40-turn held-out sample backed by explicitly stated earlier evidence, the share judged fixed or on track rises from 40.0% without a hint to 75.0% with one. On another 40 turns backed by inferred intent, it rises from 32.5% to 80.0%.

In the search tool error example, a hint indeed shifts probability mass from the year token to the month token.

On a larger 985-turn held-out sample, we regenerate each turn four times with and without a hint using the same base model. A blind judge evaluates whether each regeneration avoids the original failure. Hints raise failure avoidance from 75.1% to 93.7%, a paired gain of 18.6 percentage points, and increase the share taking the corrected action from 60.6% to 82.3%. Gains are largest on errors that repeated sampling alone struggles to fix.

We next test whether the trained model makes fewer mistakes without receiving hints. We evaluate the stock model and various post-trained checkpoints on offline benchmark tasks and in live

ion

, checking for fewer tool failures and less user dissatisfaction.

The offline evaluation uses

, a representative Computer task set, and checks for skill loading, document review, and inline citations. We measure the share of tool calls whose results are explicitly flagged as errors across the evaluation trajectories.

In these evaluations, the recorded tool-error rate was 2.79% for stock GLM 5.2, 1.35% for the RFT-only checkpoint, and 0.87% for a RFT-plus-OPSD checkpoint. These checkpoints were trained on different data, so this is not a matched-data ablation of OPSD. Task-level benchmark results were mixed, so fewer tool errors alone does not necessarily translate into broad improvement in task success.

For online evaluation, we ran two separate A/B tests with about one hundred thousand users in each condition. In the first, an early RFT-plus-OPSD checkpoint had a slightly lower tool-failure rate than stock GLM 5.2, 2.82% versus 2.94%, but the difference was not statistically significant.

In the later test, we compared two RFT-plus-OPSD checkpoints: an earlier one (checkpoint one) and a later one (checkpoint two). Tool-call failures fell from 2.24% to 1.77% of calls with a recorded status. This was a statistically significant 21.2% relative reduction. We did not directly compare checkpoint two with stock GLM 5.2 online.

The user-feedback results are less conclusive. In the full later experiment, the average probability of strong dissatisfaction (medium or high) was 2.58% for checkpoint one and 2.54% for checkpoint two, with no statistically significant difference.

The central idea is to learn at the level of the decision, not just the session.

A successful outcome can hide mistakes, and an unsuccessful session can still reveal how to improve. We keep useful behavior from successful sessions as an anchor, use complaints and tool errors to identify avoidable failures, and train the model toward the predictions it makes when those mistakes and corrections are made explicit. Success provides behavior to preserve; failure provides direction for improvement.

Real-world use makes this approach especially useful. Real users bring goals, constraints, and workflows that are difficult to anticipate in a synthetic environment. Their corrections reveal requirements the model missed, while tool errors expose gaps between what the model attempted and what the environment allows. These signals complement outcome-based training: instead of asking only whether a task succeeded, we can ask where the model went wrong and what information could have helped it make a better decision.

The limits are equally important. Judges can be wrong, and correcting one turn does not guarantee that the full task succeeds. Our strongest post-training evidence is for tool reliability; the online tests did not establish a reduction in user dissatisfaction. The goal is not merely an agent that recovers after a correction. It is an agent that needs correction less often.
