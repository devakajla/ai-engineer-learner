# Diameter of a binary tree

The **diameter** is the number of **edges** on the longest path between any two nodes (the path may skip the root). Write `diameter(root)`. A tree with 0 or 1 node has diameter `0`.

```python
diameter(build([1, 2, 3, 4, 5]))    # -> 3    (4 -> 2 -> 1 -> 3)
diameter(build([1, 2]))             # -> 1
```

**Think first:** for each node, the longest path that bends there is `height(left) + height(right)`. How do you check every node in one pass?

**Hint:** pattern *height + global best*: a helper returns the height; before returning, update `best = max(best, left_height + right_height)`.

> `TreeNode` is given in `starter.py`. You only use `.val`, `.left` and `.right`. (You will learn classes in Python lesson 19.) In the tests a tree is built from a level-order list like `[1, 2, 3, None, 4]` (`None` = no node).
