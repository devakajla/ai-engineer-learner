import heapq


def k_smallest_pairs(a, b, k):
    if not a or not b:
        return []
    h = [(a[i] + b[0], i, 0) for i in range(min(k, len(a)))]
    heapq.heapify(h)
    result = []
    while h and len(result) < k:
        _, i, j = heapq.heappop(h)
        result.append([a[i], b[j]])
        if j + 1 < len(b):
            heapq.heappush(h, (a[i] + b[j + 1], i, j + 1))
    return result
