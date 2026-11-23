"""Try the search on a few built-in sentences: python -m copilot.search_cli "your question"."""

import sys

from copilot.search import search_texts

SAMPLE = [
    "Use the DELETE endpoint to remove a task.",
    "Send a POST request to create a new task.",
    "Log in with your email and password to get a token.",
    "The weather today is sunny.",
]


def main():
    question = " ".join(sys.argv[1:]) or "How do I get rid of a todo item?"
    for hit in search_texts(question, SAMPLE, k=3):
        print(f"{hit['score']:.3f}  {hit['text']}")


if __name__ == "__main__":
    main()
