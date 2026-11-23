# Price string to paise

A payment API sends prices as strings in rupees, like `"19.99"`. Write `to_paise(price)` that returns the price as an **int number of paise** (1 rupee = 100 paise).

```python
to_paise("19.99")  # -> 1999
to_paise("5")      # -> 500
to_paise("0.10")   # -> 10
to_paise(" 2.5 ")  # -> 250   (spaces around are allowed)
```

Careful: one obvious approach is wrong for some inputs. Re-read "The `int(float * 100)` trap".
