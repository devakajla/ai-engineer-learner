# A toy embedder

Write `toy_embed(text, vocab)`. It turns a text into a vector by counting how often each vocabulary word appears.

`vocab` is a list of lowercase words. The result has one number per vocabulary word, in the same order.

Rules:
- Make the text lowercase and split it into words with `.split()`.
- Remove these characters from both ends of each word: `. , ! ?` (use `strip(".,!?")`).
- Count the words that are equal to each vocabulary word.
- Return a list of ints. Its length equals `len(vocab)`.

```python
vocab = ["task", "delete", "weather"]

toy_embed("Delete the task. Delete it!", vocab)    # -> [1, 2, 0]
toy_embed("Sunny weather", vocab)                  # -> [0, 0, 1]
toy_embed("", vocab)                               # -> [0, 0, 0]
```

**Think first:** what must the result length be when the text is empty?
