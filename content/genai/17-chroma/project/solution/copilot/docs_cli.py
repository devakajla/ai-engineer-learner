"""Index and search your docs. Usage:

    python -m copilot.docs_cli index docs
    python -m copilot.docs_cli search "how do I delete a task"
"""

import sys

from copilot.store import index_folder, open_collection, search

DB_PATH = ".chroma"


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("index", "search"):
        print(__doc__)
        return
    collection = open_collection(DB_PATH)
    if sys.argv[1] == "index":
        count = index_folder(collection, sys.argv[2])
        print(f"Indexed {count} chunks.")
        return
    for hit in search(collection, " ".join(sys.argv[2:])):
        print(f"{hit['score']:.3f}  {hit['source']} [{hit['heading']}]")
        print("       " + hit["text"][:100].replace("\n", " "))


if __name__ == "__main__":
    main()
