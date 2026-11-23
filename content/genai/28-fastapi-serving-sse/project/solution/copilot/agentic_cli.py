"""Ask your docs with the agentic graph. Usage:

    python -m copilot.docs_cli sync docs
    python -m copilot.agentic_cli "how do I remove a task"
"""

import sys

from copilot.agentic_rag import agentic_answer, build_agentic_graph
from copilot.llm import get_client
from copilot.store import open_collection

DB_PATH = ".chroma"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    graph = build_agentic_graph(get_client(), open_collection(DB_PATH))
    result = agentic_answer(graph, " ".join(sys.argv[1:]))
    print("path:", " -> ".join(result["path"]))
    print("searches:", result["tries"])
    print(result["answer"])
    if result["sources"]:
        print("sources:", ", ".join(result["sources"]))


if __name__ == "__main__":
    main()
