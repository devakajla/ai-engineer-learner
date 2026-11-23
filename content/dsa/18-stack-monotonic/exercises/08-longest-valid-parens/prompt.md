# Longest valid parentheses

`s` contains only `(` and `)`. Write `longest_valid_parentheses(s)` that returns the length of the longest **substring** that is a valid parentheses string.

```python
longest_valid_parentheses(")()())")    # -> 4
longest_valid_parentheses("(()")       # -> 2
```

**Think first:** when a `)` breaks the pattern, where does the next valid part start? What do you need to remember to measure a length?

**Hint:** pattern *stack of indexes*: start with `[-1]` as a base. On `(` push the index. On `)` pop; if the stack is empty push the index as the new base, otherwise length is `i - stack[-1]`.
