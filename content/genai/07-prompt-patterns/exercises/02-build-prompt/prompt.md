# Build a prompt with delimiters

Write `build_prompt(document, question)`. It returns one string that holds the document inside tags, then the question.

The string must look **exactly** like this (with real newlines):

```
Answer only from the text between the tags. If the answer is not there, reply exactly: I don't know.

<document>
{document}
</document>

Question: {question}
```

Rules:
- The document is placed between `<document>` and `</document>`, each on its own line.
- Remove spaces and new lines from the start and end of `document` and `question` first (use `strip()`).
- There is no new line after the question.

```python
build_prompt("Paris is in France.", "Where is Paris?")
# -> "Answer only from the text between the tags. If the answer is not there, reply exactly: I don't know.\n\n<document>\nParis is in France.\n</document>\n\nQuestion: Where is Paris?"
```
