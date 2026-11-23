# Few-shot messages

Write `few_shot_messages(system, examples, question)`. It builds the list of messages for a few-shot prompt.

`examples` is a list of `(input, output)` pairs.

Rules:
- The first message is the system message.
- Then, for each example, a `user` message with the input and an `assistant` message with the output. Keep the order of the examples.
- The last message is a `user` message with the `question`.

```python
few_shot_messages("Label the sentiment.", [("I love it", "positive")], "So bad")
# -> [{'role': 'system', 'content': 'Label the sentiment.'},
#     {'role': 'user', 'content': 'I love it'},
#     {'role': 'assistant', 'content': 'positive'},
#     {'role': 'user', 'content': 'So bad'}]

few_shot_messages("Be brief.", [], "Hi")
# -> [{'role': 'system', 'content': 'Be brief.'}, {'role': 'user', 'content': 'Hi'}]
```
