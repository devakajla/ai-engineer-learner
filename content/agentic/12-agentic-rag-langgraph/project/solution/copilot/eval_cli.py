"""Score Copilot on your golden questions. Usage:

    python -m copilot.docs_cli sync docs
    python -m copilot.eval_cli evals/golden.json            # search only, no model calls
    python -m copilot.eval_cli evals/golden.json answers    # full check, uses the model (costs tokens)
"""

import sys

from copilot.evals import compare_retrievers, load_cases
from copilot.judge import evaluate_answers
from copilot.llm import get_client
from copilot.store import open_collection

DB_PATH = ".chroma"


def print_retrieval(collection, cases):
    results = compare_retrievers(collection, cases, k=3)
    print(f"{'retriever':<10} {'recall@3':>9} {'precision@3':>12} {'mrr':>6}")
    for name, result in results.items():
        print(f"{name:<10} {result['recall']:>9} {result['precision']:>12} {result['mrr']:>6}")
    for name, result in results.items():
        if result["misses"]:
            print(f"\n{name} missed: " + "; ".join(result["misses"]))


def print_answers(collection, cases):
    result = evaluate_answers(get_client(), collection, cases)
    print(f"questions: {result['n']}   average judge score: {result['average']}")
    for name, count in result["report"]["counts"].items():
        print(f"{name:<16} {count}")
    for name, questions in result["report"]["by_category"].items():
        if name != "ok" and questions:
            print(f"\n{name}: " + "; ".join(questions))
    if result["unscored"]:
        print("\nthe judge could not score: " + "; ".join(result["unscored"]))


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "evals/golden.json"
    cases = load_cases(path)
    collection = open_collection(DB_PATH)
    if len(sys.argv) > 2 and sys.argv[2] == "answers":
        print_answers(collection, cases)
    else:
        print_retrieval(collection, cases)


if __name__ == "__main__":
    main()
