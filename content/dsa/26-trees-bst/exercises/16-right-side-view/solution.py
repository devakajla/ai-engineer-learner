class TreeNode:
    """Given. A node has .val, .left and .right (None when there is no child)."""

    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


from collections import deque


def right_side_view(root):
    if root is None:
        return []
    view = []
    queue = deque([root])
    while queue:
        for _ in range(len(queue)):
            node = queue.popleft()
            last = node.val
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        view.append(last)
    return view
