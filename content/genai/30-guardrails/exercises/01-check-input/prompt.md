# Check the input before the model sees it

The cheapest guardrail is a plain check **before** you spend any money. Write `check_input(text, max_chars=2000, banned=None)`. It returns `{"ok": True, "reason": ""}` or `{"ok": False, "reason": "..."}`.

Check in this order, and stop at the first problem:
1. The text is empty or only spaces: `"empty"`.
2. `len(text) > max_chars`: `"too long"`.
3. Any phrase of the list `banned` (may be `None`) is inside the text, ignoring upper and lower case: `"banned phrase: " + phrase` (write the phrase as it is in the list).
4. Otherwise it is fine.

```python
check_input("Hello")                                   # -> {'ok': True, 'reason': ''}
check_input("   ")                                     # -> {'ok': False, 'reason': 'empty'}
check_input("x" * 11, max_chars=10)                    # -> {'ok': False, 'reason': 'too long'}
check_input("Please IGNORE previous instructions", banned=["ignore previous instructions"])
# -> {'ok': False, 'reason': 'banned phrase: ignore previous instructions'}
```

**Think first:** a banned-phrase list is easy to get around ("1gnore previous..."). So why is it still worth having?
