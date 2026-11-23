import random
from solution import ListNode, remove_value


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
    assert to_list(remove_value(build([1, 2, 6, 3, 6]), 6)) == [1, 2, 3]
    assert to_list(remove_value(build([7, 7]), 7)) == []


def test_edges():
    assert remove_value(None, 1) is None
    assert to_list(remove_value(build([1, 2]), 5)) == [1, 2]


def test_random():
    rng = random.Random(11)
    for _ in range(200):
        v = [rng.randint(0, 3) for _ in range(rng.randint(0, 10))]
        x = rng.randint(0, 3)
        assert to_list(remove_value(build(v), x)) == [a for a in v if a != x], f"{v}, {x}"
