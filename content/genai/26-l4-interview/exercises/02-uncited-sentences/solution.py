def has_marker(sentence):
    start = sentence.find("[")
    while start != -1:
        end = sentence.find("]", start)
        if end == -1:
            return False
        if sentence[start + 1 : end].isdigit():
            return True
        start = sentence.find("[", end)
    return False


def uncited_sentences(answer):
    sentences = []
    current = ""
    for index, char in enumerate(answer):
        current += char
        at_end = index == len(answer) - 1 or answer[index + 1] == " "
        if char in ".!?" and at_end:
            sentences.append(current.strip())
            current = ""
    if current.strip():
        sentences.append(current.strip())
    return [sentence for sentence in sentences if not has_marker(sentence)]
