# Step 9 — Chunk the docs

Copilot can search texts. Now it needs real texts to search. In this step you read a folder of markdown docs and cut it into chunks, each with a `source` and a `heading` for citations later.

Make a `docs/` folder in your project and put a few markdown files in it. Any API docs you like will do. If you have your TaskFlow project from the FastAPI track, write one file per topic (`tasks.md`, `auth.md`).

### 1. The cutting functions: `copilot/chunking.py`

These are the three functions you wrote in lesson 16, plus one that combines them. Pure functions, easy to test.

```python
"""Cut documents into chunks. Pure functions, no model calls."""


def chunk_fixed(text, size, overlap=0):
    """Pieces of at most `size` characters. Each starts `size - overlap` after the one before."""
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError("size must be positive and overlap must be between 0 and size - 1")
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + size])
        if start + size >= len(text):
            break
        start += size - overlap
    return chunks


def pack_paragraphs(text, max_chars):
    """Join neighbouring paragraphs while the chunk stays within max_chars."""
    if max_chars <= 0:
        raise ValueError("max_chars must be positive")
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""
    for paragraph in paragraphs:
        if current == "":
            current = paragraph
        elif len(current) + 2 + len(paragraph) <= max_chars:
            current = current + "\n\n" + paragraph
        else:
            chunks.append(current)
            current = paragraph
    if current:
        chunks.append(current)
    return chunks


def add_section(sections, heading, lines):
    text = "\n".join(lines).strip()
    if text:
        sections.append({"heading": heading, "text": text})


def split_markdown(md):
    """Sections as {"heading", "text"}. Lines inside code fences are never headings."""
    sections = []
    heading = ""
    lines = []
    in_fence = False
    for line in md.splitlines():
        if line.startswith("```"):
            in_fence = not in_fence
        stripped = line.lstrip("#")
        level = len(line) - len(stripped)
        is_heading = not in_fence and 1 <= level <= 6 and stripped.startswith(" ")
        if is_heading:
            add_section(sections, heading, lines)
            heading = stripped.strip()
            lines = []
        else:
            lines.append(line)
    add_section(sections, heading, lines)
    return sections


def chunk_markdown(md, source, max_chars=800):
    """Chunks for one markdown file, each {"id", "source", "heading", "text"}.

    Cut at headings first. A section longer than max_chars is packed by paragraph,
    and a paragraph that is still too long is cut by size, with a small overlap.
    """
    chunks = []
    for section in split_markdown(md):
        if len(section["text"]) <= max_chars:
            pieces = [section["text"]]
        else:
            pieces = []
            for packed in pack_paragraphs(section["text"], max_chars):
                if len(packed) <= max_chars:
                    pieces.append(packed)
                else:
                    pieces.extend(chunk_fixed(packed, max_chars, max_chars // 10))
        for piece in pieces:
            chunks.append({
                "id": f"{source}:{len(chunks)}",
                "source": source,
                "heading": section["heading"],
                "text": piece,
            })
    return chunks
```

Why this order of tries? Headings are the best cuts, because a writer chose them. Paragraphs are the next best. A fixed cut is the last resort, for a block of text with no structure.

The `id` is `<file>:<number>`. It is **stable**: the same docs always give the same ids. In step 10 the vector database uses it to update a chunk instead of storing it twice.

### 2. Read the folder: `copilot/ingest.py`

```python
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
```

Two small best practices: a clear error when the folder is missing, and `sorted(...)` so the order (and so the ids) does not change between runs or computers.

### 3. Look at your chunks

Add `copilot/ingest_cli.py`:

```python
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
```

```bash
uv run python -m copilot.ingest_cli docs
```

Read the list. Are there tiny chunks (a few words)? Huge ones? Try `max_chars=400` and `1500` in `ingest_folder` and see how the count changes. **Always look at your chunks.** Most search problems start here.

### 4. Commit

```bash
git add -A && git commit -m "Add chunking and docs ingestion"
```

### Expected structure

```
devdocs-copilot/
├── copilot/
│   ├── __init__.py
│   ├── chunking.py
│   ├── cli.py
│   ├── embed.py
│   ├── ingest.py
│   ├── ingest_cli.py
│   ├── llm.py
│   ├── memory.py
│   ├── prompts.py
│   ├── qa.py
│   ├── schemas.py
│   ├── search.py
│   ├── search_cli.py
│   ├── similarity.py
│   ├── spec_tools.py
│   ├── summary.py
│   └── tools.py
├── docs/            (your markdown files)
├── .env.example
├── .gitignore
├── pyproject.toml
└── uv.lock
```

### Checkpoint

The hidden tests check `chunk_fixed`, `pack_paragraphs`, `split_markdown` (including code fences), `chunk_markdown` (ids, source, heading, long sections), and `ingest_folder` on a temporary folder (sorted order, nested folders, a missing folder). Steps 1 to 8 must keep working.
