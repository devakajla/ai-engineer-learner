# Maximum points from cards

Cards lie in a row with points `cards[i]`. In each of `k` turns you take **one card from the left end or the right end**. Write `max_points(cards, k)` that returns the biggest total you can reach. `1 <= k <= len(cards)`.

```python
max_points([1, 2, 3, 4, 5, 6, 1], 3)    # -> 12   (1 + 6 + 5)
max_points([2, 2, 2], 2)                # -> 4
```

**Think first:** the cards you do **not** take form one block in the middle. How long is it, and what do you want its sum to be?

**Hint:** pattern *fixed window on the complement*: slide a window of size `len(cards) - k` and find the **smallest** sum; answer is `total - smallest`.
