---
title: "Trees & BST"
summary: "Binary trees with recursion (DFS), queues (BFS) and the BST order rule."
plan_ids: []
---

A **tree** is a node with up to two children: `.left` and `.right`. A missing child is `None`. A node with no children is a **leaf**. Trees show up everywhere: file folders, menus, and search structures.

> `TreeNode` is given as ready code in `starter.py`. You only use `.val`, `.left` and `.right`. (Classes: Python lesson 19.) Watch the intro video first.

## Build and read a tree

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

root = TreeNode(1, TreeNode(2), TreeNode(3))
print(root.left.val, root.right.val)   # -> 2 3
```

Tests write trees as level-order lists: `[3, 9, 20, None, None, 15, 7]` (`None` means no node there).

## Pattern 1: recursion (DFS)

A tree is a root plus two smaller trees, so recursion fits. Always: base case `None`, then trust the recursion on `left` and `right`.

```python
def max_depth(root):
    if root is None:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))
```

## The three traversals

Same walk, different moment to read the node:

| Name | Order | Result on `2 / 1, 3` |
| --- | --- | --- |
| Preorder | node, left, right | `[2, 1, 3]` |
| Inorder | left, node, right | `[1, 2, 3]` |
| Postorder | left, right, node | `[1, 3, 2]` |

**Postorder** is the shape when the answer for a node needs answers from its children (height, balanced, diameter).

## Pattern 2: BFS by level (queue)

```python
from collections import deque

def level_order(root):
    if root is None:
        return []
    levels, queue = [], deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):       # exactly one level
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        levels.append(level)
    return levels
```

## Pattern 3: carry information down

Pass a value to the children: remaining sum (path sum), allowed range (valid BST).

## Pattern 4: return one thing, track another

Diameter: the helper returns the **height**, and a variable `best` records the best bend (`left + right`). Use `nonlocal best` inside the nested helper.

## Binary search tree (BST)

For every node: everything in the left subtree is **smaller**, everything in the right subtree is **bigger**.

- **Search** like binary search: go left or right. O(height).
- **Inorder** gives sorted order.
- **Valid BST** check: pass `(low, high)` limits down; comparing only parent and child is not enough.
- **LCA in a BST:** the first node where `p` and `q` split to different sides.

A balanced tree has height about log n; a chain-like tree has height n.

## Common mistakes

- Forgetting the base case `None`.
- Using `root.left.val` when `root.left` can be `None`.
- Checking a BST only against the parent.
- Mixing up depth (counted from the root) and height (counted from the bottom).
- Confusing nodes and edges (diameter counts edges).

## Interview corner

**Q: DFS vs BFS on a tree?**
A: DFS (recursion or stack) goes deep first and suits "answer from children". BFS (queue) goes level by level and suits level questions.

**Q: Time and space of a traversal?**
A: O(n) time. Space is O(height) for DFS and O(width) for BFS.

**Q: Why does inorder of a BST come out sorted?**
A: Left (smaller), then node, then right (bigger), at every node.

**Q: How do you rebuild a tree from preorder and inorder?**
A: The first preorder item is the root. Its position in inorder splits left and right parts.

## Summary

- Base case `None`; recurse left and right; combine.
- Preorder, inorder, postorder; BFS with a queue for levels.
- BST: use the order to search; inorder is sorted; validate with ranges.
- Cheat sheet: `reference/patterns.md` and `reference/heap-and-deque.md` (deque).
