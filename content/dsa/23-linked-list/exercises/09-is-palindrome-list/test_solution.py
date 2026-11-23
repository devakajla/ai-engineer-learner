import random
from solution import ListNode, is_palindrome_list


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
    assert is_palindrome_list(build([1, 2, 2, 1])) is True
    assert is_palindrome_list(build([1, 2])) is False


def test_edges():
    assert is_palindrome_list(None) is True
    assert is_palindrome_list(build([5])) is True
    assert is_palindrome_list(build([1, 2, 1])) is True


def test_random():
    rng = random.Random(9)
    for _ in range(300):
        v = [rng.randint(0, 2) for _ in range(rng.randint(0, 8))]
        assert is_palindrome_list(build(v)) is (v == v[::-1]), f"{v}"
