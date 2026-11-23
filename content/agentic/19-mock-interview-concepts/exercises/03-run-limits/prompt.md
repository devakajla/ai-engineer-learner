# Interview drill 3: step cap and cost cap

**Asked as:** "How do you stop an agent from running for ever or spending too much? Show it in code."

You get the **cost of each step the agent wants to take** (a list of numbers in dollars). Run the steps one by one, but **stop before** a step if either limit would be broken.

Write `run_with_limits(step_costs, max_steps, max_cost)`:

- For each cost, **before** running the step:
  - if `ran >= max_steps`: stop with `"max_steps"`.
  - if `spent + cost > max_cost`: stop with `"max_cost"`.
  - otherwise run it: `spent += cost`, `ran += 1`.
- If all steps ran, stop reason is `"done"`.
- Return `{"ran": ran, "spent": round(spent, 4), "stopped": reason}`.

```python
run_with_limits([0.4, 0.4, 0.4], max_steps=10, max_cost=1.0)
# -> {'ran': 2, 'spent': 0.8, 'stopped': 'max_cost'}
```

**Think first:** why check the limit *before* the step and not after? What does an after-the-fact check cost you?

**Hint:** the checks are inside the loop, at the top. Round only in the returned dict.
