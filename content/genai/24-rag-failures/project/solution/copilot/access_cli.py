"""Ask as a given user. Usage:

    python -m copilot.access_cli acme eng "how do I create a task"
    python -m copilot.access_cli acme hr "what are the salary bands"

The rules come from access.json (copy access.example.json and edit it).
"""

import sys
from datetime import date

from copilot.access import answer_for_user, load_access
from copilot.llm import get_client
from copilot.store import open_collection

DB_PATH = ".chroma"
ACCESS_PATH = "access.json"


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        return
    user = {"tenant": sys.argv[1], "groups": [g for g in sys.argv[2].split(",") if g]}
    question = " ".join(sys.argv[3:])
    result = answer_for_user(
        get_client(), open_collection(DB_PATH), load_access(ACCESS_PATH), user, question,
        today=date.today().isoformat(), max_age_days=365,
    )
    print(result["answer"])
    for source in result["sources"]:
        print(f"[{source['n']}] {source['source']} > {source['heading']}")


if __name__ == "__main__":
    main()
