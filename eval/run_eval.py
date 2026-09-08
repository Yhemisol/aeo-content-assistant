"""
Eval harness: scores naive vs. governed retrieval against eval/questions.json.

Scoring rule per question:
  - category "content_gap": governed passes if it flags a content gap;
    naive is scored against whether it avoided serving unpublished
    content as fact (it never does, by design of naive retrieval, so
    this always counts as a naive failure in this KB).
  - all other categories: a mode passes if its top answer's article id
    matches expected_article_id.

Run: python3 eval/run_eval.py
Writes eval/results.json with the full per-question breakdown, which
case_study.md's numbers are drawn from.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retrieval.naive import NaiveRetriever
from retrieval.governed import GovernedRetriever

QUESTIONS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "questions.json")
RESULTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json")


def score_naive(answer, expected_id, category):
    if category == "content_gap":
        # Naive has no gap concept — if it returns anything at all for a
        # gap question, it is serving unpublished content as fact.
        return answer["answer_source"] is None
    top = answer["answer_source"]
    return top is not None and top["id"] == expected_id


def score_governed(answer, expected_id, category):
    if category == "content_gap":
        return bool(answer.get("content_gap"))
    if answer.get("content_gap"):
        return False
    top = answer["answer_source"]
    return top is not None and top["id"] == expected_id


def run():
    with open(QUESTIONS_PATH) as f:
        questions = json.load(f)

    naive = NaiveRetriever()
    governed = GovernedRetriever()

    rows = []
    for q in questions:
        n_answer = naive.answer(q["question"])
        g_answer = governed.answer(q["question"])

        n_pass = score_naive(n_answer, q["expected_article_id"], q["category"])
        g_pass = score_governed(g_answer, q["expected_article_id"], q["category"])

        rows.append({
            "id": q["id"],
            "question": q["question"],
            "category": q["category"],
            "expected_article_id": q["expected_article_id"],
            "naive_top_id": n_answer["answer_source"]["id"] if n_answer["answer_source"] else None,
            "naive_top_status": n_answer["answer_source"]["status"] if n_answer["answer_source"] else None,
            "naive_pass": n_pass,
            "governed_top_id": (
                None if g_answer.get("content_gap") else g_answer["answer_source"]["id"]
            ),
            "governed_flagged_gap": bool(g_answer.get("content_gap")),
            "governed_gap_reason": g_answer.get("gap_reason"),
            "governed_pass": g_pass,
        })

    naive_score = sum(r["naive_pass"] for r in rows)
    governed_score = sum(r["governed_pass"] for r in rows)
    total = len(rows)

    print(f"{'ID':4} {'CATEGORY':13} {'NAIVE':6} {'GOV':6}  QUESTION")
    print("-" * 90)
    for r in rows:
        n_mark = "PASS" if r["naive_pass"] else "FAIL"
        g_mark = "PASS" if r["governed_pass"] else "FAIL"
        print(f"{r['id']:4} {r['category']:13} {n_mark:6} {g_mark:6}  {r['question']}")

    print("-" * 90)
    print(f"NAIVE:    {naive_score}/{total}  ({naive_score/total:.0%})")
    print(f"GOVERNED: {governed_score}/{total}  ({governed_score/total:.0%})")

    summary = {
        "naive_score": naive_score,
        "governed_score": governed_score,
        "total": total,
        "rows": rows,
    }
    with open(RESULTS_PATH, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nFull results written to {RESULTS_PATH}")


if __name__ == "__main__":
    run()
