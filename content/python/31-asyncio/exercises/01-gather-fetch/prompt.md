# Fetch many things at the same time

`fetch` is an `async` function that takes one url and returns text. Write two `async` functions:

- `fetch_all(fetch, urls)` runs `fetch(url)` for every url **at the same time** and returns the list of results in the same order as `urls`.
- `fetch_all_safe(fetch, urls)` does the same, but one failing url must not lose the others. For each url return `(url, result)` on success or `(url, None)` if `fetch` raised an error.

Both return `[]` for an empty list.

```python
async def fake(url):
    return url.upper()

asyncio.run(fetch_all(fake, ["a", "b"]))        # -> ["A", "B"]
# fetch_all_safe, where "bad" raises ValueError:
# -> [("a", "A"), ("bad", None), ("c", "C")]
```

**Think first:** If you `await` each fetch in a `for` loop, do they run together? What does `gather` return when one job raises an error?

**Hint:** `await asyncio.gather(*coroutines)`. For the safe version, add `return_exceptions=True` and check each result with `isinstance(result, Exception)`.
