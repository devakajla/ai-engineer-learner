import heapq


def top_k_frequent(nums, k):
    counts = {}
    for x in nums:
        counts[x] = counts.get(x, 0) + 1
    h = [(-c, v) for v, c in counts.items()]
    heapq.heapify(h)
    return [heapq.heappop(h)[1] for _ in range(k)]
