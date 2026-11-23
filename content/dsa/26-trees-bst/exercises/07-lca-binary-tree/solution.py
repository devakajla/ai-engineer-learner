class TreeNode:
    """Given. A node has .val, .left and .right (None when there is no child)."""

    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def lowest_common_ancestor(root, p, q):
    def find(node):
        if node is None or node.val == p or node.val == q:
            return node
        left = find(node.left)
        right = find(node.right)
        if left and right:
            return node
        return left or right

    return find(root).val
