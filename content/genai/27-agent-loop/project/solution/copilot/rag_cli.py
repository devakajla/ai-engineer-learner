"""Talk to your docs. Usage:

    python -m copilot.docs_cli index docs
    python -m copilot.rag_cli                      # a chat, follow-up questions work
    python -m copilot.rag_cli "how do I delete a task"   # one question
"""

import sys

from copilot.llm import get_client
from copilot.rewrite import answer_with_history
from copilot.store import open_collection

DB_PATH = ".chroma"


def ask_once(client, collection, history, question):
    """One turn. Returns the new history (the plain question and the answer text)."""
    result = answer_with_history(client, collection, history, question)
    print(result["answer"])
    if not result["ok"]:
        print("Warning: the citations could not be checked. Do not trust this answer.")
    for source in result["sources"]:
        print(f"[{source['n']}] {source['source']} > {source['heading']}")
    return history + [
        {"role": "user", "content": question},
        {"role": "assistant", "content": result["answer"]},
    ]


def main():
    client = get_client()
    collection = open_collection(DB_PATH)
    if len(sys.argv) > 1:
        ask_once(client, collection, [], " ".join(sys.argv[1:]))
        return
    history = []
    print("Ask about your docs. Type 'quit' to stop.")
    while True:
        question = input("You: ").strip()
        if question.lower() in ("quit", "exit"):
            break
        if question:
            history = ask_once(client, collection, history[-6:], question)


if __name__ == "__main__":
    main()
