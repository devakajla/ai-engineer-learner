# Left and right sum differences

Write `left_right_diff(nums)` that returns a list `answer` where `answer[i] = abs(left_sum - right_sum)`. `left_sum` is the sum of items before `i`, `right_sum` is the sum of items after `i`.

```python
left_right_diff([10, 4, 8, 3])    # -> [15, 1, 11, 22]
left_right_diff([1])              # -> [0]
```

**Think first:** can you do it in one pass after computing the total?

**Hint:** pattern *prefix sum with total*: `right = total - left - nums[i]`.
