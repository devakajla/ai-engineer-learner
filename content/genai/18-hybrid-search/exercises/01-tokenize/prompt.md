# Tokenize for keyword search

Write `tokenize(text)`. It turns a text into a list of lowercase words for keyword search.

Rules:
- Make the text lowercase and split it on whitespace (`.split()`).
- Strip these characters from **both ends** of each word: `.` `,` `;` `:` `!` `?` `(` `)` `"` `'` and the backtick `` ` ``.
- Do not change the inside of a word (`x-api-key` and `/tasks/{id}` stay whole).
- Drop words that are empty after stripping.

```python
tokenize("Use `DELETE /tasks/{id}`.")      # -> ['use', 'delete', '/tasks/{id}']
tokenize("Error 429: too many requests!")  # -> ['error', '429', 'too', 'many', 'requests']
tokenize("... ?!")                         # -> []
tokenize("Send the X-API-Key header.")     # -> ['send', 'the', 'x-api-key', 'header']
```

**Think first:** why is it important that `429` and `x-api-key` stay whole?
