"""
Naive retrieval: pure text search, no awareness of governance metadata.

This is the baseline every RAG demo starts with — index everything,
rank by text similarity, return the top match. It doesn't know or care
whether an article is published, retired, or an unreviewed draft. If a
retired article's wording happens to overlap with the query, it can
easily outrank (or simply coexist with) the current one.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from retrieval.kb_loader import article_text, load_articles


class NaiveRetriever:
    def __init__(self, articles=None):
        self.articles = articles if articles is not None else load_articles()
        self._texts = [article_text(a) for a in self.articles]
        self._vectorizer = TfidfVectorizer(stop_words="english")
        self._matrix = self._vectorizer.fit_transform(self._texts)

    def search(self, query, top_k=3):
        """Returns up to top_k (article, score) pairs, highest score first.

        Searches ALL articles regardless of status — published, retired,
        or draft are all fair game.
        """
        query_vec = self._vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self._matrix)[0]
        ranked = sorted(
            zip(self.articles, scores), key=lambda pair: pair[1], reverse=True
        )
        return [(a, s) for a, s in ranked[:top_k] if s > 0]

    def answer(self, query, top_k=3):
        """Returns the top result as a naive 'answer', with no governance
        awareness at all — whatever scores highest is presented as fact."""
        results = self.search(query, top_k=top_k)
        if not results:
            return {"answer_source": None, "results": []}
        top_article, top_score = results[0]
        return {
            "answer_source": top_article,
            "score": top_score,
            "results": results,
        }
