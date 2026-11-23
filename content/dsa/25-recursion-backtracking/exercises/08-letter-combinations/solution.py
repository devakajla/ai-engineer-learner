def letter_combinations(digits):
    letters = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl", "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}
    if not digits:
        return []
    result = []

    def go(i, current):
        if i == len(digits):
            result.append(current)
            return
        for ch in letters[digits[i]]:
            go(i + 1, current + ch)

    go(0, "")
    return result
