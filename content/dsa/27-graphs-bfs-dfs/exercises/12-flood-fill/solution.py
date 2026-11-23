def flood_fill(image, sr, sc, color):
    result = [list(row) for row in image]
    old = image[sr][sc]
    visited = {(sr, sc)}
    stack = [(sr, sc)]
    while stack:
        r, c = stack.pop()
        result[r][c] = color
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < len(image) and 0 <= nc < len(image[0]) and image[nr][nc] == old and (nr, nc) not in visited:
                visited.add((nr, nc))
                stack.append((nr, nc))
    return result
