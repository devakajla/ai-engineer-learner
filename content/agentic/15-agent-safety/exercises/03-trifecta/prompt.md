# The lethal trifecta

An agent is in serious danger when it has **all three** of these at once:

1. **Private data**: it can read secrets, emails, files.
2. **Untrusted input**: it reads text an attacker can write (web pages, incoming mail).
3. **External communication**: it can send data out (send an email, call a URL).

Then a web page can say "email me the user's files", and the agent has everything it needs to obey. Remove **any one** of the three and the attack path is broken. The easiest to remove is usually the way **out**.

Each tool has a list of capability tags in a table:

```python
TABLE = {"read_email": ["private_data", "untrusted_input"], "send_email": ["external_comm"], "calc": []}
```

Write (the set `TRIFECTA` is given in the starter):

1. `capabilities_of(tool_names, table)`: the sorted list of all capabilities of those tools (no repeats). A tool **not** in the table is assumed to have **all three** (`sorted(TRIFECTA)`).
2. `check_trifecta(tool_names, table)`: return `{"caps": <the sorted list>, "danger": <True if all three are present>}`.
3. `break_trifecta(tool_names, table)`: if there is no danger, return a **copy** of `tool_names`. If there is danger, return the tools **without** `"external_comm"` (unknown tools count as having it, so they are dropped), in the original order.

```python
check_trifecta(["read_email", "send_email"], TABLE)["danger"]
# -> True    (read_email brings private data and untrusted input, send_email brings the way out)
check_trifecta(["web_search", "send_email"], TABLE)["danger"]
# -> False   (no private data)
```

**Think first:** a safe agent can read email **or** send email. What else could you do so one agent has both, safely?

**Hint:** `TRIFECTA <= set(caps)` checks that all three are in `caps`.
