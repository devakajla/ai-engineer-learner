import random
from solution import ListNode, nth_from_end


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
    assert nth_from_end(build([1, 2, 3, 4, 5]), 2) == 4
    assert nth_from_end(build([9]), 1) == 9


def test_edges():
    assert nth_from_end(build([1, 2, 3]), 3) == 1, "n equals the length"


def test_random():
    rng = random.Random(6)
    for _ in range(100):
        v = [rng.randint(0, 99) for _ in range(rng.randint(1, 12))]
        n = rng.randint(1, len(v))
        assert nth_from_end(build(v), n) == v[-n], f"{v}, {n}"
