class ListNode:
    """Given. A node has .val and .next (None at the end of the list)."""

    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def remove_nth_from_end(head, n):
    dummy = ListNode(0, head)
    fast = slow = dummy
    for _ in range(n + 1):
        fast = fast.next
    while fast:
        fast = fast.next
        slow = slow.next
    slow.next = slow.next.next
    return dummy.next
