def is_prime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


def primes_up_to(n):
    result = []
    for k in range(2, n + 1):
        if is_prime(k):
            result.append(k)
    return result
