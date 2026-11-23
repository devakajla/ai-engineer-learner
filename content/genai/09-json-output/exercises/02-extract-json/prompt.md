# Extract a JSON object from a messy reply

Models often put words or a code fence around the JSON. Write `extract_json(text)` to find the JSON object and return it as a dictionary.

Rules:
- The object starts at the **first** `{` and ends at the **last** `}`. Take that part of the text.
- Parse it with `json.loads`.
- If there is no `{` and `}` pair, or the part is not valid JSON, return `None`.

```python
extract_json('Sure! Here it is: {"a": 1} Hope that helps.')   # -> {'a': 1}
extract_json('```json\n{"name": "Dev"}\n```')                  # -> {'name': 'Dev'}
extract_json("no json here")                                    # -> None
extract_json("{oops}")                                          # -> None
```
