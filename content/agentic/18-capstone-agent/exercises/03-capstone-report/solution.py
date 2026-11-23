# Given from earlier exercises. Do not change these.
import math


def pass_rate(results):
    if not results:
        return 0.0
    return round(sum(1 for r in results if r["passed"]) / len(results), 2)


# Your task:
def percentile(values, p):
    if not values:
        return 0
    ordered = sorted(values)
    rank = math.ceil(p / 100 * len(ordered))
    return ordered[max(rank, 1) - 1]


def capstone_report(results):
    count = len(results)
    return {
        "cases": count,
        "pass_rate": pass_rate(results),
        "avg_steps": round(sum(r["steps"] for r in results) / count, 2) if count else 0.0,
        "total_tokens": sum(r["tokens"] for r in results),
        "p95_ms": percentile([r["ms"] for r in results], 95),
        "failed": [r["id"] for r in results if not r["passed"]],
    }


def format_report(report):
    failed = ", ".join(report["failed"]) if report["failed"] else "none"
    return "\n".join([
        f"Cases: {report['cases']}",
        f"Pass rate: {report['pass_rate']:.0%}",
        f"Average steps: {report['avg_steps']}",
        f"Total tokens: {report['total_tokens']}",
        f"p95 latency: {report['p95_ms']} ms",
        f"Failed: {failed}",
    ])
