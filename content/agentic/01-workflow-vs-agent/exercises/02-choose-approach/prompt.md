# Pick the simplest approach

Write `choose_approach(steps_known, needs_tools, high_risk=False)`. All three arguments are `True` or `False`. It returns one of these words:

- `"single_call"`: the task needs **no tools**. One model call is enough.
- `"workflow"`: the task needs tools **and** you know the steps in advance. Your code runs the fixed path.
- `"agent"`: the task needs tools, the steps are **not** known, and the risk is low. The model decides the steps.
- `"agent_with_approval"`: like `"agent"`, but `high_risk` is `True`. A human must approve risky actions.

Check the rules in this order: tools first, then known steps, then risk. Known steps win over risk, because fixed code is safer than a model's choice.

```python
choose_approach(steps_known=True, needs_tools=False)                  # -> 'single_call'
choose_approach(steps_known=True, needs_tools=True)                   # -> 'workflow'
choose_approach(steps_known=False, needs_tools=True)                  # -> 'agent'
choose_approach(steps_known=False, needs_tools=True, high_risk=True)  # -> 'agent_with_approval'
```

**Think first:** why does a task with no tools never need an agent, even when the steps are not known?

**Hint:** use `if ...: return ...` one after the other. The first rule that fits decides.
