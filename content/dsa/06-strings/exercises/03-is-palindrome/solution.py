def is_palindrome(s):
    cleaned = ""
    for ch in s:
        if ch.isalnum():
            cleaned += ch.lower()
    return cleaned == cleaned[::-1]
