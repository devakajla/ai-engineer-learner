"""Print the chunks of a docs folder: python -m copilot.ingest_cli docs."""

import sys

from copilot.ingest import ingest_folder


def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else "docs"
    chunks = ingest_folder(folder)
    for chunk in chunks:
        print(f"{chunk['id']:<24} [{chunk['heading']}] {len(chunk['text'])} chars")
    print(f"{len(chunks)} chunks")


if __name__ == "__main__":
    main()
