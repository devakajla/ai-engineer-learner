# Messages for one plan step

When you run a plan, each step is one model call. The model must see the **goal**, the **whole plan**, the **results of the earlier steps**, and the **current step**. Write `build_step_messages(goal, steps, results, i)`. It returns a list of two messages.

- `goal`: text. `steps`: list of step texts. `results`: list of the results so far. `i`: the index of the current step (starting at 0).
- Message 1 has role `system` and the exact content `"You are carrying out one step of a plan. Do only the current step."`
- Message 2 has role `user`. Its content is these parts, with **one blank line** (`"\n\n"`) between the parts:
  1. `Goal: <goal>`
  2. `Plan:` then one line per step, numbered from 1 as `1. <step>`
  3. `Results so far:` then one line per **finished** step (only `results[:i]`), numbered from 1 as `1. <result>`. If there are none, write the single line `(none yet)`.
  4. `Current step (<i+1> of <number of steps>): <steps[i]>`

```python
build_step_messages("Boil an egg", ["Fill a pot", "Boil it"], ["done"], 1)[1]["content"]
# -> 'Goal: Boil an egg\n\nPlan:\n1. Fill a pot\n2. Boil it\n\nResults so far:\n1. done\n\nCurrent step (2 of 2): Boil it'
```

For `i = 0` the "Results so far" part is `Results so far:\n(none yet)`.

**Think first:** why does the model need the whole plan and not only the current step? Why show only `results[:i]`?

**Hint:** `enumerate(items, start=1)` gives numbers from 1. `"\n".join(lines)` joins lines.
