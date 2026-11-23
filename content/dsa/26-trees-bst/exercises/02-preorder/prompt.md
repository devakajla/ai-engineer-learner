# Preorder traversal

Preorder visits **node, left subtree, right subtree**. Write `preorder(root)` that returns the values as a list.

```python
preorder(build([1, None, 2, 3]))    # -> [1, 2, 3]
preorder(None)                      # -> []
```

**Think first:** in which order do you write the current value and the two recursive calls?

**Hint:** pattern *DFS recursion*: `[root.val] + preorder(root.left) + preorder(root.right)`.

> `TreeNode` is given in `starter.py`. You only use `.val`, `.left` and `.right`. (You will learn classes in Python lesson 19.) In the tests a tree is built from a level-order list like `[1, 2, 3, None, 4]` (`None` = no node).
