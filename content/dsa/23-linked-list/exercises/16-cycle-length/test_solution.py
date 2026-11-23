import random
from solution import ListNode, cycle_length


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
    assert cycle_length(build_cycle([1, 2, 3, 4, 5], 2)[0]) == 3
    assert cycle_length(build([1, 2, 3])) == 0


def test_edges():
    assert cycle_length(None) == 0
    assert cycle_length(build_cycle([1], 0)[0]) == 1


def test_random():
    rng = random.Random(16)
    for _ in range(300):
        n = rng.randint(1, 12)
        pos = rng.randint(-1, n - 1)
        head, _ = build_cycle(list(range(n)), pos)
        assert cycle_length(head) == (n - pos if pos >= 0 else 0), f"n={n}, pos={pos}"
