"""
Interactive CLI for the AEO content assistant.

Ask a question, see how naive and governed retrieval answer it — including
the article metadata each answer is drawn from. Toggle modes live, or view
both side by side.

Usage:
    python3 chat.py

Commands (type at the prompt):
    /mode naive       switch to naive-only mode
    /mode governed    switch to governed-only mode
    /mode both        show both side by side (default)
    /help             show these commands again
    /quit             exit
"""
import sys

from retrieval.naive import NaiveRetriever
from retrieval.governed import GovernedRetriever

HELP_TEXT = """
Commands:
  /mode naive       switch to naive-only mode
  /mode governed    switch to governed-only mode
  /mode both        show both side by side (default)
  /help             show this message
  /quit             exit
Anything else is treated as a question to the knowledge base.
""".strip()


def format_naive_answer(result):
    if result["answer_source"] is None:
        return "  No match found."
    a = result["answer_source"]
    lines = [
        f"  Answer source: {a['title']}  (score={result['score']:.3f})",
        f"    status: {a['status']}   last_reviewed: {a['last_reviewed']}   owner: {a['owner']}",
        f"    taxonomy: {a['taxonomy_path']}",
        f"    \"{a['body'][:220]}{'...' if len(a['body']) > 220 else ''}\"",
    ]
    if a["status"] != "published":
        lines.append(
            f"    ⚠ this article is {a['status']} — naive retrieval doesn't know or care"
        )
    return "\n".join(lines)


def format_governed_answer(result):
    if result.get("content_gap"):
        lines = [f"  ⚑ CONTENT GAP FLAGGED  (best published score={result['score']:.3f})"]
        if result.get("gap_reason"):
            lines.append(f"    reason: {result['gap_reason']}")
        lines.append("    -> no answer given; this would route to a human / escalation queue")
        return "\n".join(lines)
    a = result["answer_source"]
    conf_note = "  (low confidence)" if result.get("low_confidence") else ""
    lines = [
        f"  Answer source: {a['title']}  (score={result['score']:.3f}){conf_note}",
        f"    status: {a['status']}   last_reviewed: {a['last_reviewed']}   owner: {a['owner']}",
        f"    taxonomy: {a['taxonomy_path']}",
        f"    \"{a['body'][:220]}{'...' if len(a['body']) > 220 else ''}\"",
    ]
    return "\n".join(lines)


def main():
    print("AEO Content Assistant — naive vs. governed retrieval")
    print("Loading knowledge base...")
    naive = NaiveRetriever()
    governed = GovernedRetriever()
    print(f"Loaded {len(naive.articles)} total articles "
          f"({len(governed.articles)} published).")
    print(HELP_TEXT)
    print()

    mode = "both"
    while True:
        try:
            raw = input(f"[{mode}] > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not raw:
            continue
        if raw in ("/quit", "/exit"):
            break
        if raw == "/help":
            print(HELP_TEXT)
            continue
        if raw.startswith("/mode"):
            parts = raw.split()
            if len(parts) == 2 and parts[1] in ("naive", "governed", "both"):
                mode = parts[1]
                print(f"Mode set to: {mode}")
            else:
                print("Usage: /mode naive|governed|both")
            continue

        question = raw
        if mode in ("naive", "both"):
            print("\nNAIVE:")
            print(format_naive_answer(naive.answer(question)))
        if mode in ("governed", "both"):
            print("\nGOVERNED:")
            print(format_governed_answer(governed.answer(question)))
        print()


if __name__ == "__main__":
    sys.exit(main())
