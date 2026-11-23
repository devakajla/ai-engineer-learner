# Given from earlier exercises. Do not change these.
def extract_citations(answer):
    numbers = []
    i = 0
    while i < len(answer):
        if answer[i] == "[":
            j = answer.find("]", i)
            if j == -1:
                break
            inner = answer[i + 1:j]
            if inner.isdigit():
                n = int(inner)
                if n not in numbers:
                    numbers.append(n)
                i = j + 1
                continue
        i += 1
    return numbers


# Your task:
def check_citations(answer, n_hits):
    ...
