# Most common letter

Write `most_common_letter(text)` that returns the letter (lower case) that appears most often, ignoring case and anything that is not a letter. If there is a tie, return the one that comes **first in the alphabet**. For text with no letters return `None`.

```python
most_common_letter("Hello World")   # -> "l"
most_common_letter("abab")          # -> "a"
most_common_letter("123 !")         # -> None
```

Hint: `from collections import Counter`.
