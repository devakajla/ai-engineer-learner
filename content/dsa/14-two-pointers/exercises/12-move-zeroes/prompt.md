# Move zeroes to the end

Write `move_zeroes(nums)` that moves every `0` to the end **in place**, keeping the order of the other items. Return `None`.

```python
nums = [0, 1, 0, 3, 12]
move_zeroes(nums)       # nums is now [1, 3, 12, 0, 0]
```

**Think first:** which pointer reads, and which one remembers where the next non-zero goes?

**Hint:** pattern *reader/writer*. Swap `nums[slow]` and `nums[fast]` when `nums[fast] != 0`, then `slow += 1`.
