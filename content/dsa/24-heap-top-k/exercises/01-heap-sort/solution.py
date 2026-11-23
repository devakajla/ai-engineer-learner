import heapq


def heap_sort(nums):
    h = []
    for x in nums:
        heapq.heappush(h, x)
    return [heapq.heappop(h) for _ in range(len(nums))]
