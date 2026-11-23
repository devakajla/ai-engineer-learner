"""Ask a question about your docs. Usage:

    python -m copilot.docs_cli index docs
    python -m copilot.rag_cli "how do I delete a task"
"""

import sys

from copilot.llm import get_client
from copilot.citations import cited_answer
from copilot.store import open_collection

DB_PATH = ".chroma"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    collection = open_collection(DB_PATH)
    result = cited_answer(get_client(), collection, " ".join(sys.argv[1:]))
    print(result["answer"])
    print()
    if not result["ok"]:
        print("Warning: the citations could not be checked. Do not trust this answer.")
    for source in result["sources"]:
        print(f"[{source['n']}] {source['source']} > {source['heading']}")


if __name__ == "__main__":
    main()
