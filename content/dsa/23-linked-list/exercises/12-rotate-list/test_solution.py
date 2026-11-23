import random
from solution import ListNode, rotate_right


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
    assert to_list(rotate_right(build([1, 2, 3, 4, 5]), 2)) == [4, 5, 1, 2, 3]
    assert to_list(rotate_right(build([1, 2]), 5)) == [2, 1]


def test_edges():
    assert rotate_right(None, 3) is None
    assert to_list(rotate_right(build([1, 2, 3]), 0)) == [1, 2, 3]
    assert to_list(rotate_right(build([1, 2, 3]), 3)) == [1, 2, 3]


def test_random():
    rng = random.Random(12)
    for _ in range(200):
        v = [rng.randint(0, 99) for _ in range(rng.randint(1, 9))]
        k = rng.randint(0, 25)
        r = k % len(v)
        want = v[len(v) - r:] + v[:len(v) - r]
        assert to_list(rotate_right(build(v), k)) == want, f"{v}, {k}"
