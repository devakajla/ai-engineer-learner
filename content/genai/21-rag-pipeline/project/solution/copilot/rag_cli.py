"""Ask a question about your docs. Usage:

    python -m copilot.docs_cli index docs
    python -m copilot.rag_cli "how do I delete a task"
"""

import sys

from copilot.llm import get_client
from copilot.rag import answer
from copilot.store import open_collection

DB_PATH = ".chroma"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    collection = open_collection(DB_PATH)
    result = answer(get_client(), collection, " ".join(sys.argv[1:]))
    print(result["answer"])
    print()
    for i, hit in enumerate(result["hits"], start=1):
        print(f"[{i}] {hit['source']} > {hit['heading']}")


if __name__ == "__main__":
    main()
