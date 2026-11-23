def _is_pal(s, i, j):
    while i < j:
        if s[i] != s[j]:
            return False
        i += 1
        j -= 1
    return True


def valid_palindrome_ii(s):
    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return _is_pal(s, left + 1, right) or _is_pal(s, left, right - 1)
        left += 1
        right -= 1
    return True
