# Root-to-leaf path sum

A **leaf** has no children. Write `has_path_sum(root, target)` that returns `True` if some path from the root down to a leaf has values adding up to `target`. An empty tree has no path.

```python
t = build([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1])
has_path_sum(t, 22)    # -> True   (5 + 4 + 11 + 2)
has_path_sum(t, 5)     # -> False
```

**Think first:** after you use the current node, what is the target for the children? When is a node a leaf?

**Hint:** pattern *carry the remainder down*: at a leaf return `root.val == target`; else try left or right with `target - root.val`.

> `TreeNode` is given in `starter.py`. You only use `.val`, `.left` and `.right`. (You will learn classes in Python lesson 19.) In the tests a tree is built from a level-order list like `[1, 2, 3, None, 4]` (`None` = no node).
