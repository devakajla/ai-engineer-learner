import heapq


def min_join_cost(sticks):
    heap = list(sticks)
    heapq.heapify(heap)
    total = 0
    while len(heap) > 1:
        joined = heapq.heappop(heap) + heapq.heappop(heap)
        total += joined
        heapq.heappush(heap, joined)
    return total
