# A retry decorator with arguments

Turn the retry pattern from the error-handling lesson into a decorator:

```python
@retry(attempts=3, exceptions=(ConnectionError,), base_delay=0.5, sleep=time.sleep)
def call_api(): ...
```

- retries only the listed exceptions, up to `attempts` calls total
- waits `base_delay * 2 ** (n - 1)` before the n-th retry, using the injected `sleep`
- re-raises the last exception when out of attempts; other exceptions propagate immediately
- preserves the function's metadata (`functools.wraps`)
- adds an attribute on the wrapper: `wrapper.attempts_made` = how many calls the **last** invocation needed

```python
@retry(attempts=3, exceptions=(ConnectionError,), sleep=lambda s: None)
def flaky(): ...
flaky(); flaky.attempts_made   # e.g. 2
```
