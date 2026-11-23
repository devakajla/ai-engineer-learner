def word_pattern(pattern, text):
    words = text.split()
    if len(words) != len(pattern):
        return False
    to_word = {}
    to_letter = {}
    for ch, word in zip(pattern, words):
        if to_word.get(ch, word) != word or to_letter.get(word, ch) != ch:
            return False
        to_word[ch] = word
        to_letter[word] = ch
    return True
