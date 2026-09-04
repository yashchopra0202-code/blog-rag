---
url: https://research.google/blog/advancing-amie-towards-expert-level-audio-visual-clinical-consultations/
title: Advancing AMIE towards expert-level audio-visual clinical consultations
site: google-research
date: 
scraped_at: 2026-09-04T13:16:06+00:00
---

August 11, 2026

Anil Palepu, Senior Research Scientist, and Mike Schaekermann, Research Lead, Google

We advance AMIE, our research medical AI system, to conduct real-time video consultations, with a first-of-its-kind demonstration of expert-level performance in a randomized controlled study with simulated consultations.

When a physician meets a patient, the consultation extends far beyond the words exchanged. The physician observes the patient's gait, registers visible signs of discomfort, notes their breathing, and guides the patient through physical examination maneuvers. This continuous stream of visual and auditory information is seamlessly integrated with the spoken clinical history. These non-verbal visual and auditory cues are central to effective diagnosis, patient trust, and clinical communication.

AI systems capable of clinical reasoning and dialogue have the potential to dramatically increase access to medical expertise and care, fostering a future where physicians can focus their time on the most meaningful aspects of patient interactions. In early work, the Articulate Medical Intelligence Explorer (

), our research AI system for clinical reasoning and dialogue, demonstrated expert-level performance in

and proved effective as a

. Recently, we advanced AMIE’s capabilities

towards

.

We have also extended AMIE's capabilities towards specialist-level evaluations in

and

, and

over

, in simulated settings with patient actors. In parallel, we have begun translating these research advances towards clinical practice, through a framework for

, as well as our first real-world clinical studies including a

with

, and an

in partnership with

.

Despite these advances, a fundamental constraint in our research remained that text-based interfaces discard the visual and auditory dimensions of clinical practice. Patients must translate complex physical symptoms into written descriptions, a process that discards diagnostic information and can negatively affect patients with limited digital or health literacy. Text-only systems cannot independently observe the visual and auditory cues that inform clinical reasoning, nor can they guide patients through the physical examination maneuvers that shape differential diagnosis.

Today, in “

, we present AMIE in a real-time video configuration, AMIE (Video), that addresses these limitations. Built on

and

, AMIE (Video) conducts synchronous clinical video consultations, perceiving non-verbal clinical cues, guiding patient actors through virtual physical examinations, and reasoning diagnostically, all in real time. In a multi-arm randomized study with 100 scenarios, 300 live consultations, and a group of 30 board-certified primary care physicians (PCPs), we present the first demonstration of an AI system exhibiting expert-level performance in real-time clinical video consultations.

Conducting an effective clinical conversation over video requires balancing competing demands: the system must respond to patients at natural conversational speed while simultaneously performing careful clinical reasoning and continuously processing visual and auditory streams. Currently, a single agent cannot satisfy all these requirements. Deep reasoning takes time, but conversational pauses erode patient trust and rapport.

To address this challenge, AMIE (Video) uses an asynchronous multi-agent architecture that divides labor across three specialized agents working continuously in parallel:

This decoupled design allows AMIE (Video) to maintain natural conversational latency while performing diagnostic reasoning and audio-visual perception that would otherwise introduce unacceptable delays. Automated evaluations confirm that each agent in this three-agent architecture makes important contributions towards improvements on clinical metrics, such as competency in history-taking, clinical reasoning and treatment recommendations, as well as on metrics related to dialogue quality, including patient-centered communication skills and response latency.

A key challenge in building audio-visual medical AI is characterizing a system's perceptual and reasoning capabilities at scale. To guide development, we derived a taxonomy of clinical audio-visual competencies relevant to telehealth from the medical literature, covering non-verbal visual cues, auditory signals, and physical examination maneuvers. We then built an automated evaluation suite structured around this taxonomy.

