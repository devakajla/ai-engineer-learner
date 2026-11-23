# Group anagrams

Write `group_anagrams(words)` that groups words that are anagrams of each other. Return a list of groups. Groups must appear in the order of their **first word**, and words inside a group keep their original order.

```python
group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
# -> [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]
group_anagrams([""])    # -> [[""]]
```

**Think first:** what single value is the same for all anagrams of a word? Use it as a key.

**Hint:** pattern *group by key*: key = `"".join(sorted(word))`; `groups.setdefault(key, []).append(word)`. A dict keeps insertion order.
