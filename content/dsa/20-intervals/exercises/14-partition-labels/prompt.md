# Partition labels

Write `partition_labels(s)` that cuts the string into as **many parts as possible** so that **each letter appears in only one part**. Return the **sizes** of the parts in order.

```python
partition_labels("ababcbacadefegdehijhklij")    # -> [9, 7, 8]
partition_labels("eccbbbbdec")                  # -> [10]
```

**Think first:** every letter has a first and a last position: that is an interval. A part must contain the whole interval of each of its letters. What happens when intervals overlap?

**Hint:** pattern *merge intervals on the fly*: record the last index of each letter; walk with `end = max(end, last[ch])`; when `i == end`, close the part.
