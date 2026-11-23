# Grade the whole golden set

Run your RAG on every golden question and let the judge grade each answer. In the starter: `build_judge_messages`, `parse_verdict` and `judge`.

Write `run_golden(client, cases, answer_fn, threshold=4)`.

- `cases`: a list of `{"question": ...}`.
- `answer_fn(question)` runs your RAG and returns `{"answer": text, "hits": [{"text": ...}, ...]}`.

For each case:
1. Call `answer_fn(question)`.
2. Build the judge context: the `"text"` of all the hits joined with a blank line (`"\n\n"`).
3. Call `judge(client, question, context, result["answer"])`.
4. If the score is `None`, add the question to `unscored` and go on (it does not count in the average).
5. Otherwise keep the score. If it is **below** `threshold`, add the question to `failed`.

Return `{"n": number of cases, "average": ..., "failed": [...], "unscored": [...]}`. The average is over the scored cases only, rounded to 2 decimals, and `0.0` if there are none.

```python
run_golden(client, [{"question": "q1"}, {"question": "q2"}], answer_fn)
# judge gives 5 and 2  ->  {'n': 2, 'average': 3.5, 'failed': ['q2'], 'unscored': []}
```

**Think first:** why is it risky to have the same model write and judge the answers?
