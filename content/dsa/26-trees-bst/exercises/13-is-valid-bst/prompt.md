# Is it a valid BST?

Write `is_valid_bst(root)` that returns `True` if the tree is a binary search tree: for **every** node, all values in its left subtree are **smaller** and all in its right subtree are **bigger** (no equal values). An empty tree is valid.

```python
is_valid_bst(build([2, 1, 3]))              # -> True
is_valid_bst(build([5, 1, 4, None, None, 3, 6]))    # -> False   (3 is in the right subtree of 5)
```

**Think first:** checking only parent and child is not enough (see example 2). What limits does a node inherit from all its ancestors?

**Hint:** pattern *pass a valid range down*: `check(node, low, high)`: the value must satisfy `low < val < high`; left child gets `(low, val)`, right child gets `(val, high)`. Start with `None` limits (or `float("-inf")` and `float("inf")`).

> `TreeNode` is given in `starter.py`. You only use `.val`, `.left` and `.right`. (You will learn classes in Python lesson 19.) In the tests a tree is built from a level-order list like `[1, 2, 3, None, 4]` (`None` = no node).
