from collections import Counter


def top_ips(lines, k):
    if k < 1:
        raise ValueError("k must be at least 1")
    counts = Counter()
    for line in lines:
        parts = line.split()
        if parts:
            counts[parts[0]] += 1
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return ranked[:k]
