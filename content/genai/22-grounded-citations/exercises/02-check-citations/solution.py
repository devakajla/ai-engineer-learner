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


def check_citations(answer, n_hits):
    cited = extract_citations(answer)
    valid = [n for n in cited if 1 <= n <= n_hits]
    invalid = [n for n in cited if n < 1 or n > n_hits]
    return {"cited": valid, "invalid": invalid, "ok": bool(valid) and not invalid}
