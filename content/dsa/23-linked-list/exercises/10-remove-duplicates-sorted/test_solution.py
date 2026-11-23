import random
from solution import ListNode, remove_duplicates


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
    assert to_list(remove_duplicates(build([1, 1, 2, 3, 3]))) == [1, 2, 3]
    assert to_list(remove_duplicates(build([2, 2, 2]))) == [2]


def test_edges():
    assert remove_duplicates(None) is None
    assert to_list(remove_duplicates(build([1, 2, 3]))) == [1, 2, 3]


def test_random():
    rng = random.Random(10)
    for _ in range(200):
        v = sorted(rng.randint(0, 5) for _ in range(rng.randint(0, 10)))
        assert to_list(remove_duplicates(build(v))) == sorted(set(v)), f"{v}"
