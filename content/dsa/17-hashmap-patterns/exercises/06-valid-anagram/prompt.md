# Valid anagram

Write `is_anagram(s, t)` that returns `True` if `t` uses exactly the same letters as `s`, the same number of times, in any order.

```python
is_anagram("anagram", "nagaram")    # -> True
is_anagram("rat", "car")            # -> False
```

**Think first:** if the lengths differ, do you even need to look at the letters?

**Hint:** pattern *counter-dict*: count `s`, subtract with `t`, every count must end at `0`. (Comparing two dicts with `==` also works.)
