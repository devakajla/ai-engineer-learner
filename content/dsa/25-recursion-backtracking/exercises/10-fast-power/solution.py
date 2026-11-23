def fast_power(x, n):
    if n == 0:
        return 1
    half = fast_power(x, n // 2)
    if n % 2:
        return half * half * x
    return half * half
