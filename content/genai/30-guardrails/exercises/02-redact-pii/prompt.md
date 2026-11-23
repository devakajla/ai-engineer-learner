# Hide personal data

**PII** (personally identifiable information) means things like emails and phone numbers. Do not send them to a model provider, and do not show them in answers or logs unless you must. Replace them first.

Write `redact_pii(text)`. No `re` module is needed. Work on the words of the text (split on a single space `" "`, and join with `" "` again, so the spacing stays).

For each word:
- Remove trailing punctuation `. , ; : ! ?` to get the **core**, and remember it as the **tail** (it is put back after the replacement).
- **Email**: the core has an `@` that is **not** the first character, and at least one `.` after the `@` (and the core does not end with a dot, which cannot happen after the punctuation removal). Replace the core with `[EMAIL]`.
- **Phone**: the core has only digits, `+` and `-`, and has **10 or more digits**. Replace the core with `[PHONE]`.
- Any other word stays as it is.

```python
redact_pii("Mail me at asha@example.com, or call 9876543210.")
# -> 'Mail me at [EMAIL], or call [PHONE].'
redact_pii("Order 12345 shipped @ noon")
# -> 'Order 12345 shipped @ noon'        (too few digits, and "@" alone is not an email)
```

**Think first:** what PII does this simple method miss? (names, addresses, phones written with spaces...) What would you use in production?
