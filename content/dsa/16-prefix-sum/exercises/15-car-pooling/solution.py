def car_pooling(trips, capacity):
    last = max((end for _, _, end in trips), default=0)
    diff = [0] * (last + 1)
    for people, start, end in trips:
        diff[start] += people
        diff[end] -= people
    inside = 0
    for change in diff:
        inside += change
        if inside > capacity:
            return False
    return True
