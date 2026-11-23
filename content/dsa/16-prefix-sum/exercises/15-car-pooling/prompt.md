# Car pooling

A car has `capacity` seats and only drives **east**. Each trip is `[passengers, start, end]`: those passengers get in at `start` and get out at `end` (people leaving at a point go out **before** new people get in). Write `car_pooling(trips, capacity)` that returns `True` if the car can do all trips without ever having more than `capacity` people.

```python
car_pooling([[2, 1, 5], [3, 3, 7]], 4)    # -> False
car_pooling([[2, 1, 5], [3, 3, 7]], 5)    # -> True
```

**Think first:** how many people are in the car at each point? Is that "add on start, subtract on end" for every trip?

**Hint:** pattern *difference array*: `diff[start] += p`, `diff[end] -= p`; the running sum is the number of people. Check it never goes above `capacity`.
