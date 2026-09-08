"""Loads the knowledge base articles from kb/*.json."""
import glob
import json
import os

KB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kb")


def load_articles(kb_dir=KB_DIR):
    """Returns a list of article dicts, sorted by id for stable ordering."""
    articles = []
    for path in sorted(glob.glob(os.path.join(kb_dir, "*.json"))):
        with open(path) as f:
            articles.append(json.load(f))
    return articles


def article_text(article):
    """The text a retriever searches over: title + body."""
    return f"{article['title']}\n\n{article['body']}"
