def swap_ends(t):
    first, *middle, last = t
    return (last, *middle, first)
