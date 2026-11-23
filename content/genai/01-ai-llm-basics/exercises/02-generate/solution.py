def next_word(word, table):
    options = table.get(word)
    if not options:
        return None
    best = None
    best_chance = -1
    for candidate, chance in options.items():
        if chance > best_chance:
            best = candidate
            best_chance = chance
    return best


def generate(start, table, max_words):
    words = [start]
    while len(words) < max_words:
        best = next_word(words[-1], table)
        if best is None:
            break
        words.append(best)
    return " ".join(words)
