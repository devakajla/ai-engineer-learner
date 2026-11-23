def is_isomorphic(s, t):
    forward = {}
    backward = {}
    for a, b in zip(s, t):
        if forward.get(a, b) != b or backward.get(b, a) != a:
            return False
        forward[a] = b
        backward[b] = a
    return True
