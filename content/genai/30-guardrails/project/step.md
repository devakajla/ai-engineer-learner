# Step 22 — Guardrails around Copilot

Copilot now answers from docs and calls tools. Real users and real documents bring risks: huge inputs, personal data in questions, text that tries to give the model orders, and tools that should not run. Guardrails (lesson 30) are **small, boring checks in code** that run before and after the model. No single one is enough. Together they are **defence in depth**.

Your folder after this step (new files marked):

```
devdocs-copilot/
└── copilot/
    ├── guardrails.py   <- new
    ├── guard_cli.py    <- new
    ├── agent.py        <- changed: a `runner` option
    └── ... (all files from step 21)
```

### 1. `copilot/guardrails.py`

```python
"""Guardrails: check the input, hide personal data, control which tools may run, and check the output."""

import json

from copilot.embed import embed_texts
from copilot.llm import DEFAULT_MODEL
from copilot.rag import answer as rag_answer
from copilot.tools import run_tool_call

REFUSAL = "Sorry, I can't help with that request."


def check_input(text, max_chars=2000, banned=None):
    """The cheap checks first: empty, too long, banned phrase. Returns {"ok", "reason"}."""
    if not text.strip():
        return {"ok": False, "reason": "empty"}
    if len(text) > max_chars:
        return {"ok": False, "reason": "too long"}
    lowered = text.lower()
    for phrase in banned or []:
        if phrase.lower() in lowered:
            return {"ok": False, "reason": "banned phrase: " + phrase}
    return {"ok": True, "reason": ""}


def redact_pii(text):
    """Replace e-mail addresses and phone numbers with [EMAIL] and [PHONE]. Simple on purpose."""
    result = []
    for word in text.split(" "):
        core = word.rstrip(".,;:!?")
        tail = word[len(core):]
        at = core.find("@")
        digits = [char for char in core if char.isdigit()]
        only_phone_chars = all(char.isdigit() or char in "+-" for char in core)
        if at > 0 and "." in core[at + 1 :] and not core.endswith("."):
            result.append("[EMAIL]" + tail)
        elif only_phone_chars and len(digits) >= 10:
            result.append("[PHONE]" + tail)
        else:
            result.append(word)
    return " ".join(result)


def allow_tool_call(name, args, allowed, risky, approve):
    """May this tool run? Not on the allow-list: no. A risky tool needs approve(name, args) to say yes."""
    if name not in allowed:
        return {"ok": False, "reason": "tool not allowed"}
    if name in risky and not approve(name, args):
        return {"ok": False, "reason": "not approved"}
    return {"ok": True, "reason": ""}


def guarded_tool_call(call, functions, spec, allowed, risky, approve):
    """Like run_tool_call, but the guard decides first. A blocked call becomes an error text for the model."""
    try:
        args = json.loads(call.function.arguments)
    except json.JSONDecodeError:
        args = {}
    check = allow_tool_call(call.function.name, args, allowed, risky, approve)
    if not check["ok"]:
        return {"role": "tool", "tool_call_id": call.id, "content": f"error: blocked ({check['reason']})"}
    return run_tool_call(call, functions, spec)


def guarded_answer(client, collection, text, max_chars=2000, banned=None, k=3, embed=embed_texts,
                   model=DEFAULT_MODEL, base_delay=1.0):
    """RAG with guards on both sides. Returns {"answer", "hits", "blocked", "reason"}.

    blocked is None, "input" or "output". Personal data is hidden before the model sees it and before the user does.
    """
    check = check_input(text, max_chars, banned)
    if not check["ok"]:
        return {"answer": REFUSAL, "hits": [], "blocked": "input", "reason": check["reason"]}
    result = rag_answer(client, collection, redact_pii(text), k=k, embed=embed, model=model, base_delay=base_delay)
    reply = redact_pii(result["answer"] or "")
    if not reply.strip():
        return {"answer": REFUSAL, "hits": result["hits"], "blocked": "output", "reason": "empty answer"}
    return {"answer": reply, "hits": result["hits"], "blocked": None, "reason": ""}
```

