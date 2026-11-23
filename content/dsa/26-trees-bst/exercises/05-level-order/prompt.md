# Level order traversal

Write `level_order(root)` that returns the values **level by level**, from left to right, as a list of lists. `None` gives `[]`.

```python
level_order(build([3, 9, 20, None, None, 15, 7]))    # -> [[3], [9, 20], [15, 7]]
level_order(None)                                    # -> []
```

**Think first:** a stack goes deep first. Which structure gives you "first in, first out"? How do you know where one level ends?

**Hint:** pattern *BFS with a queue*: `from collections import deque` (see `reference/heap-and-deque.md`); for each round process `len(queue)` nodes, which is exactly one level.

> `TreeNode` is given in `starter.py`. You only use `.val`, `.left` and `.right`. (You will learn classes in Python lesson 19.) In the tests a tree is built from a level-order list like `[1, 2, 3, None, 4]` (`None` = no node).
