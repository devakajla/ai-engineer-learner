class ListNode:
    """Given. A node has .val and .next (None at the end of the list)."""

    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def cycle_length(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            count = 1
            node = slow.next
            while node is not slow:
                node = node.next
                count += 1
            return count
    return 0
