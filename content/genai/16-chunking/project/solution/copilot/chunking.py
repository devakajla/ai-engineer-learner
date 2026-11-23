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
