def top_chars(text, n):
    counts = {}
    for ch in text.lower():
        if ch != " ":
            counts[ch] = counts.get(ch, 0) + 1
    ranked = sorted((-count, ch) for ch, count in counts.items())
    return [(ch, -neg) for neg, ch in ranked][:n]
