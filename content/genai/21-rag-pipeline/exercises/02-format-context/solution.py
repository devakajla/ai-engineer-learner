def format_context(hits):
    blocks = []
    for i, hit in enumerate(hits, start=1):
        label = hit["source"]
        if hit.get("heading"):
            label = label + " > " + hit["heading"]
        blocks.append(f"[{i}] {label}\n{hit['text']}")
    return "\n\n".join(blocks)
