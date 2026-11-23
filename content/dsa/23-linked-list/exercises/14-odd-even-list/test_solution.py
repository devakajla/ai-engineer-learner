import random
from solution import ListNode, odd_even_list


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
    assert to_list(odd_even_list(build([1, 2, 3, 4, 5]))) == [1, 3, 5, 2, 4]
    assert to_list(odd_even_list(build([2, 1, 3, 5, 6]))) == [2, 3, 6, 1, 5]


def test_edges():
    assert odd_even_list(None) is None
    assert to_list(odd_even_list(build([1]))) == [1]
    assert to_list(odd_even_list(build([1, 2]))) == [1, 2]


def test_random():
    rng = random.Random(14)
    for _ in range(200):
        v = [rng.randint(0, 99) for _ in range(rng.randint(0, 11))]
        assert to_list(odd_even_list(build(v))) == v[0::2] + v[1::2], f"{v}"
