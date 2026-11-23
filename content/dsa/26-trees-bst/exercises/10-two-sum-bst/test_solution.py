import random
from solution import TreeNode, find_target


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
    t = build([5, 3, 6, 2, 4, None, 7])
    assert find_target(t, 9) is True
    assert find_target(t, 28) is False


def test_edges():
    assert find_target(None, 0) is False
    assert find_target(build([2]), 4) is False, "a node cannot be used twice"


def test_random():
    rng = random.Random(10)
    for _ in range(200):
        t = rand_bst(rng, rng.randint(1, 10))
        vals = pre(t)
        k = rng.randint(0, 80)
        want = any(a + b == k for i, a in enumerate(vals) for b in vals[i + 1:])
        assert find_target(t, k) is want, f"k={k}"
