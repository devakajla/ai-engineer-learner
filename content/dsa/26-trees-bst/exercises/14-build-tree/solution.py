class TreeNode:
    """Given. A node has .val, .left and .right (None when there is no child)."""

    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def build_tree(preorder, inorder):
    index = {v: i for i, v in enumerate(inorder)}
    pos = 0

    def go(lo, hi):
        nonlocal pos
        if lo > hi:
            return None
        root = TreeNode(preorder[pos])
        pos += 1
        mid = index[root.val]
        root.left = go(lo, mid - 1)
        root.right = go(mid + 1, hi)
        return root

    return go(0, len(inorder) - 1)
