# Temporarily set environment variables

Tests often need env vars changed **only for a block**. Write a class-based context manager `temp_env(**vars)`:

- on enter: set each `os.environ[NAME] = value`; a value of `None` means **unset** that variable during the block
- on exit: restore **exactly** the previous state — variables that existed get their old values back, variables that didn't exist are removed
- restore even if the block raises; don't suppress exceptions

```python
os.environ["MODE"] = "dev"
with temp_env(MODE="test", NEW_VAR="1"):
    os.environ["MODE"]     # -> "test"
os.environ["MODE"]         # -> "dev"
"NEW_VAR" in os.environ    # -> False
```
