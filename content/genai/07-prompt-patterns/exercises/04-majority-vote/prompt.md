# Majority vote (self-consistency)

You asked the model the same hard question several times and got several answers. Take the answer that came up the most.

The function `clean_answer(text)` is **given** in `starter.py`. It removes spaces and a final dot, and makes the text lowercase. Do not change it.

Write `majority_answer(answers)`:
- Clean every answer with `clean_answer`.
- Count how many times each cleaned answer appears.
- Return the answer with the biggest count.
- If two answers have the same count, return the one that appeared **first** in the list.
- An empty list gives `None`.

**Think first:** What do you count, and what do you remember while you look for the biggest count?

**Hint:** The counter-dict pattern from the votes example in the lesson.

```python
majority_answer(["Answer: 5", "answer: 5.", "Answer: 6"])   # -> 'answer: 5'
majority_answer(["a", "b", "b"])                            # -> 'b'
majority_answer(["a", "b"])                                 # -> 'a'
majority_answer([])                                         # -> None
```
