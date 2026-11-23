# Summary ranges

`nums` is a **sorted list of unique integers**. Write `summary_ranges(nums)` that returns the smallest list of ranges as strings: `"a->b"` for a run of 2 or more consecutive numbers, and `"a"` for a single number.

```python
summary_ranges([0, 1, 2, 4, 5, 7])    # -> ["0->2", "4->5", "7"]
summary_ranges([])                    # -> []
```

**Think first:** when does a run end? Compare each number with the one **before** it.

**Hint:** pattern *group consecutive*: keep `start`; when `nums[i] != nums[i - 1] + 1`, close the run `start..nums[i - 1]` and start a new one.
