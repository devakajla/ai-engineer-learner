# Write lines

Write `write_lines(path, lines)` that writes each string in `lines` to the file at `path`, one per line (each ending with `"\n"`). It should replace any old content. `path` is a `str` or `Path`.

```python
write_lines("out.txt", ["a", "b"])   # file content: "a\nb\n"
write_lines("empty.txt", [])         # file content: ""
```
