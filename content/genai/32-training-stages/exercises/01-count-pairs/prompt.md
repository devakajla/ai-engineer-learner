# Count which word follows which

Pretraining in miniature: read some text and count which word follows which word.

Write `count_pairs(text)`. Return a dictionary of dictionaries: `{word: {next word: how many times}}`.

Rules:
- Make the text lowercase, then split it into words with `.split()`.
- Look at each word and the word right after it (a sliding pair). The last word has no next word.
- Text with fewer than 2 words gives `{}`.

**Think first:** In the lesson, the "banana" example counted letters. What changes when you count words? What do you loop over?

**Hint:** Use a nested dictionary and `.get(x, 0) + 1`.

```python
count_pairs("the cat sat the cat ran")
# -> {'the': {'cat': 2}, 'cat': {'sat': 1, 'ran': 1}, 'sat': {'the': 1}}

count_pairs("Hi")
# -> {}
```
