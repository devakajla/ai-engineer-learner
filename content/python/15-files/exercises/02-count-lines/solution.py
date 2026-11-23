def count_lines(path):
    count = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                count += 1
    return count
