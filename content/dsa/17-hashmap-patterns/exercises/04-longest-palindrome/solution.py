def longest_palindrome(s):
    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    length = 0
    odd = False
    for n in counts.values():
        length += n // 2 * 2
        if n % 2 == 1:
            odd = True
    return length + 1 if odd else length
