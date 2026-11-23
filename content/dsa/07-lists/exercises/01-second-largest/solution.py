def second_largest(nums):
    first = None
    second = None
    for n in nums:
        if first is None or n > first:
            second = first
            first = n
        elif n != first and (second is None or n > second):
            second = n
    return second
