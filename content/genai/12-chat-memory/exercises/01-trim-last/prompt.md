# Keep the last N messages

Write `trim_last(history, n)`. It returns a **new** list with only the last `n` messages.

Rules:
- If `n` is `0` or negative, return an empty list `[]`.
- If `n` is bigger than the history, return all the messages.
- Do not change the list that was passed in.

```python
h = ["a", "b", "c", "d"]

trim_last(h, 2)    # -> ['c', 'd']
trim_last(h, 10)   # -> ['a', 'b', 'c', 'd']
trim_last(h, 0)    # -> []
```

**Think first:** what does `h[-0:]` return?
