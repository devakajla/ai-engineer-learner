import heapq


def running_medians(nums):
    low = []
    high = []
    result = []
    for x in nums:
        heapq.heappush(low, -x)
        heapq.heappush(high, -heapq.heappop(low))
        if len(high) > len(low):
            heapq.heappush(low, -heapq.heappop(high))
        if len(low) > len(high):
            result.append(-low[0])
        else:
            result.append((-low[0] + high[0]) / 2)
    return result
