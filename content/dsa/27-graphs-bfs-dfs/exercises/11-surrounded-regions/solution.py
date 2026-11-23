def solve(board):
    rows = len(board)
    cols = len(board[0]) if board else 0
    safe = set()
    stack = []
    for r in range(rows):
        for c in range(cols):
            if (r in (0, rows - 1) or c in (0, cols - 1)) and board[r][c] == "O":
                safe.add((r, c))
                stack.append((r, c))
    while stack:
        r, c = stack.pop()
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] == "O" and (nr, nc) not in safe:
                safe.add((nr, nc))
                stack.append((nr, nc))
    return ["".join("O" if (r, c) in safe else "X" for c in range(cols)) for r in range(rows)]
