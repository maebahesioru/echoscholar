# EchoScholar — an audio-first, source-grounded study companion

> ML Empowerment Build Challenge 3.0 — learn AI, build real-world projects, create impact

**Every answer can be heard. Every question can be listened to. Nothing is invented.**

EchoScholar turns a student's own course material (PDF textbooks, slide decks, lecture
transcripts, notes) into a **source-cited knowledge base** that speaks: grounded tutoring
with audio playback, an **audio quiz mode**, spoken feedback, and a **personalized audio
study brief** generated from the learner model.

It is built for **students who learn by listening** — including blind and low-vision
students, students with dyslexia or reading fatigue, commuters, and anyone who studies
better with their ears than their eyes. All content remains available as text with
citations; the audio is an equal path, not a fallback.

## The problem

1. Study material is scattered across lecture videos, textbooks and slides.
2. Generic AI chatbots answer from anywhere *except* the course — and hallucinate.
3. Screen-first study tools lock out students who cannot read comfortably for long
   periods: blind and low-vision learners, dyslexic learners, and anyone whose best
   focus happens away from a desk.

## What EchoScholar does

| Feature | Detail |
|---|---|
| **Multimodal ingestion** | PDF / PPTX / TXT / MD / VTT / SRT → source-linked passages (page / slide / timestamp) |
| **Source-grounded tutor** | Answers cite the exact passage `[unit_id]`; off-material questions are **declined**, never invented |
| **🔊 Spoken answers** | Every tutor answer is synthesized (edge-tts, cached) and **autoplays** in the UI |
| **🔊 Audio quiz** | MCQ / short / numerical questions with a Listen button; each question independently verified by a second model pass; repeated questions blocked |
| **🔊 Spoken feedback** | After grading, the model answer and explanation are read aloud |
| **🔊 Study brief** | One button → a personalized spoken brief: weak topics, mastery %, what to focus on next |
| **Learner model** | Bayesian Knowledge Tracing per topic, updated after every graded answer |
| **Accessible UI** | Large type, high contrast, keyboard-first (Ctrl+Enter to ask), ARIA labels, screen-reader-friendly structure |

## How it works

```
 upload ──► ingest (pdf/pptx/txt/vtt) ──► knowledge base (source-linked units)
                                              │
                        analyze ──► topic map ──► unit tags
                                              │
 question ──► TF-IDF retrieval ──► grounded answer + citations ──► 🔊 TTS (cached)
                                              │
 quiz scope ──► generation ──► independent verification ──► quiz ──► 🔊 TTS
                                              │
 answers ──► grading ──► BKT mastery ──► 🔊 personalized audio brief
```

- Retrieval: scikit-learn TF-IDF (local, no embedding service, any language) + optional LLM re-rank.
- Grounding: retrieval-scoped prompts, mandatory citations, explicit `NOT_COVERED` refusal.
- Audio: edge-tts neural voices, content-hash caching (repeat = instant, offline-friendly),
  multi-language voices configured via `AUDIO_VOICE`.
- LLM: any OpenAI-compatible endpoint (we run a DeepSeek-class model).

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp config.example.env .env      # set LLM_BASE_URL / LLM_API_KEY / LLM_MODEL
uvicorn server:app --port 7862  # open http://127.0.0.1:7862
```

Sample course included (`data/sample_course/`, regenerate with `python scripts/make_sample.py`).

## Impact

- **Accessibility**: an equal audio path for blind, low-vision and dyslexic students —
  a study workflow that works without a screen in front of your eyes.
- **Trust**: source-grounded answers with one-click verification; refusals instead of
  hallucinations — safe for unsupervised study.
- **Learning science**: mastery tracking + spoken briefs turn raw material into a
  personalized revision loop, useful for any student, essential for those who can't
  re-read pages to find what they missed.

## Repository layout

```
core/ingest.py    multimodal ingestion → source-linked units
core/retrieve.py  TF-IDF retrieval + topic mapping
core/tutor.py     grounded Q&A with citations and refusal
core/quiz.py      quiz generation + independent verification + novelty
core/learner.py   Bayesian Knowledge Tracing + study plan
core/audio.py     🔊 TTS layer: answers, feedback, briefs (edge-tts, cached)
server.py         FastAPI app (REST + static UI)
static/index.html audio-first single-page UI
scripts/          sample generator, evaluation, demo recorder
```

## Honest limitations

- Video ingestion takes transcripts (VTT/SRT); speech-to-text is left to the user's tool.
- Diagram content is not OCR'd; the system flags visuals rather than pretending.
- TTS needs network on first synthesis per phrase (then cached).
- The LLM judge in the evaluation is strict; see `docs/EVALUATION.md`.
