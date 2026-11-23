class TreeNode:
    """Given. A node has .val, .left and .right (None when there is no child)."""

    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def postorder(root):
    if root is None:
        return []
    return postorder(root.left) + postorder(root.right) + [root.val]
