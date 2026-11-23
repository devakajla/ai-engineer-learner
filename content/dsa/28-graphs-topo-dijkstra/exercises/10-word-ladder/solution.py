from collections import deque


def ladder_length(begin, end, words):
    pool = set(words)
    if end not in pool:
        return 0
    queue = deque([(begin, 1)])
    pool.discard(begin)
    while queue:
        word, length = queue.popleft()
        if word == end:
            return length
        for i in range(len(word)):
            for ch in "abcdefghijklmnopqrstuvwxyz":
                nxt = word[:i] + ch + word[i + 1:]
                if nxt in pool:
                    pool.remove(nxt)
                    queue.append((nxt, length + 1))
    return 0
