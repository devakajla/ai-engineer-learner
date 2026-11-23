# A fair train and validation split

You keep some examples **out of training** (the **validation** set) to see if the model really learned, or only copied. Two rules matter: the sets must not overlap, and the split should be **stable**. If you add new data next week, old examples must not jump from one set to the other. A random shuffle breaks this. A **hash** of the example does not.

Write `split_dataset(lines, val_fraction=0.1)`. Return `(train, val)`, two lists that keep the original order.

For each line compute `bucket = int(hashlib.md5(line.encode("utf-8")).hexdigest(), 16) % 100`. The line goes to `val` if `bucket < round(val_fraction * 100)`, otherwise to `train`. (`import hashlib` is already in the starter.)

```python
train, val = split_dataset(lines, 0.1)
# about 10% of the lines are in val; the same line always lands in the same set
```

**Think first:** why is `random.shuffle` a poor choice when the dataset keeps growing?

**Hint:** a loop with one `append` to either list. The hash always gives the same number for the same text.
