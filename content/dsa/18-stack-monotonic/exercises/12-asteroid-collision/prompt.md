# Asteroid collision

Asteroids move along a line. Each number is one asteroid: the sign is the **direction** (positive right, negative left) and the size is `abs(value)`. All move at the same speed. When two meet, the **smaller explodes**; if equal, both explode. Asteroids moving the same way never meet. Write `asteroid_collision(asteroids)` that returns the asteroids left, in order.

```python
asteroid_collision([5, 10, -5])     # -> [5, 10]
asteroid_collision([8, -8])         # -> []
```

**Think first:** which asteroids can collide: only a right-mover followed by a left-mover. Who is the left-mover fighting?

**Hint:** pattern *stack*: for a left-mover `x < 0`, `while stack and stack[-1] > 0` and it is smaller than `-x`: pop. Then decide: equal pops the top too, a bigger top kills `x`, else push `x`.
