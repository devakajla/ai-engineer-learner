# K-th smallest in a BST

`root` is a binary search tree. Write `kth_smallest(root, k)` that returns the k-th smallest value (`k` starts at 1; `1 <= k <=` number of nodes).

```python
kth_smallest(build([3, 1, 4, None, 2]), 1)           # -> 1
kth_smallest(build([5, 3, 6, 2, 4, None, None, 1]), 3)    # -> 3
```

**Think first:** which traversal visits a BST in sorted order? Do you need to visit all nodes?

**Hint:** pattern *inorder walk*: walk inorder and count; return when the count reaches `k` (or just build the inorder list and pick `k - 1`).

> `TreeNode` is given in `starter.py`. You only use `.val`, `.left` and `.right`. (You will learn classes in Python lesson 19.) In the tests a tree is built from a level-order list like `[1, 2, 3, None, 4]` (`None` = no node).
