def count_multiples(n, k):
    count = 0
    for i in range(1, n + 1):
        if i % k == 0:
            count += 1
    return count
