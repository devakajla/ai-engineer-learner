import random
from solution import ListNode, merge_sorted


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
    assert to_list(merge_sorted(build([1, 3, 5]), build([2, 4]))) == [1, 2, 3, 4, 5]
    assert to_list(merge_sorted(None, build([1]))) == [1]


def test_edges():
    assert merge_sorted(None, None) is None
    assert to_list(merge_sorted(build([1, 2]), None)) == [1, 2]


def test_random():
    rng = random.Random(8)
    for _ in range(200):
        a = sorted(rng.randint(0, 9) for _ in range(rng.randint(0, 6)))
        b = sorted(rng.randint(0, 9) for _ in range(rng.randint(0, 6)))
        assert to_list(merge_sorted(build(a), build(b))) == sorted(a + b), f"{a}, {b}"
