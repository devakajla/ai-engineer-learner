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
