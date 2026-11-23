# Lowest common ancestor (binary tree)

All values in the tree are **different**. `p` and `q` are values that exist in the tree. Write `lowest_common_ancestor(root, p, q)` that returns the **value** of the lowest node that has both `p` and `q` in its subtree (a node counts as its own descendant).

```python
t = build([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
lowest_common_ancestor(t, 5, 1)    # -> 3
lowest_common_ancestor(t, 5, 4)    # -> 5
```

**Think first:** ask each subtree "do you contain `p` or `q`?". What does it mean if both the left and the right subtree say yes?

**Hint:** pattern *post-order search*: if `root` is `None` or its value is `p` or `q`, return `root`; search left and right; if both return something, `root` is the answer; else return the one that is not `None`.

> `TreeNode` is given in `starter.py`. You only use `.val`, `.left` and `.right`. (You will learn classes in Python lesson 19.) In the tests a tree is built from a level-order list like `[1, 2, 3, None, 4]` (`None` = no node).
