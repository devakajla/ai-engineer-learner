# Backspace compare

In `s` and `t` the character `#` is a **backspace** (it deletes the previous letter; on an empty text it does nothing). Write `backspace_compare(s, t)` that returns `True` if both texts are equal after all backspaces.

```python
backspace_compare("ab#c", "ad#c")    # -> True   (both "ac")
backspace_compare("a#c", "b")        # -> False
```

**Think first:** typing letters and pressing backspace is exactly push and pop.

**Hint:** pattern *stack*: write a helper `build(text)`: push letters, pop on `#` (if not empty). Compare `build(s) == build(t)`.
