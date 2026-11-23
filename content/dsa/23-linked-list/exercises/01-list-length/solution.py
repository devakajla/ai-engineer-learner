class ListNode:
    """Given. A node has .val and .next (None at the end of the list)."""

    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def list_length(head):
    count = 0
    while head:
        count += 1
        head = head.next
    return count
