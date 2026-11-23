def min_add_to_make_valid(s):
    open_count = 0
    added = 0
    for ch in s:
        if ch == "(":
            open_count += 1
        elif open_count > 0:
            open_count -= 1
        else:
            added += 1
    return added + open_count
