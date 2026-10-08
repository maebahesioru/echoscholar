# Devpost submission text — EchoScholar (ML Empowerment Build Challenge 3.0)

## Problem Statement

Students study from lecture videos, textbooks and slides scattered across platforms — and
generic AI chatbots answer from anywhere *except* the course material, or invent answers
when the material doesn't cover a question.

For students who learn by listening — blind and low-vision students, students with
dyslexia or reading fatigue, commuters, and anyone whose best focus happens away from a
desk — the problem is worse: almost every study tool is screen-first. Text-heavy
interfaces, silent quiz apps and silent feedback lock out the students who most need a
trustworthy study companion.

## Solution Overview

**EchoScholar** is an audio-first, source-grounded study companion. Upload your own course
material (PDF textbooks, PPTX slide decks, lecture transcripts, notes), and EchoScholar:

1. Builds a **source-cited knowledge base** — every passage keeps its exact origin
   (page / slide / timestamp).
2. Answers questions **only from that material**, with citations — and **declines**
   questions the material doesn't cover instead of hallucinating.
3. **Speaks**: every answer is read aloud automatically; quiz questions can be listened
   to; feedback is spoken; and one button plays a **personalized audio study brief**
   built from the learner model.
4. Tracks mastery per topic with **Bayesian Knowledge Tracing**, so the audio brief
   tells the student exactly what to review next.

The audio path is an equal path, not a fallback: the same content stays available as
text with one-click source verification for sighted users and screen readers.

## Key Features

- **Multimodal ingestion** — PDF / PPTX / TXT / MD / VTT / SRT with zero manual preprocessing.
- **Grounded tutor with refusal** — answers cite `[unit_id]`; off-material questions return
  an explicit refusal; a citation click opens the exact excerpt.
- **🔊 Spoken answers** — neural TTS (edge-tts), content-hash cached so repeats are instant.
- **🔊 Audio quiz mode** — MCQ / short / numerical questions, each **independently verified
  by a second model pass** (mismatched keys are dropped or repaired), with repetition
  blocked across sessions.
- **🔊 Spoken feedback** — model answer + explanation read aloud after grading.
- **🔊 Personalized audio study brief** — weak topics, mastery %, and next steps, spoken.
- **Learner model** — per-topic BKT mastery + a 7-day study plan weighted by forgetting curves.
- **Accessible UI** — large type, high contrast, keyboard-first (Ctrl+Enter to ask),
  ARIA-labelled controls.

## Target Users

- Blind and low-vision students who need study tools that work without a screen in front of them.
- Students with dyslexia or reading fatigue who absorb material better by listening.
- Commuters and auditory learners who want hands-free, eyes-free revision.
- Any student who wants a tutor they can trust: cited answers, honest refusals, no hallucination.

## Social Impact Statement

Education is the most scalable form of empowerment, and accessibility is where it most
often fails. Most "AI tutor" tools are built for sighted, screen-attached users;
EchoScholar was designed from the audio side first, so the students most often left
behind get the *better* experience, not a degraded one. Source grounding adds trust:
a study companion that refuses to invent is safe for unsupervised learning — and
teaching students that "I don't know" is an acceptable answer is itself a lesson
worth scaling.

## How We Built It

- **Python + FastAPI** backend; single-page vanilla-JS UI (no build step).
- **Retrieval**: scikit-learn TF-IDF (local, any language) + optional LLM re-ranking.
- **Grounding**: retrieval-scoped prompts, mandatory citations, explicit refusal token.
- **Quiz pipeline**: generate → structural validation → independent solve-verification → novelty hashing.
- **Audio**: edge-tts neural voices, disk-cached by content hash; multi-language voices via config.
- **Learner model**: Bayesian Knowledge Tracing with question-type aware priors.
- **LLM**: any OpenAI-compatible endpoint.

## Challenges

- Keeping an LLM honest about refusals needed a strict prompt contract plus UI-level flags.
- Independent question verification caught real answer-key errors that generation alone missed.
- Audio caching made the audio-first experience fast (repeat synthesis: instant).

## What's Next

- Speech-to-text for raw lecture videos; OCR for diagrams.
- Voice input so the whole loop is eyes-free.
- IRT/DKT extensions of the learner model; multi-language tutoring.

## Built with

python, fastapi, edge-tts, scikit-learn, bayesian-knowledge-tracing, llm, rag, accessibility
