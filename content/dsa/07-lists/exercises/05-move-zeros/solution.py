def move_zeros(nums):
    result = []
    zeros = 0
    for n in nums:
        if n == 0:
            zeros += 1
        else:
            result.append(n)
    return result + [0] * zeros
