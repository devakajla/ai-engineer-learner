# Group anagrams

Write `group_anagrams(words)` that groups words that are anagrams of each other. Return a list of groups. Each group keeps the input order; groups are ordered by the first appearance of any member.

```python
group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
# -> [['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]
```

**Think first:** what do anagrams have in common that you can use as a dict key?

**Hint:** key = `"".join(sorted(word))`.
