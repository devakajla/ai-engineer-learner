# Classify with a label list

Write `classify(client, text, labels)`. It asks the model to put `text` into one of the `labels`, and returns a clean label.

The function `pick_label(reply, labels)` from the lesson is **given** in `starter.py`. Use it for the cleaning step. Do not change it.

Rules:
- Send one `user` message with this exact text (labels joined with `", "`):
  `Classify the text as one of: <labels>. Answer with only the label.\n\nText: <text>`
- Call `client.chat.completions.create(model="qwen/qwen3.8-27b", messages=messages, temperature=0)`.
- Clean the reply: `strip()`, then `lower()`, then remove dots from both ends with `strip(".")`.
- If the cleaned reply is in `labels`, return it. Otherwise return `"unknown"`.
- `labels` are all lowercase.

```python
classify(client, "I love it", ["positive", "negative"])
# model says "  Positive.\n"  -> 'positive'

classify(client, "meh", ["positive", "negative"])
# model says "It is hard to say"  -> 'unknown'
```
