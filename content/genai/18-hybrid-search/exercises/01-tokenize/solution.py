PUNCTUATION = ".,;:!?()\"'`"


def tokenize(text):
    words = []
    for word in text.lower().split():
        word = word.strip(PUNCTUATION)
        if word:
            words.append(word)
    return words
