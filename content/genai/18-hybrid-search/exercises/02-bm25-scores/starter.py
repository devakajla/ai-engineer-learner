import math

PUNCTUATION = ".,;:!?()\"'`"


def tokenize(text):
    words = []
    for word in text.lower().split():
        word = word.strip(PUNCTUATION)
        if word:
            words.append(word)
    return words


def bm25_scores(query, docs, k1=1.5, b=0.75):
    pass
