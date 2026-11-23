# Split the thinking from the answer

A reasoning model can write its thinking inside the reply, between `<think>` and `</think>`. Separate the two.

Write `split_thinking(text)`. Return a tuple `(thinking, answer)`.

Rules:
- If `text` has no `<think>` tag, return `("", text.strip())`.
- If it has `<think>` and `</think>`: the thinking is the text between them, the answer is the text after `</think>`. Strip spaces from both.
- If it has `<think>` but **no** `</think>` (the model ran out of tokens while thinking): everything after `<think>` is the thinking, and the answer is `""`.
- Text before `<think>` is ignored.

**Think first:** What does `.find` give you when a tag is missing, and how do you jump past the tag itself?

**Hint:** The `split_note` example in the lesson. Use `len("<think>")`.

```python
split_thinking("<think>23-9=14</think>\nAnswer: 14")   # -> ('23-9=14', 'Answer: 14')
split_thinking("Just an answer.")                       # -> ('', 'Just an answer.')
split_thinking("<think>still thinking")                 # -> ('still thinking', '')
```
