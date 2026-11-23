import heapq


def merge_k_sorted(lists):
    h = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]
    heapq.heapify(h)
    result = []
    while h:
        v, i, j = heapq.heappop(h)
        result.append(v)
        if j + 1 < len(lists[i]):
            heapq.heappush(h, (lists[i][j + 1], i, j + 1))
    return result
