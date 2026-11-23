class ListNode:
    """Given. A node has .val and .next (None at the end of the list)."""

    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def middle_node(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow
