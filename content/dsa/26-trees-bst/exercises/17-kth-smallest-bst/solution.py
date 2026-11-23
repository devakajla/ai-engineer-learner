class TreeNode:
    """Given. A node has .val, .left and .right (None when there is no child)."""

    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def kth_smallest(root, k):
    values = []

    def walk(node):
        if node is None or len(values) >= k:
            return
        walk(node.left)
        if len(values) < k:
            values.append(node.val)
        walk(node.right)

    walk(root)
    return values[k - 1]
