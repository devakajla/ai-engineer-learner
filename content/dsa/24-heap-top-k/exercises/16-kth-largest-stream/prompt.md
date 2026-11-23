# K-th largest after each number

Numbers arrive one by one. Write `kth_largest_stream(k, nums)` that returns a list: after each number, the k-th largest value so far, or `None` while fewer than `k` numbers have arrived.

```python
kth_largest_stream(3, [4, 5, 8, 2, 3])    # -> [None, None, 4, 4, 4]
kth_largest_stream(1, [5, 3, 7])          # -> [5, 5, 7]
```

**Think first:** you only ever need the `k` biggest numbers. Which one of them is the smallest?

**Hint:** pattern *min-heap of size k*: push the number; if `len(h) > k` pop the smallest; when `len(h) == k` the answer is `h[0]`.
