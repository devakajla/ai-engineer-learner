import heapq


def frequency_sort(s):
    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    h = [(-c, ch) for ch, c in counts.items()]
    heapq.heapify(h)
    parts = []
    while h:
        c, ch = heapq.heappop(h)
        parts.append(ch * -c)
    return "".join(parts)
