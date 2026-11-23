import heapq


def reorganize(s):
    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    h = [(-c, ch) for ch, c in counts.items()]
    heapq.heapify(h)
    result = []
    prev = None
    while h:
        c, ch = heapq.heappop(h)
        result.append(ch)
        if prev:
            heapq.heappush(h, prev)
            prev = None
        if c + 1:
            prev = (c + 1, ch)
    return "".join(result) if len(result) == len(s) else ""
