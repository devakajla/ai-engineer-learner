def two_sum(nums, target):
    index_of = {}
    for j, x in enumerate(nums):
        need = target - x
        if need in index_of:
            return [index_of[need], j]
        index_of[x] = j
    return []
