# Split markdown by heading

Write `split_markdown(md)`. It cuts a markdown text into sections. It returns a list of dictionaries `{"heading": ..., "text": ...}`, in order.

Rules:
- A heading line starts with 1 to 6 `#` characters followed by a space, for example `## Delete a task`. The heading value is the title without the `#` characters, stripped: `"Delete a task"`.
- The `text` of a section is every line after the heading, up to the next heading, joined with `"\n"` and stripped.
- Text before the first heading belongs to a section with `heading` `""`.
- **Skip** sections whose text is empty.
- Lines inside a code fence (between lines that start with three backticks) are **never** headings. They stay in the text.

```python
md = "# Tasks\nAbout tasks.\n\n## Delete\nUse DELETE.\n## Empty\n## List\nUse GET."
split_markdown(md)
# -> [{'heading': 'Tasks', 'text': 'About tasks.'},
#     {'heading': 'Delete', 'text': 'Use DELETE.'},
#     {'heading': 'List', 'text': 'Use GET.'}]

split_markdown("Intro line\n# A\nbody")
# -> [{'heading': '', 'text': 'Intro line'}, {'heading': 'A', 'text': 'body'}]
```

**Think first:** what two things must you do when you meet a heading line? What must you do after the last line?

**Hint:** a `for line in md.splitlines()` loop, a list of current lines, and an `in_fence` flag.
