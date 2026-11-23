def pack_paragraphs(text, max_chars):
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
