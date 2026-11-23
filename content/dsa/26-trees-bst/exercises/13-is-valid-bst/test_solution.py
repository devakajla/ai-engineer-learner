import random
from solution import TreeNode, is_valid_bst


def build(vals):
    """Level-order list (None = missing) -> tree."""
    if not vals or vals[0] is None:
        return None
    nodes = [TreeNode(vals[0])]
    queue, i = [nodes[0]], 1
    while queue and i < len(vals):
        node = queue.pop(0)
        if i < len(vals) and vals[i] is not None:
            node.left = TreeNode(vals[i])
            queue.append(node.left)
        i += 1
        if i < len(vals) and vals[i] is not None:
            node.right = TreeNode(vals[i])
            queue.append(node.right)
        i += 1
    return nodes[0]


def shape(rng, depth):
    if depth == 0 or rng.random() < 0.25:
        return None
    node = TreeNode(0)
    node.left = shape(rng, depth - 1)
    node.right = shape(rng, depth - 1)
    return node


def all_nodes(root):
    return [] if root is None else [root] + all_nodes(root.left) + all_nodes(root.right)


def rand_tree(rng, depth=4, unique=False):
    root = shape(rng, depth)
    nodes = all_nodes(root)
    values = rng.sample(range(0, 40), len(nodes)) if unique else [rng.randint(0, 9) for _ in nodes]
    for n, v in zip(nodes, values):
        n.val = v
    return root


def insert(root, v):
    if root is None:
        return TreeNode(v)
    if v < root.val:
        root.left = insert(root.left, v)
    else:
        root.right = insert(root.right, v)
    return root


def rand_bst(rng, n):
    root = None
    for v in rng.sample(range(0, 40), n):
        root = insert(root, v)
    return root


def pre(r):
    return [] if r is None else [r.val] + pre(r.left) + pre(r.right)


def ino(r):
    return [] if r is None else ino(r.left) + [r.val] + ino(r.right)


def post(r):
    return [] if r is None else post(r.left) + post(r.right) + [r.val]


def height(r):
    return 0 if r is None else 1 + max(height(r.left), height(r.right))


def test_examples():
    assert is_valid_bst(build([2, 1, 3])) is True
    assert is_valid_bst(build([5, 1, 4, None, None, 3, 6])) is False


def test_edges():
    assert is_valid_bst(None) is True
    assert is_valid_bst(build([2, 2, 2])) is False, "equal values are not allowed"
    assert is_valid_bst(build([5, 4, 6, None, None, 3, 7])) is False


def test_random():
    rng = random.Random(13)
    for _ in range(300):
        if rng.random() < 0.5:
            t = rand_bst(rng, rng.randint(1, 9))
        else:
            t = rand_tree(rng, 4)
        vals = ino(t)
        want = all(a < b for a, b in zip(vals, vals[1:]))
        assert is_valid_bst(t) is want, f"inorder {vals}"
