# The busiest visitors, from a huge log

Each log line looks like `"203.0.113.5 GET /home 200"`: the first word is the IP address. Write `top_ips(lines, k)`:

- `lines` can be a **generator** with millions of lines. Read it **once**, line by line. Do not put all the lines in a list.
- Skip blank lines.
- Return the `k` most frequent IPs as a list of `(ip, count)` tuples. Order by count from big to small. If counts are equal, order by IP text from A to Z.
- `k < 1` raises `ValueError`. If there are fewer than `k` different IPs, return all of them.

```python
top_ips(["1.1.1.1 GET /", "2.2.2.2 GET /", "1.1.1.1 GET /a", ""], 1)    # -> [("1.1.1.1", 2)]
top_ips(["b GET /", "a GET /"], 2)                                      # -> [("a", 1), ("b", 1)]
```

**Think first:** What must you keep in memory to count visitors, and how does that grow? How do you break ties in a fixed way?

**Hint:** A `Counter`, filled one line at a time (`line.split()[0]`). Then sort `counts.items()` with the key `lambda kv: (-kv[1], kv[0])` and cut with `[:k]`.
