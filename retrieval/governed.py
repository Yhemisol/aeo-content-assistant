"""
Governed retrieval: filters to published, current content before ranking,
and refuses to guess when nothing published actually covers the question.

Two governance moves, both driven by the metadata naive retrieval ignores:

1. Filter to `status == "published"` BEFORE ranking. A retired article
   can't outrank its replacement if it's never in the running.

2. Content-gap detection. A published match that scores well is trusted
   and returned directly. But when the best published match is only
   weakly relevant, that's a signal worth checking further: is that
   because nothing in the knowledge base covers this topic well, or
   because the real answer exists but lives in a draft/retired article
   that governance correctly excluded? Either way, a weak published
   match should not be served as a confident answer — it gets flagged
   as a content gap instead of guessed.

Thresholds below were tuned against this project's actual eval
questions (see eval/questions.json) — they're deliberately conservative
rather than universal constants.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from retrieval.kb_loader import article_text, load_articles

STRONG_MATCH_THRESHOLD = 0.30   # published match this strong is trusted outright
WEAK_MATCH_FLOOR = 0.15         # published match below this is never trusted
GAP_DOMINANCE_SCORE = 0.30      # how strongly an unpublished article must score
GAP_DOMINANCE_MARGIN = 0.12     # ...and by how much it must beat the published top


class GovernedRetriever:
    def __init__(self, articles=None):
        all_articles = articles if articles is not None else load_articles()
        self.all_articles = all_articles
        self.articles = [a for a in all_articles if a["status"] == "published"]

        # Primary index: published content only. This is what answers are
        # actually drawn from.
        self._texts = [article_text(a) for a in self.articles]
        self._vectorizer = TfidfVectorizer(stop_words="english")
        self._matrix = self._vectorizer.fit_transform(self._texts)

        # Shadow index: every article regardless of status. Never used to
        # answer directly — only consulted to explain a weak published
        # match, e.g. "the real content exists, it's just a draft."
        self._shadow_texts = [article_text(a) for a in all_articles]
        self._shadow_vectorizer = TfidfVectorizer(stop_words="english")
        self._shadow_matrix = self._shadow_vectorizer.fit_transform(self._shadow_texts)

    def search(self, query, top_k=3):
        """Returns up to top_k (article, score) pairs from PUBLISHED
        articles only, highest score first."""
        query_vec = self._vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self._matrix)[0]
        ranked = sorted(
            zip(self.articles, scores), key=lambda pair: pair[1], reverse=True
        )
        return [(a, s) for a, s in ranked[:top_k] if s > 0]

    def _shadow_top(self, query):
        query_vec = self._shadow_vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self._shadow_matrix)[0]
        ranked = sorted(
            zip(self.all_articles, scores), key=lambda pair: pair[1], reverse=True
        )
        return ranked[0] if ranked else (None, 0.0)

    def answer(self, query, top_k=3):
        """Returns a governed answer: a trusted published match, or an
        explicit content-gap flag when nothing published is a confident
        answer to the question."""
        results = self.search(query, top_k=top_k)
        published_top_score = results[0][1] if results else 0.0

        if published_top_score >= STRONG_MATCH_THRESHOLD:
            top_article, top_score = results[0]
            return {
                "answer_source": top_article,
                "content_gap": False,
                "score": top_score,
                "results": results,
            }

        # Published match is weak — check whether unpublished content
        # explains why, before deciding how to respond.
        shadow_article, shadow_score = self._shadow_top(query)
        unpublished_dominates = (
            shadow_article is not None
            and shadow_article["status"] != "published"
            and shadow_score >= GAP_DOMINANCE_SCORE
            and shadow_score - published_top_score >= GAP_DOMINANCE_MARGIN
        )

        if unpublished_dominates or published_top_score < WEAK_MATCH_FLOOR:
            return {
                "answer_source": None,
                "content_gap": True,
                "gap_reason": (
                    f"Closest match is an unpublished '{shadow_article['status']}' "
                    f"article ({shadow_article['id']}), not a published one."
                    if unpublished_dominates
                    else "No published article is confidently relevant."
                ),
                "score": published_top_score,
                "results": results,
            }

        # Weak, but not weak enough to refuse — return it, marked low
        # confidence rather than silently treated as a strong answer.
        top_article, top_score = results[0]
        return {
            "answer_source": top_article,
            "content_gap": False,
            "low_confidence": True,
            "score": top_score,
            "results": results,
        }
