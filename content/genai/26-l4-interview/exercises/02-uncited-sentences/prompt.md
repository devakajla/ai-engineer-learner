# Find the sentences without a citation

A grounded answer cites every fact. Write `uncited_sentences(answer)`. It returns the sentences that have **no** citation marker like `[1]`, in order.

Rules:
- A sentence ends at `.`, `!` or `?` when the next character is a space or the end of the text. (So `3.5` does not end a sentence.)
- The marker is placed **before** the final punctuation: `Use DELETE [1].`
- A marker is `[` + digits + `]`. `[x]` and `[]` do not count.
- Return the sentences stripped of spaces at both ends. Text after the last punctuation counts as a sentence if it is not empty.
- No `re` module is needed.

```python
uncited_sentences("Use DELETE [1]. It is fast. Send a token [2].")
# -> ['It is fast.']
uncited_sentences("Version 3.5 is out [1].")      # -> []
```

**Think first:** why can a sentence with a valid marker still be wrong? (Lesson 22.)
