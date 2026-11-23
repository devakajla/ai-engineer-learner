# Find the common items quickly

Write two functions:

- `common_items(a, b)` → a **sorted list** of the distinct items that are in both lists. Do not use `x in some_list` anywhere: the tests pass lists that **raise an error** if you do. (They can still be looped over and turned into a set.)
- `dedupe_keep_order(items)` → a new list with the duplicates removed, keeping the **first** appearance of each item and the original order. It must be fast for long lists.

```python
common_items([5, 3, 8, 1, 8], [8, 2, 5, 9])       # -> [5, 8]
dedupe_keep_order([3, 1, 3, 2, 1])                # -> [3, 1, 2]
```

**Think first:** What is the cost of `x in a_list` inside a loop? What gives a constant-time "have I seen this?" check?

**Hint:** Turn one list into a `set`, or use `set(a) & set(b)`. For `dedupe_keep_order`, keep a `seen` set while you build the result list.
