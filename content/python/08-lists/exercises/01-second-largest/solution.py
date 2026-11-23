def second_largest(nums):
    unique = []
    for n in nums:
        if n not in unique:
            unique.append(n)
    if len(unique) < 2:
        return None
    unique.sort()
    return unique[-2]
