class ListNode:
    """Given. A node has .val and .next (None at the end of the list)."""

    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def nth_from_end(head, n):
    fast = head
    for _ in range(n):
        fast = fast.next
    slow = head
    while fast:
        fast = fast.next
        slow = slow.next
    return slow.val
