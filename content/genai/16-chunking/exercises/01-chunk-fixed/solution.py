def chunk_fixed(text, size, overlap=0):
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
