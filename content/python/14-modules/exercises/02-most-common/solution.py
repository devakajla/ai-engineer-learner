from collections import Counter


def most_common_letter(text):
    counts = Counter(ch for ch in text.lower() if ch.isalpha())
    if not counts:
        return None
    best = max(counts.values())
    return min(ch for ch, n in counts.items() if n == best)
