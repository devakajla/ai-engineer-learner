# Given. Do not change these three helpers.
def count_pairs(text):
    words = text.lower().split()
    counts = {}
    for i in range(len(words) - 1):
        first = words[i]
        second = words[i + 1]
        if first not in counts:
            counts[first] = {}
        counts[first][second] = counts[first].get(second, 0) + 1
    return counts


def to_chances(counts):
    table = {}
    for word, followers in counts.items():
        total = sum(followers.values())
        row = {}
        for nxt, count in followers.items():
            row[nxt] = round(count / total, 2)
        table[word] = row
    return table


def generate(start, table, max_words):
    words = [start]
    while len(words) < max_words:
        options = table.get(words[-1])
        if not options:
            break
        best = None
        best_chance = -1
        for candidate, chance in options.items():
            if chance > best_chance:
                best = candidate
                best_chance = chance
        words.append(best)
    return " ".join(words)


# Your task:
def train_and_generate(text, start, max_words):
    ...
