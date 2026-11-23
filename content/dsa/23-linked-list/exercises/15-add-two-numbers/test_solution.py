import random
from solution import ListNode, add_two_numbers


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


def num(values):
    return sum(d * 10 ** i for i, d in enumerate(values))


def test_examples():
    assert to_list(add_two_numbers(build([2, 4, 3]), build([5, 6, 4]))) == [7, 0, 8]
    assert to_list(add_two_numbers(build([9, 9]), build([1]))) == [0, 0, 1]


def test_edges():
    assert to_list(add_two_numbers(build([0]), build([0]))) == [0]
    assert to_list(add_two_numbers(build([9, 9, 9]), build([9, 9, 9]))) == [8, 9, 9, 1]


def test_random():
    rng = random.Random(15)
    for _ in range(300):
        a = [rng.randint(0, 9) for _ in range(rng.randint(1, 6))]
        b = [rng.randint(0, 9) for _ in range(rng.randint(1, 6))]
        got = to_list(add_two_numbers(build(a), build(b)))
        assert num(got) == num(a) + num(b), f"{a} + {b} -> {got}"
