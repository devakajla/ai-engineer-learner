"""Score the search on your golden questions. Usage:

    python -m copilot.docs_cli sync docs
    python -m copilot.eval_cli evals/golden.json
"""

import sys

from copilot.evals import compare_retrievers, load_cases
from copilot.store import open_collection

DB_PATH = ".chroma"


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "evals/golden.json"
    cases = load_cases(path)
    results = compare_retrievers(open_collection(DB_PATH), cases, k=3)
    print(f"{'retriever':<10} {'recall@3':>9} {'precision@3':>12} {'mrr':>6}")
    for name, result in results.items():
        print(f"{name:<10} {result['recall']:>9} {result['precision']:>12} {result['mrr']:>6}")
    for name, result in results.items():
        if result["misses"]:
            print(f"\n{name} missed: " + "; ".join(result["misses"]))


if __name__ == "__main__":
    main()
