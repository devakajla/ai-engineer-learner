class TreeNode:
    """Given. A node has .val, .left and .right (None when there is no child)."""

    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def is_symmetric(root):
    def mirror(a, b):
        if a is None and b is None:
            return True
        if a is None or b is None:
            return False
        return a.val == b.val and mirror(a.left, b.right) and mirror(a.right, b.left)

    return root is None or mirror(root.left, root.right)
