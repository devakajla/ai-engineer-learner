import heapq


def k_closest(points, k):
    h = [(x * x + y * y, x, y) for x, y in points]
    heapq.heapify(h)
    result = []
    for _ in range(k):
        _, x, y = heapq.heappop(h)
        result.append([x, y])
    return result
