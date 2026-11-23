import random
from solution import ListNode, remove_nth_from_end


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
    assert to_list(remove_nth_from_end(build([1, 2, 3, 4, 5]), 2)) == [1, 2, 3, 5]
    assert to_list(remove_nth_from_end(build([1]), 1)) == []


def test_edges():
    assert to_list(remove_nth_from_end(build([1, 2]), 2)) == [2], "remove the head"
    assert to_list(remove_nth_from_end(build([1, 2]), 1)) == [1], "remove the tail"


def test_random():
    rng = random.Random(7)
    for _ in range(200):
        v = [rng.randint(0, 99) for _ in range(rng.randint(1, 12))]
        n = rng.randint(1, len(v))
        want = v[:len(v) - n] + v[len(v) - n + 1:]
        assert to_list(remove_nth_from_end(build(v), n)) == want, f"{v}, {n}"
