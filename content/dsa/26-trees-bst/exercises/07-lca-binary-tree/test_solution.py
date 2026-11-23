import random
from solution import TreeNode, lowest_common_ancestor


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


def path_to(root, v):
    if root is None:
        return None
    if root.val == v:
        return [root.val]
    for child in (root.left, root.right):
        sub = path_to(child, v)
        if sub is not None:
            return [root.val] + sub
    return None


def brute(root, p, q):
    a, b = path_to(root, p), path_to(root, q)
    last = None
    for x, y in zip(a, b):
        if x != y:
            break
        last = x
    return last


def test_examples():
    t = build([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
    assert lowest_common_ancestor(t, 5, 1) == 3
    assert lowest_common_ancestor(t, 5, 4) == 5


def test_random():
    rng = random.Random(7)
    for _ in range(300):
        t = rand_tree(rng, 4, unique=True)
        vals = pre(t)
        if not vals:
            continue
        p, q = rng.choice(vals), rng.choice(vals)
        assert lowest_common_ancestor(t, p, q) == brute(t, p, q), f"p={p}, q={q}"
