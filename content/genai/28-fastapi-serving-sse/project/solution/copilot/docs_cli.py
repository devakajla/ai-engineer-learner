"""Index and search your docs. Usage:

    python -m copilot.docs_cli index docs
    python -m copilot.docs_cli sync docs
    python -m copilot.docs_cli search "how do I delete a task"
    python -m copilot.docs_cli vector "how do I delete a task"
    python -m copilot.docs_cli keyword "error 429"
"""

import sys

from copilot.hybrid import hybrid_search, keyword_search
from copilot.store import index_folder, open_collection, search
from copilot.sync import load_manifest, save_manifest, sync_folder

DB_PATH = ".chroma"
MANIFEST_PATH = "manifest.json"


def show(hits):
    for hit in hits:
        score = f"{hit['score']:.3f}" if "score" in hit else "-----"
        print(f"{score}  {hit['source']} [{hit['heading']}]")
        print("       " + hit["text"][:100].replace("\n", " "))


def main():
    commands = ("index", "sync", "search", "vector", "keyword")
    if len(sys.argv) < 3 or sys.argv[1] not in commands:
        print(__doc__)
        return
    collection = open_collection(DB_PATH)
    command, rest = sys.argv[1], sys.argv[2:]
    if command == "index":
        print(f"Indexed {index_folder(collection, rest[0])} chunks.")
    elif command == "sync":
        manifest = load_manifest(MANIFEST_PATH)
        report = sync_folder(collection, rest[0], manifest)
        save_manifest(MANIFEST_PATH, manifest)
        print(report)
    elif command == "search":
        show(hybrid_search(collection, " ".join(rest)))
    elif command == "vector":
        show(search(collection, " ".join(rest)))
    else:
        show(keyword_search(collection, " ".join(rest), k=3))


if __name__ == "__main__":
    main()
