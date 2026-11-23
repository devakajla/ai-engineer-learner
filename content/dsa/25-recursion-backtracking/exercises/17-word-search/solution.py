def exist(board, word):
    rows, cols = len(board), len(board[0]) if board else 0
    used = set()

    def go(r, c, i):
        if i == len(word):
            return True
        if not (0 <= r < rows and 0 <= c < cols) or (r, c) in used or board[r][c] != word[i]:
            return False
        used.add((r, c))
        found = go(r + 1, c, i + 1) or go(r - 1, c, i + 1) or go(r, c + 1, i + 1) or go(r, c - 1, i + 1)
        used.remove((r, c))
        return found

    return any(go(r, c, 0) for r in range(rows) for c in range(cols))
