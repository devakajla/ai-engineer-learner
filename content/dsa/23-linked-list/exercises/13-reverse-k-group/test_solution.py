import random
from solution import ListNode, reverse_k_group


def build(values):
    head = None
    for v in reversed(values):
        head = ListNode(v, head)
    return head


def to_list(head):
    out = []
    while head:
        out.append(head.val)
        head = head.next
        assert len(out) < 1000, "result is too long: is there a loop?"
    return out


def build_cycle(values, pos):
    """Nodes for values; the last node points back to index pos (-1 = no cycle)."""
    nodes = [ListNode(v) for v in values]
    for a, b in zip(nodes, nodes[1:]):
        a.next = b
    if nodes and pos >= 0:
        nodes[-1].next = nodes[pos]
    return (nodes[0] if nodes else None), nodes


def test_examples():
    assert to_list(reverse_k_group(build([1, 2, 3, 4, 5]), 2)) == [2, 1, 4, 3, 5]
    assert to_list(reverse_k_group(build([1, 2, 3, 4, 5]), 3)) == [3, 2, 1, 4, 5]


def test_edges():
    assert reverse_k_group(None, 2) is None
    assert to_list(reverse_k_group(build([1, 2, 3]), 1)) == [1, 2, 3]
    assert to_list(reverse_k_group(build([1, 2, 3]), 3)) == [3, 2, 1]
    assert to_list(reverse_k_group(build([1, 2]), 3)) == [1, 2]


def test_random():
    rng = random.Random(13)
    for _ in range(300):
        v = [rng.randint(0, 99) for _ in range(rng.randint(0, 11))]
        k = rng.randint(1, 5)
        want = []
        for i in range(0, len(v), k):
            part = v[i:i + k]
            want += part[::-1] if len(part) == k else part
        assert to_list(reverse_k_group(build(v), k)) == want, f"{v}, {k}"
