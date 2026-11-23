def clean_answer(text):
    return text.strip().lower().strip(".")


def majority_answer(answers):
    counts = {}
    for answer in answers:
        cleaned = clean_answer(answer)
        counts[cleaned] = counts.get(cleaned, 0) + 1
    best = None
    best_count = 0
    for answer, count in counts.items():
        if count > best_count:
            best = answer
            best_count = count
    return best
