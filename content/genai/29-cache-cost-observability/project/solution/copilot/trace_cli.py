"""Trace one question, or run an agent eval and compare it with a baseline. Usage:

    python -m copilot.trace_cli ask "how do I delete a task"
    python -m copilot.trace_cli eval evals/agent_cases.json              # prints the results
    python -m copilot.trace_cli eval evals/agent_cases.json baseline.json  # also runs the gate
"""

import json
import sys

from copilot.llm import get_client
from copilot.store import open_collection
from copilot.tracing import gate, load_json, pass_rate, percentile, run_eval, trace_summary, traced_rag

DB_PATH = ".chroma"


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return
    client = get_client()
    collection = open_collection(DB_PATH)
    if sys.argv[1] == "ask":
        out = traced_rag(client, collection, " ".join(sys.argv[2:]))
        for span in out["trace"]:
            print(span)
        print(trace_summary(out["trace"]))
        print(out["answer"])
        return
    cases = load_json(sys.argv[2])
    results = run_eval(lambda question: traced_rag(client, collection, question), cases)
    print(f"cases: {len(results)}   pass rate: {pass_rate(results)}   p95 ms: {percentile([r['ms'] for r in results], 95)}")
    for r in results:
        if not r["passed"]:
            print("failed:", r["id"], r.get("error", ""))
    if len(sys.argv) > 3:
        verdict = gate(load_json(sys.argv[3]), results)
        print("gate:", "ok" if verdict["ok"] else "BLOCKED: " + "; ".join(verdict["reasons"]))
    with open("last_results.json", "w", encoding="utf-8") as file:
        json.dump(results, file, indent=2)
    print("saved last_results.json (copy it to baseline.json when you accept the result)")


if __name__ == "__main__":
    main()
