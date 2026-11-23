"""Read a folder of markdown docs and turn it into chunks."""

from pathlib import Path

from copilot.chunking import chunk_markdown


def load_docs(folder):
    """All .md files under the folder as (relative path, text), sorted by path."""
    root = Path(folder)
    if not root.is_dir():
        raise FileNotFoundError(f"docs folder not found: {folder}")
    docs = []
    for path in sorted(root.rglob("*.md")):
        docs.append((path.relative_to(root).as_posix(), path.read_text(encoding="utf-8")))
    return docs


def ingest_folder(folder, max_chars=800):
    """Every chunk of every doc in the folder."""
    chunks = []
    for source, text in load_docs(folder):
        chunks.extend(chunk_markdown(text, source, max_chars))
    return chunks
