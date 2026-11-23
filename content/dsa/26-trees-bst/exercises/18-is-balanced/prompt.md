# Is the tree height-balanced?

A tree is **balanced** if for **every** node the heights of its left and right subtrees differ by at most 1. Write `is_balanced(root)`. An empty tree is balanced.

```python
is_balanced(build([3, 9, 20, None, None, 15, 7]))        # -> True
is_balanced(build([1, 2, 2, 3, 3, None, None, 4, 4]))    # -> False
```

**Think first:** if you compute the height of every subtree again and again, the cost grows. Can one function return both "height" and "is it balanced"?

**Hint:** pattern *height with a sentinel*: `check(node)` returns the height, or `-1` if the subtree is unbalanced; if a child returns `-1`, or the heights differ by more than 1, return `-1`.

> `TreeNode` is given in `starter.py`. You only use `.val`, `.left` and `.right`. (You will learn classes in Python lesson 19.) In the tests a tree is built from a level-order list like `[1, 2, 3, None, 4]` (`None` = no node).
