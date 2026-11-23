"""Ask the agent about an OpenAPI spec. Usage:

    python -m copilot.agent_cli openapi.json "which endpoints change a task?"
"""

import sys

from copilot.agent import load_spec, run_agent_safe, tool_names_used
from copilot.llm import get_client


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return
    spec = load_spec(sys.argv[1])
    result = run_agent_safe(get_client(), sys.argv[2], spec)
    print("tools used:", ", ".join(tool_names_used(result["messages"])) or "none")
    print(f"steps: {result['steps']}   stopped: {result['stopped']}")
    print(result["answer"] or "(no answer)")


if __name__ == "__main__":
    main()
