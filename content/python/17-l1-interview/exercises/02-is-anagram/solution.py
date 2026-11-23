def is_anagram(a, b):
    def clean(s):
        return sorted(ch for ch in s.lower() if ch != " ")

    return clean(a) == clean(b)
