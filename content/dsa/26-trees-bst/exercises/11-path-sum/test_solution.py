import random
from solution import TreeNode, has_path_sum


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


def leaf_sums(root, acc=0):
    if root is None:
        return []
    acc += root.val
    if root.left is None and root.right is None:
        return [acc]
    return leaf_sums(root.left, acc) + leaf_sums(root.right, acc)


def test_examples():
    t = build([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1])
    assert has_path_sum(t, 22) is True
    assert has_path_sum(t, 5) is False


def test_edges():
    assert has_path_sum(None, 0) is False
    assert has_path_sum(build([1]), 1) is True
    assert has_path_sum(build([1, 2]), 1) is False, "node 1 is not a leaf"


def test_random():
    rng = random.Random(11)
    for _ in range(300):
        t = rand_tree(rng, 4)
        target = rng.randint(0, 30)
        assert has_path_sum(t, target) is (target in leaf_sums(t)), f"target={target}"
