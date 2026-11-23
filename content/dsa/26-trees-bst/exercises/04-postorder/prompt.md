# Postorder traversal

Postorder visits **left subtree, right subtree, node**. Write `postorder(root)` that returns the values as a list.

```python
postorder(build([1, None, 2, 3]))    # -> [3, 2, 1]
postorder(build([2, 1, 3]))          # -> [1, 3, 2]
```

**Think first:** the node is visited last. What does that mean for the order of the list you build?

**Hint:** pattern *DFS recursion*: `postorder(left) + postorder(right) + [root.val]`.

> `TreeNode` is given in `starter.py`. You only use `.val`, `.left` and `.right`. (You will learn classes in Python lesson 19.) In the tests a tree is built from a level-order list like `[1, 2, 3, None, 4]` (`None` = no node).
