def count_provinces(connected):
    n = len(connected)
    visited = set()
    count = 0
    for start in range(n):
        if start in visited:
            continue
        count += 1
        visited.add(start)
        stack = [start]
        while stack:
            city = stack.pop()
            for other in range(n):
                if connected[city][other] == 1 and other not in visited:
                    visited.add(other)
                    stack.append(other)
    return count
