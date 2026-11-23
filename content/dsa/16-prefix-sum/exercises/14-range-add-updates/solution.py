def apply_updates(n, updates):
    diff = [0] * (n + 1)
    for left, right, value in updates:
        diff[left] += value
        diff[right + 1] -= value
    result = []
    running = 0
    for i in range(n):
        running += diff[i]
        result.append(running)
    return result
