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
