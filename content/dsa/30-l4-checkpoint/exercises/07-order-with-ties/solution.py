import heapq


def alien_order(words):
    letters = {ch for word in words for ch in word}
    graph = {ch: set() for ch in letters}
    indegree = {ch: 0 for ch in letters}
    for first, second in zip(words, words[1:]):
        for a, b in zip(first, second):
            if a != b:
                if b not in graph[a]:
                    graph[a].add(b)
                    indegree[b] += 1
                break
        else:
            if len(first) > len(second):
                return ""
    heap = [ch for ch in letters if indegree[ch] == 0]
    heapq.heapify(heap)
    order = []
    while heap:
        ch = heapq.heappop(heap)
        order.append(ch)
        for nb in graph[ch]:
            indegree[nb] -= 1
            if indegree[nb] == 0:
                heapq.heappush(heap, nb)
    return "".join(order) if len(order) == len(letters) else ""
