def find_duplicates(nums):
    seen = set()
    repeated = set()
    for x in nums:
        if x in seen:
            repeated.add(x)
        else:
            seen.add(x)
    return sorted(repeated)
