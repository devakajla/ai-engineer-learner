import random
from solution import ListNode, list_length


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
    assert list_length(build([4, 5, 6])) == 3
    assert list_length(None) == 0


def test_random():
    rng = random.Random(1)
    for _ in range(50):
        v = [rng.randint(0, 9) for _ in range(rng.randint(0, 12))]
        assert list_length(build(v)) == len(v), f"{v}"
