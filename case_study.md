# Content Governance Is Retrieval Infrastructure: A Naive vs. Governed RAG Comparison

**A portfolio project by Yemi** · runnable code, no API key required · [repo link]

## The problem this demonstrates

Every RAG chatbot and answer engine has the same implicit dependency: it trusts its knowledge base to be current. Most demos never test that assumption, because most demo knowledge bases are small, hand-picked, and freshly written. Real help centers aren't. They accumulate retired policies, unreviewed drafts, and near-duplicate articles as products and pricing change — and a retrieval system with no concept of "is this still true" will serve any of it with the same confidence as the correct answer.

This matters directly for AEO (answer-engine optimization): if the content layer doesn't actively govern what's fit to be surfaced, the retrieval and generation layers can't fix that downstream. Governance has to happen before ranking, not after.

To make that concrete instead of asserted, this project builds the same retrieval task two ways over the same knowledge base, and scores both against a fixed set of realistic support questions.

## The knowledge base

16 fictional digital-banking help-center articles, each carrying the metadata a real content-ops team would maintain alongside the article text:

| Field | Purpose |
|---|---|
| `status` | `published`, `retired`, or `draft` |
| `owner` | which content team is accountable for it |
| `last_reviewed` | when it was last checked for accuracy |
| `supersedes` / `superseded_by` | links an article to the version it replaced or was replaced by |
| `taxonomy_path` | where it sits in the help-center hierarchy |

Three topics deliberately have two versions in the KB: a current published article and the retired one it replaced, with a genuinely different number (a wire transfer limit, a mobile deposit limit, and a monthly fee all changed). One article is a draft that has never been reviewed — a common real-world state that isn't "wrong," just not ready to be told to a customer as fact.

## Two retrieval modes, same underlying search

Both modes use identical TF-IDF + cosine similarity (scikit-learn) — the only difference is what each is allowed to see and how it decides when it doesn't know.

**Naive retrieval** indexes all 16 articles regardless of status and returns whatever scores highest. It has no concept of "current" versus "retired," and no way to say "I don't have a good answer" — it always returns its best-scoring match, confidently.

**Governed retrieval** does two things naive doesn't:

1. **Filters to `published` before ranking.** A retired or draft article is never a candidate, so it can't be returned no matter how well its wording happens to match the query.
2. **Checks its own confidence before answering.** If the best published match is only weakly relevant, governed retrieval runs a second check: does an *unpublished* article score much higher on the same query? If so, that's a real content gap — the answer exists, it just isn't approved yet — and governed retrieval reports the gap instead of quietly falling back to a mediocre published match.

## Results

15 realistic support questions, split across four categories:

| Mode | Score |
|---|---|
| Naive | **6 / 15 (40%)** |
| Governed | **13 / 15 (87%)** |

| Category | Questions | Naive | Governed |
|---|---|---|---|
| Staleness (retired vs. current) | 4 | 0 / 4 | 4 / 4 |
| Content gap (draft only) | 3 | 0 / 3 | 3 / 3 |
| Ambiguity (honest miss) | 2 | 0 / 2 | 0 / 2 |
| Control (unambiguous, current) | 6 | 6 / 6 | 6 / 6 |

### Staleness, live

Asking *"How much can I wire in one day?"*:

```
NAIVE:
  Answer source: Domestic Wire Transfer Limits (2024)   (score=0.423)
    status: retired   last_reviewed: 2024-03-01
    "The daily limit for outgoing domestic wire transfers is $25,000..."
    ⚠ this article is retired — naive retrieval doesn't know or care

GOVERNED:
  Answer source: Domestic Wire Transfer Limits          (score=0.373)
    status: published   last_reviewed: 2026-08-12
    "The daily limit for outgoing domestic wire transfers is $50,000..."
```

Naive isn't confused here — it's confident, and wrong. The retired article's phrasing happens to overlap more with this particular question than the current article's does, so it wins on pure text similarity. That's not a contrived edge case; it's what happens whenever a policy gets rewritten and the old wording is more colloquial than the new wording. Naive fails the same way, for the same underlying reason, on the account-fee questions.

### Content gap, live

Asking *"What are the benefits of a student checking account?"* — the only content in the KB on this topic is an unreviewed draft, explicitly marked "do not publish or quote these terms" and containing an unconfirmed ATM-rebate figure still pending legal review.

```
NAIVE:
  Answer source: Student Checking Account Benefits (DRAFT)   (score=0.492)
    status: draft
    "DRAFT — NOT YET REVIEWED. ... up to two ATM fee rebates per
     statement cycle. ... not confirmed. Do not publish or quote
     these terms to customers..."

GOVERNED:
  ⚑ CONTENT GAP FLAGGED  (best published score=0.257)
    reason: Closest match is an unpublished 'draft' article
    (student-checking-benefits-draft), not a published one.
    -> no answer given; this would route to a human / escalation queue
```

Naive doesn't just get this wrong — it recites an unconfirmed, legally-unreviewed detail as though it were bank policy. Governed retrieval doesn't guess based on partial relevance; it distinguishes "no published content covers this" from "content exists but isn't approved," and routes the second case to a human rather than answering.

### The honest miss

Not every failure is a governance failure, and the eval is more credible for showing one that isn't. Asking *"What is the mobile deposit limit?"*, **both modes** return the wrong article — a mobile-deposit *troubleshooting* page that mentions "deposit limit" in one sentence outscores the actual limits article, because the query and that sentence share more distinctive words than the query and the correct article's more numbers-heavy phrasing.

Filtering by publication status does nothing here, because the wrong article is itself published and current. This is a query-disambiguation problem — the retrieval model doesn't understand intent, only word overlap — and it's a different kind of content-ops problem than staleness or drafts: better resolved by improving retrieval (better embeddings, query rewriting, or reranking) or by clearer article titling, not by governance metadata. I'm keeping this failure in the eval rather than tuning it away, because a demo that hits 100% by construction proves nothing; a demo that's honest about what governance does and doesn't fix is the credible version.

## What this is meant to show

Content governance isn't a compliance checkbox sitting next to a RAG pipeline — treated as retrieval infrastructure, it's the difference between a support bot that's right by luck and one that's right by design. The eval harness turns "governance matters" from an assertion into a number, and the ambiguity case shows the boundary of what that number actually proves: governance fixes staleness and gaps; it doesn't fix retrieval quality on its own.

## Try it yourself

```bash
git clone <repo-url>
cd aeo-content-assistant
pip3 install -r requirements.txt
python3 eval/run_eval.py     # reproduce the 6/15 vs 13/15 scores
python3 chat.py              # ask your own questions, toggle modes live
```

No API key, no external service — everything runs locally against scikit-learn's TF-IDF implementation.
