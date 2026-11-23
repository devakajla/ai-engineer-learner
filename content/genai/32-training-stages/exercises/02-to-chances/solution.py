def to_chances(counts):
    table = {}
    for word, followers in counts.items():
        total = sum(followers.values())
        row = {}
        for nxt, count in followers.items():
            row[nxt] = round(count / total, 2)
        table[word] = row
    return table
