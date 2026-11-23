# Maximum depth of a tree

The **depth** is the number of nodes on the longest path from the root down to a leaf. Write `max_depth(root)`. An empty tree (`None`) has depth `0`.

```python
max_depth(build([3, 9, 20, None, None, 15, 7]))    # -> 3
max_depth(None)                                    # -> 0
```

**Think first:** the depth of a tree depends on the depths of its two children. What is the depth of `None`?

**Hint:** pattern *post-order recursion*: `1 + max(max_depth(left), max_depth(right))`, base case `None` -> `0`.

> `TreeNode` is given in `starter.py`. You only use `.val`, `.left` and `.right`. (You will learn classes in Python lesson 19.) In the tests a tree is built from a level-order list like `[1, 2, 3, None, 4]` (`None` = no node).
