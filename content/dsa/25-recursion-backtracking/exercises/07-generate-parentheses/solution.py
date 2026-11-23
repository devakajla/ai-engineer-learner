def generate_parentheses(n):
    result = []

    def go(current, opened, closed):
        if len(current) == 2 * n:
            result.append(current)
            return
        if opened < n:
            go(current + "(", opened + 1, closed)
        if closed < opened:
            go(current + ")", opened, closed + 1)

    go("", 0, 0)
    return result