This evaluation framework combines targeted single-turn audio-visual assessments with multi-turn simulated audio consultations. The single-turn audio-visual assessments test specific instances of clinical perception and reasoning (e.g., correctly identifying anatomical laterality or recognizing signs of respiratory distress). And the multi-turn simulated audio consultations assess end-to-end conversational performance while injecting visual cues as textual descriptions into the simulation (for example, an AI patient simulator for a Parkinson’s scenario prompted to show their handwriting may inject a verbal description of “[holding up paper to camera showing cramped, tiny script]”). Together, these complementary evaluations enabled rapid iteration on system design and richly characterized capabilities and failure modes of AMIE (Video) prior to human evaluation.

To evaluate clinical competence in the more challenging and realistic setting of an end-to-end audio-visual clinical consultation, we conducted a large-scale, randomized

(OSCE) study with a synchronous video consultation interface.

To cover a breadth of medical conditions in our evaluation, the study spanned 100 clinical scenarios covering five body systems, including cardiopulmonary, abdominal, head/eyes/ears/nose/throat (HEENT), neurological/psychiatric, and musculoskeletal conditions. Fifteen trained patient actors carried out 300 standardized consultations across three study arms:

An independent panel of 20 experienced primary care physicians evaluated all consultations using established clinical rubrics, including both general clinical competency scales and detailed case-specific scoring criteria tailored to each scenario.

Across core clinical competencies, history-taking thoroughness, diagnostic accuracy, management appropriateness, and communication quality, clinical evaluators rated AMIE (Video) on par with PCPs. AMIE (Video) also matched or exceeded AMIE (Text) on these dimensions.

AMIE (Video) was rated significantly higher, on average, than both PCPs and AMIE (Text) eliciting physical signs and proactively guiding patient actors through virtual examination maneuvers. This advantage was also reflected in case-specific perception and examination rubric scores.

Patient actors strongly preferred the synchronous video interface over text-based chat, rating it as significantly easier to use and more effective for communicating health concerns. They also rated AMIE (Video) favorably on empathy, rapport, and confidence in care compared to both PCPs and AMIE (Text).

This research has important limitations and it is critical to interpret these results within the context of these limitations. This study was conducted entirely with professional patient actors in simulated clinical settings, not with real patients presenting with their own health conditions. Patient actors, however skilled, cannot fully replicate the complexity and unpredictability of real clinical encounters, and the scenarios were limited to conditions that can be authentically portrayed through acting, omitting important clinical presentations where audio-visual perception would be diagnostically consequential. Beyond the scope of the study, targeted automated evaluations revealed occasional perceptual and reasoning errors, despite overall high-quality conversation and diagnostic accuracy, and the system still exhibits intermittent technical issues that can disrupt conversational naturalness. Given the prototype nature of Project Astra, this includes technical considerations that future development may address at a system level that go beyond the specific medical application explored in this work. Assessing these findings in studies with real patients and real clinical conditions is an essential next step before any conclusions about real-world utility can be drawn.

This work demonstrates that the transition from text-based to audio-visual clinical AI is achievable at expert-level quality. AMIE (Video) engages with the perceptual richness of clinical practice, observing non-verbal cues, guiding physical examination, and conversing naturally through spoken dialogue — capabilities that more closely approximate the experience of a telehealth video encounter.

Important questions remain on the path towards responsible real-world evidence. Our findings need to be validated with real patients, expanded to encompass clinical presentations that cannot be enacted, and supported by robust safety frameworks. We have already taken early steps in this direction: a

with Beth Israel Deaconess Medical Center provided initial evidence for the safety and utility of text-based AMIE in clinical practice, and our

with Included Health is further evaluating AI in real-world virtual care. Together, these research experiences will help inform how audio-visual capabilities might be responsibly integrated into clinical practice. While much remains to be done, these results mark an important milestone towards AI systems that could one day augment care by engaging with the sensory complexity of clinical practice.

September 3, 2026

September 3, 2026

September 1, 2026
