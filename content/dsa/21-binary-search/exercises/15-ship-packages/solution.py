def ship_capacity(weights, days):
    def days_needed(cap):
        count = 1
        load = 0
        for w in weights:
            if load + w > cap:
                count += 1
                load = w
            else:
                load += w
        return count

    lo, hi = max(weights), sum(weights)
    while lo < hi:
        mid = (lo + hi) // 2
        if days_needed(mid) <= days:
            hi = mid
        else:
            lo = mid + 1
    return lo
