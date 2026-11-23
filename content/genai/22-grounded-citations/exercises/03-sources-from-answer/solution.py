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


def sources_from_answer(answer, hits):
    sources = []
    for n in extract_citations(answer):
        if 1 <= n <= len(hits):
            hit = hits[n - 1]
            sources.append({"n": n, "source": hit["source"], "heading": hit.get("heading", "")})
    return sources
