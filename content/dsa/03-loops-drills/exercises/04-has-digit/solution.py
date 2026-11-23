def has_digit(n, d):
    if n == 0:
        return d == 0
    while n > 0:
        if n % 10 == d:
            return True
        n //= 10
    return False
