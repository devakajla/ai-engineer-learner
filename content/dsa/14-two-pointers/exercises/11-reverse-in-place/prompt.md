# Reverse a list in place

Write `reverse_in_place(items)` that reverses the list **in place** using two pointers and swaps. Do not use `reverse()`, slicing or `reversed`. Return `None`.

```python
items = [1, 2, 3, 4]
reverse_in_place(items)      # items is now [4, 3, 2, 1]
```

**Think first:** how many swaps do you need for a list of 5 items?

**Hint:** `items[left], items[right] = items[right], items[left]`, then move both pointers inward while `left < right`.
