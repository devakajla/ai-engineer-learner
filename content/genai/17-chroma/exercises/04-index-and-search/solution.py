# Given from earlier exercises. Do not change these.
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

def add_section(sections, heading, lines):
    text = "\n".join(lines).strip()
    if text:
        sections.append({"heading": heading, "text": text})


def split_markdown(md):
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


def chunk_document(name, md, max_chars):
    chunks = []
    for section in split_markdown(md):
        for text in pack_paragraphs(section["text"], max_chars):
            chunks.append({
                "id": f"{name}#{len(chunks)}",
                "text": text,
                "source": name,
                "heading": section["heading"],
            })
    return chunks

def add_chunks(collection, embed, chunks):
    if not chunks:
        return 0
    texts = [c["text"] for c in chunks]
    collection.upsert(
        ids=[c["id"] for c in chunks],
        documents=texts,
        embeddings=embed(texts),
        metadatas=[{"source": c["source"], "heading": c["heading"]} for c in chunks],
    )
    return len(chunks)

def search(collection, embed, query, k=3):
    count = collection.count()
    if k <= 0 or count == 0:
        return []
    vector = embed([query])[0]
    result = collection.query(query_embeddings=[vector], n_results=min(k, count))
    hits = []
    for i, chunk_id in enumerate(result["ids"][0]):
        metadata = result["metadatas"][0][i]
        hits.append({
            "id": chunk_id,
            "text": result["documents"][0][i],
            "source": metadata["source"],
            "heading": metadata["heading"],
            "score": 1 - result["distances"][0][i],
        })
    return hits


def index_and_search(collection, embed, name, md, query, max_chars=300, k=3):
    chunks = chunk_document(name, md, max_chars)
    add_chunks(collection, embed, chunks)
    return search(collection, embed, query, k)
