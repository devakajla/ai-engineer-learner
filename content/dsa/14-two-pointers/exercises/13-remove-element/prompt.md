# Remove an element

Write `remove_element(nums, val)` that removes every `val` **in place** so the first `k` items are the other values in their original order, and returns `k`. Items after `k` do not matter.

```python
nums = [3, 2, 2, 3]
remove_element(nums, 3)      # -> 2, and nums[:2] == [2, 2]
remove_element([1, 2], 9)    # -> 2
```

**Think first:** how is this different from "remove duplicates"? What do you compare against?

**Hint:** reader/writer: write `nums[slow] = nums[fast]` when `nums[fast] != val`.
