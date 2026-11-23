def allocate_books(pages, students):
    def needed(limit):
        count = 1
        current = 0
        for p in pages:
            if current + p > limit:
                count += 1
                current = p
            else:
                current += p
        return count

    lo, hi = max(pages), sum(pages)
    while lo < hi:
        mid = (lo + hi) // 2
        if needed(mid) <= students:
            hi = mid
        else:
            lo = mid + 1
    return lo
