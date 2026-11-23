# Remove k equal neighbours

Write `remove_k_duplicates(s, k)`. Whenever there are **`k` equal letters in a row**, delete them. Keep doing it until no more can be deleted. Return the string. `k >= 2`.

```python
remove_k_duplicates("deeedbbcccbdaa", 3)    # -> "aa"
remove_k_duplicates("abcd", 2)              # -> "abcd"
```

**Think first:** with `k = 2` the stack of letters was enough. What extra number must each stack item remember now?

**Hint:** pattern *stack of [letter, count]*: if the top letter is the same, increase its count; when the count reaches `k`, pop it. Rebuild with `letter * count`.
