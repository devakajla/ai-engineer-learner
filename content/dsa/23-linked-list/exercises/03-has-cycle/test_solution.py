import random
from solution import ListNode, has_cycle


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
    assert has_cycle(build_cycle([1, 2, 3, 4], 1)[0]) is True
    assert has_cycle(build([1, 2, 3])) is False


def test_edges():
    assert has_cycle(None) is False
    assert has_cycle(build_cycle([1], 0)[0]) is True, "node pointing to itself"
    assert has_cycle(build_cycle([1, 2], 0)[0]) is True


def test_random():
    rng = random.Random(3)
    for _ in range(200):
        n = rng.randint(1, 10)
        pos = rng.randint(-1, n - 1)
        head, _ = build_cycle(list(range(n)), pos)
        assert has_cycle(head) is (pos >= 0), f"n={n}, pos={pos}"
