# Ask with retries

Write `ask_with_retry(client, messages, max_tries=3, sleep=None)`. It calls the model, and tries again if the call raises an error. Between tries it waits, using exponential backoff.

Your `backoff_delays(tries, base=1, cap=30)` function from the previous exercise is **given** in `starter.py`. Do not change it.

Rules:
- Call `client.chat.completions.create(model="qwen/qwen3.8-27b", messages=messages)`.
- On success, return `response.choices[0].message.content` right away.
- If the call raises any exception, try again, up to `max_tries` calls in total.
- If every try fails, raise the **last** exception.
- If `max_tries` is less than `1`, raise `ValueError("max_tries must be at least 1")`.
- Waiting: if `sleep` is not `None`, call `sleep(delay)` after each failed try **except the last one**. The delays come from `backoff_delays(max_tries - 1)`: first delay after the first failure, and so on.
- If `sleep` is `None`, do not wait. (Tests stay fast. Real code passes `time.sleep`.)

**Think first:** After which failures do you wait, and how many delays do you need?

**Hint:** Get the list of delays first. Use the try number as the index into it.

```python
ask_with_retry(client, messages)
# client fails once, then works -> returns the text (2 calls made)

ask_with_retry(client, messages, max_tries=3, sleep=waits.append)
# client fails twice, then works -> waits == [1, 2]

ask_with_retry(client, messages, max_tries=2)
# client always fails -> raises the error from the 2nd call
```
