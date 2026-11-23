# Clean extracted text

Text from a PDF is messy: page numbers, words broken at line ends, double spaces, many blank lines. Garbage in the index means garbage in the answers.

Write `clean_text(raw)`.

Rules (apply all of them):
1. Change Windows line ends `"\r\n"` to `"\n"`.
2. Join words that were broken with a hyphen at the end of a line: remove every `"-\n"`.
3. In every line, turn runs of spaces and tabs into one space and remove spaces at both ends of the line.
4. Delete lines that are only digits (page numbers). Do not delete a line like `"Step 2"`.
5. Never leave more than one blank line in a row.
6. Remove blank lines and spaces at the start and the end of the whole text.

```python
raw = "The exam-\nple  works.\r\n\r\n\r\n\r\n12\r\nNext   page."
clean_text(raw)
# -> 'The example works.\n\nNext page.'
```

**Think first:** what text could rule 2 damage?
