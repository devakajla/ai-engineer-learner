# Compose small functions

Write:

- `compose(*funcs)` → returns a function that applies `funcs` **left to right**: `compose(f, g)(x) == g(f(x))`. With no functions it returns the input unchanged. (Hint: `functools.reduce`.)
- `make_cleaner()` → uses `compose` and `functools.partial` to build a text cleaner that: strips whitespace → lowercases → replaces runs of spaces with a single `-` (use `partial(re.sub, r"\s+", "-")`) → truncates to 20 chars. It's a slug maker!
- `running_max(nums)` → list of the maximum seen so far at each position (use `itertools.accumulate`)

```python
compose(str.strip, str.upper)("  hi ")   # -> "HI"
make_cleaner()("  Hello   World  ")      # -> "hello-world"
running_max([3, 1, 4, 1, 5])             # -> [3, 3, 4, 4, 5]
```
