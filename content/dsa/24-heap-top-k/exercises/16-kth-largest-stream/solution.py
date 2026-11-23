import heapq


def kth_largest_stream(k, nums):
    h = []
    result = []
    for x in nums:
        heapq.heappush(h, x)
        if len(h) > k:
            heapq.heappop(h)
        result.append(h[0] if len(h) == k else None)
    return result
