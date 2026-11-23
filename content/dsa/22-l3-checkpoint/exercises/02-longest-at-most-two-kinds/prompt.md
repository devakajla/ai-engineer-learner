# Longest run with at most two kinds

Write `longest_two_kinds(s)` that returns the length of the longest **substring** of `s` that has **at most 2 different characters**.

```python
longest_two_kinds("eceba")      # -> 3    ("ece")
longest_two_kinds("ccaabbb")    # -> 5    ("aabbb")
```

**Think first:** when the window has 3 kinds, what must you do?

**Hint:** pattern *sliding window + counter-dict*: grow `right`, count letters, shrink `left` while `len(counts) > 2`.
