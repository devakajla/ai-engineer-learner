def longest_word(sentence):
    best = ""
    for w in sentence.split():
        if len(w) > len(best):
            best = w
    return best
