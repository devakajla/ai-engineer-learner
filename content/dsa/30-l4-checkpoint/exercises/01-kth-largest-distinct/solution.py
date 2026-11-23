import heapq


def kth_largest_distinct(nums, k):
    distinct = set(nums)
    if len(distinct) < k:
        return None
    return heapq.nlargest(k, distinct)[-1]
