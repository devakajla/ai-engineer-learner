import random
from solution import ListNode, cycle_start


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
    head, nodes = build_cycle([3, 2, 0, -4], 1)
    assert cycle_start(head) is nodes[1]
    assert cycle_start(build([1, 2])) is None


def test_edges():
    assert cycle_start(None) is None
    head, nodes = build_cycle([1], 0)
    assert cycle_start(head) is nodes[0]
    head, nodes = build_cycle([1, 2, 3], 0)
    assert cycle_start(head) is nodes[0], "cycle starts at the head"


def test_random():
    rng = random.Random(4)
    for _ in range(300):
        n = rng.randint(1, 12)
        pos = rng.randint(-1, n - 1)
        head, nodes = build_cycle(list(range(n)), pos)
        want = nodes[pos] if pos >= 0 else None
        assert cycle_start(head) is want, f"n={n}, pos={pos}"
