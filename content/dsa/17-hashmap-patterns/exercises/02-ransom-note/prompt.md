# Ransom note

Write `can_construct(note, magazine)` that returns `True` if you can build `note` using letters from `magazine`. Every letter of the magazine can be used **at most once**.

```python
can_construct("aa", "aab")    # -> True
can_construct("aa", "ab")     # -> False
```

**Think first:** what do you need to know about the magazine before you start reading the note?

**Hint:** pattern *counter-dict (available)*: count the magazine, then for each note letter take one away; if it is not available, return `False`.
