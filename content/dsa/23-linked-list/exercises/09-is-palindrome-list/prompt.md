# Is the list a palindrome?

Write `is_palindrome_list(head)` that returns `True` if the values read the same forward and backward. Try O(1) extra space (the list may be changed).

```python
is_palindrome_list(build([1, 2, 2, 1]))    # -> True
is_palindrome_list(build([1, 2]))          # -> False
```

**Think first:** find the middle, then compare the first half with the **reversed** second half. Which two earlier exercises do you combine?

**Hint:** pattern *middle + reverse*: slow/fast to find the middle; reverse the second half; walk both halves together.

> `ListNode` is given in `starter.py`. You only use `.val` and `.next`. (You will learn classes in Python lesson 19.)
