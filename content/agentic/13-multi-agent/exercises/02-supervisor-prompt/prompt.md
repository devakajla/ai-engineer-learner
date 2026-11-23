# The supervisor's question

In the **supervisor pattern** one agent does not do the work. It **routes**: it looks at the task and the work so far, and names the next worker, or says `FINISH`. This is the router of lesson 3, with a model making the choice.

The starter gives you `ask`, `run_worker` and `format_results` from exercise 1. Write:

1. `supervisor_prompt(task, workers, results)`. `workers` is a dict `{name: {"description": ..., "system": ...}}`. Return exactly this text:
   ```
   Task: <task>

   Workers:
   - <name>: <description>
   - <name>: <description>

   Work so far:
   <format_results(results), or (nothing yet) if results is empty>

   Which worker should act next? Reply with one worker name, or FINISH if the task is done.
   ```
   (one blank line between the parts; the last line has no `\n` at the end).
2. `parse_choice(reply, names)`: clean the reply with `reply.strip().strip(".!\"' `")`. If it equals a name in `names` (ignore case) return **that name as written in `names`**. If it equals `FINISH` (ignore case) return `"FINISH"`. Anything else (extra words, empty) returns `None`.

```python
parse_choice("  Writer. ", ["researcher", "writer"])      # -> 'writer'
parse_choice("the researcher please", ["researcher"])      # -> None
```

**Think first:** why return `None` for "the researcher please" instead of guessing "researcher"?

**Hint:** an exact match is strict on purpose. A guess can send work to the wrong agent.
