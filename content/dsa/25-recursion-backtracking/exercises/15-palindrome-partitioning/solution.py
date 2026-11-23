def partition(s):
    result = []
    current = []

    def go(start):
        if start == len(s):
            result.append(list(current))
            return
        for end in range(start + 1, len(s) + 1):
            piece = s[start:end]
            if piece == piece[::-1]:
                current.append(piece)
                go(end)
                current.pop()

    go(0)
    return result
