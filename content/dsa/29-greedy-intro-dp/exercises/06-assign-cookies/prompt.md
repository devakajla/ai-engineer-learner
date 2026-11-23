# Assign cookies

`greed[i]` is the smallest cookie size child `i` will accept. `sizes` are the cookie sizes you have. Each child gets at most one cookie and each cookie goes to at most one child. Write `content_children(greed, sizes)` that returns the largest number of happy children.

```python
content_children([1, 2, 3], [1, 1])      # -> 1
content_children([1, 2], [1, 2, 3])      # -> 2
```

**Think first:** should the biggest cookie go to the greediest child, or should you try to waste as little as possible?

**Hint:** pattern *greedy matching with sorting*: sort both; for each cookie (smallest first), if it satisfies the current least-greedy child, move to the next child.
