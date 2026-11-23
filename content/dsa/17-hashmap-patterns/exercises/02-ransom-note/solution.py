def can_construct(note, magazine):
    available = {}
    for ch in magazine:
        available[ch] = available.get(ch, 0) + 1
    for ch in note:
        if available.get(ch, 0) == 0:
            return False
        available[ch] -= 1
    return True
