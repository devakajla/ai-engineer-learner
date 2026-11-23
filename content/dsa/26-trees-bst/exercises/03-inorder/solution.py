class TreeNode:
    """Given. A node has .val, .left and .right (None when there is no child)."""

    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def inorder(root):
    if root is None:
        return []
    return inorder(root.left) + [root.val] + inorder(root.right)
