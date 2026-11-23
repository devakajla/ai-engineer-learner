class TreeNode:
    """Given. A node has .val, .left and .right (None when there is no child)."""

    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def contains(root, val):
    node = root
    while node:
        if val == node.val:
            return True
        node = node.left if val < node.val else node.right
    return False
