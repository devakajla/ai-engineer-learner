# Add two numbers as lists

Two non-negative numbers are stored as lists of digits in **reverse order** (`342` is `2 -> 4 -> 3`). Write `add_two_numbers(a, b)` that returns the sum in the same form. You may create new nodes with `ListNode(value)`.

```python
to_list(add_two_numbers(build([2, 4, 3]), build([5, 6, 4])))    # -> [7, 0, 8]    (342 + 465 = 807)
to_list(add_two_numbers(build([9, 9]), build([1])))             # -> [0, 0, 1]
```

**Think first:** this is school addition. What do you carry to the next digit, and when does the loop stop?

**Hint:** pattern *dummy head + carry*: loop `while a or b or carry`; `total = carry + (a.val if a else 0) + (b.val if b else 0)`; digit is `total % 10`, carry is `total // 10`.

> `ListNode` is given in `starter.py`. You only use `.val` and `.next`. (You will learn classes in Python lesson 19.)
