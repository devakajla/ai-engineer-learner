def max_vowels(s, k):
    vowels = "aeiou"
    count = 0
    for ch in s[:k]:
        if ch in vowels:
            count += 1
    best = count
    for i in range(k, len(s)):
        if s[i] in vowels:
            count += 1
        if s[i - k] in vowels:
            count -= 1
        best = max(best, count)
    return best
