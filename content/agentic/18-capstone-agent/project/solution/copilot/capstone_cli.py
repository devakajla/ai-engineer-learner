"""The capstone agent. Usage:

    python -m copilot.capstone_cli ask "how do I delete a task"
    python -m copilot.capstone_cli ask "what tasks are open"       # needs TaskFlow running
    python -m copilot.capstone_cli eval evals/capstone_cases.json  # prints the report
"""

import sys
import time

from copilot.capstone import answer_question, build_tools, capstone_report, fetch_tasks, format_report, run_cases
from copilot.llm import get_client
from copilot.store import open_collection
from copilot.tracing import load_json, trace_summary

DB_PATH = ".chroma"
BANNED = ["ignore previous instructions", "ignore your rules"]


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return
    client = get_client()
    tools = build_tools(open_collection(DB_PATH), fetch_tasks)
    if sys.argv[1] == "ask":
        out = answer_question(client, " ".join(sys.argv[2:]), tools, [], time.perf_counter, banned=BANNED)
        for span in out["trace"]:
            print(span)
        print(trace_summary(out["trace"]))
        print(f"route: {out['route']}")
        print(out["answer"])
        return
    results = run_cases(client, load_json(sys.argv[2]), tools)
    print(format_report(capstone_report(results)))


if __name__ == "__main__":
    main()
