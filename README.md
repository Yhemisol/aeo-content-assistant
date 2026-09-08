# AEO Content Assistant

A portfolio project demonstrating **AEO / content-governance** discipline in a RAG chatbot.

It runs two retrieval modes side by side over the same fictional digital-banking help-center knowledge base:

- **Naive retrieval** — pure text search (TF-IDF + cosine similarity), no awareness of article status, freshness, or supersession.
- **Governed retrieval** — filters to published, current (non-superseded) content before ranking, and explicitly flags gaps instead of guessing.

An eval harness scores both modes against realistic support questions to make the difference concrete, not just asserted.

See `case_study.md` (added at the end of the build) for the full writeup, and `chat.py` to try it live.

## Setup

```
pip3 install -r requirements.txt
```

No API key, no external service — everything runs locally with scikit-learn.

## Project structure

```
kb/          16 help-center articles as JSON, each with governance metadata
retrieval/   naive.py and governed.py retrieval implementations
eval/        eval question set + scoring harness
chat.py      interactive CLI — toggle between modes live
case_study.md
```
