# Build a tree from preorder and inorder

All values are **different**. Write `build_tree(preorder, inorder)` that rebuilds the tree and returns its root (`TreeNode` is given in `starter.py`; use `TreeNode(value)`). Empty lists give `None`.

```python
t = build_tree([3, 9, 20, 15, 7], [9, 3, 15, 20, 7])
# t.val -> 3, t.left.val -> 9, t.right.val -> 20
```

**Think first:** the first item of preorder is the root. In inorder, what is on the left of the root and what is on the right? How many nodes are in the left part?

**Hint:** pattern *root from preorder, split by inorder*: map each value to its inorder index; `go(lo, hi)` builds the tree for inorder `[lo, hi]` and takes the next preorder value as the root.

> `TreeNode` is given in `starter.py`. You only use `.val`, `.left` and `.right`. (You will learn classes in Python lesson 19.) In the tests a tree is built from a level-order list like `[1, 2, 3, None, 4]` (`None` = no node).
