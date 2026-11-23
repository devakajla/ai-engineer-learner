class TreeNode:
    """Given. A node has .val, .left and .right (None when there is no child)."""

    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def find_target(root, k):
    values = []

    def walk(node):
        if node:
            walk(node.left)
            values.append(node.val)
            walk(node.right)

    walk(root)
    lo, hi = 0, len(values) - 1
    while lo < hi:
        total = values[lo] + values[hi]
        if total == k:
            return True
        if total < k:
            lo += 1
        else:
            hi -= 1
    return False
