# Fruit into baskets

A row of trees; `fruits[i]` is the fruit type of tree `i`. You have two baskets and each holds **one type**. Start at any tree, then pick **one fruit from every tree** moving right, until you meet a third type (then you must stop). Write `total_fruit(fruits)` that returns the most fruits you can pick.

```python
total_fruit([1, 2, 3, 2, 2])    # -> 4   (2, 3, 2, 2)
total_fruit([1, 2, 1])          # -> 3
```

**Think first:** this is a famous question in disguise. What is it really asking about the longest part of the list?

**Hint:** pattern *variable window, maximum*: longest part with at most 2 distinct values (same as exercise 03 with `k = 2`).
