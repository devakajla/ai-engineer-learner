# Lowest common ancestor (BST)

`root` is a **binary search tree** (left values smaller, right values bigger) with different values. `p` and `q` are values in it. Write `lca_bst(root, p, q)` that returns the **value** of their lowest common ancestor. Use the BST order: no need to search the whole tree.

```python
t = build([6, 2, 8, 0, 4, 7, 9, None, None, 3, 5])
lca_bst(t, 2, 8)    # -> 6
lca_bst(t, 2, 4)    # -> 2
```

**Think first:** if both `p` and `q` are smaller than the current node, which side holds the answer? If one is smaller and one bigger?

**Hint:** pattern *walk down by comparison*: while true: both smaller -> go left; both bigger -> go right; else the current node is the split point.

> `TreeNode` is given in `starter.py`. You only use `.val`, `.left` and `.right`. (You will learn classes in Python lesson 19.) In the tests a tree is built from a level-order list like `[1, 2, 3, None, 4]` (`None` = no node).
