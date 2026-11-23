# Given from earlier exercises. Do not change these.
import math


def pass_rate(results):
    if not results:
        return 0.0
    return round(sum(1 for r in results if r["passed"]) / len(results), 2)


# Your task:
def percentile(values, p):
    ...


def capstone_report(results):
    ...


def format_report(report):
    ...
