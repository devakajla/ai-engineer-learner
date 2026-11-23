# Phone letter combinations

On an old phone: `2 -> abc`, `3 -> def`, `4 -> ghi`, `5 -> jkl`, `6 -> mno`, `7 -> pqrs`, `8 -> tuv`, `9 -> wxyz`. Write `letter_combinations(digits)` that returns all strings the digits could spell, in **alphabetical order**. For an empty string return `[]`.

```python
letter_combinations("23")    # -> ["ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf"]
letter_combinations("")      # -> []
```

**Think first:** for each digit you choose one letter. After you choose, what is left to solve?

**Hint:** pattern *choose one per position*: `go(i, current)`: for each letter of `digits[i]`, recurse with `current + letter`; when `i == len(digits)` save it.
