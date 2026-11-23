# Right side view

Imagine standing on the right side of the tree. Write `right_side_view(root)` that returns the values you can see, from top to bottom (the **last node of each level**).

```python
right_side_view(build([1, 2, 3, None, 5, None, 4]))    # -> [1, 3, 4]
right_side_view(None)                                  # -> []
```

**Think first:** which exercise gave you the nodes level by level? Which node of a level is visible?

**Hint:** pattern *BFS by level*: process one level at a time and keep the last value of each level.

> `TreeNode` is given in `starter.py`. You only use `.val`, `.left` and `.right`. (You will learn classes in Python lesson 19.) In the tests a tree is built from a level-order list like `[1, 2, 3, None, 4]` (`None` = no node).