Read it in parts:

1. **`check_input`** is the cheapest guard: empty, too long, or a banned phrase. It costs nothing and no model call happens. A blocked request gets a fixed `REFUSAL`, never a model-written one. The banned-phrase list is **not** real protection against injection (attackers rephrase), only a first filter.
2. **`redact_pii`** replaces e-mail addresses and phone numbers by `[EMAIL]` and `[PHONE]`. It works word by word and ignores punctuation at the end of a word. A short number such as `12345` is not a phone number (fewer than 10 digits). It is **simple on purpose**. For real products use a proper PII library and test it with your own data.
3. **`allow_tool_call`** is the rule for tools: a name that is not on the **allow-list** never runs, and a **risky** tool also needs `approve(name, args)` to say yes (a human click, a policy check). Least privilege means the agent only gets the tools the task needs.
4. **`guarded_tool_call`** puts that rule in front of `run_tool_call`. A blocked call returns `error: blocked (reason)` as the tool message, so the model **learns** that it cannot do that and can answer without it. Nothing crashes, and the blocked function never runs.
5. **`guarded_answer`** is RAG with guards on both sides:
   - input check first (no model call when it fails),
   - redact the question before retrieval and before the prompt,
   - call the normal `answer` from step 12,
   - redact the **answer** too (the docs might contain an e-mail address),
   - an empty answer is replaced by the refusal, with `blocked: "output"`.

   It returns `blocked` (`None`, `"input"` or `"output"`) and a `reason`, so your logs show which guard fired.

### 2. A small change in `copilot/agent.py`

The agent must use the guarded runner, so `agent_step` and `run_agent_safe` get one new option, `runner`. It defaults to `run_tool_call`, so old code keeps working. Change these lines:

```python
def agent_step(client, messages, tools, functions, spec, model=DEFAULT_MODEL, runner=run_tool_call):
    ...
        new_messages = new_messages + [runner(call, functions, spec)]


def run_agent_safe(client, question, spec, tools=TOOLS, functions=FUNCTIONS, system=AGENT_SYSTEM,
                   max_steps=5, max_repeats=2, model=DEFAULT_MODEL, runner=run_tool_call):
    ...
        result = agent_step(client, messages, tools, functions, spec, model=model, runner=runner)
```

Use it like this. `partial` fixes the guard settings and leaves the three arguments the agent supplies:

```python
from functools import partial
from copilot.guardrails import guarded_tool_call

runner = partial(guarded_tool_call, allowed=["list_endpoints"], risky=[], approve=lambda name, args: False)
result = run_agent_safe(client, "describe GET /tasks", spec, runner=runner)
```

Here `describe_endpoint` is not on the allow-list, so the model gets `error: blocked (tool not allowed)`.

### 3. Run it: `copilot/guard_cli.py`

```python
"""Ask the docs with guardrails on. Usage:

    python -m copilot.guard_cli "how do I delete a task? my email is sam@example.com"
"""

import sys

from copilot.guardrails import guarded_answer
from copilot.llm import get_client
from copilot.store import open_collection

DB_PATH = ".chroma"
BANNED = ["ignore previous instructions", "ignore your rules"]


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    result = guarded_answer(get_client(), open_collection(DB_PATH), " ".join(sys.argv[1:]), banned=BANNED)
    print(result["answer"])
    if result["blocked"]:
        print(f"(blocked at {result['blocked']}: {result['reason']})")


if __name__ == "__main__":
    main()
```

Try: `how do I delete a task? my email is sam@example.com`. The model never sees the address. Then try a banned phrase, and see that no model call is made.

> Guardrails reduce risk. They do not remove it. Keep the other layers: tool output as untrusted data (agentic lesson 15), access filters (step 16), step caps (step 20), and tests with attack cases.

### Checkpoint

Run the tests. Then write three attack questions of your own (a banned phrase, a very long text, a question with a phone number) and check what each guard does. Note one attack that **gets through**. That is your next test.
