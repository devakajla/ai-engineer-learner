from collections import Counter, defaultdict, deque


def top_words(text, n):
    return Counter(text.lower().split()).most_common(n)


def group_by_domain(emails):
    groups = defaultdict(list)
    for email in emails:
        groups[email.split("@", 1)[1]].append(email)
    return dict(groups)


class RecentEvents:
    def __init__(self, limit: int) -> None:
        self._events = deque(maxlen=limit)

    def add(self, event) -> None:
        self._events.append(event)

    def items(self) -> list:
        return list(self._events)
