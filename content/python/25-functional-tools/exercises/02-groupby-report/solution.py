from collections import defaultdict
from itertools import groupby
from operator import itemgetter


def status_report(orders):
    key = itemgetter("status")
    report = []
    for status, group in groupby(sorted(orders, key=key), key=key):
        items = list(group)
        report.append((status, len(items), round(sum(o["amount"] for o in items), 2)))
    return report


def top_spenders(orders, n):
    totals = defaultdict(float)
    for o in orders:
        if o["status"] != "cancelled":
            totals[o["user"]] += o["amount"]
    ranked = sorted(totals.items(), key=lambda kv: (-kv[1], kv[0]))
    return [user for user, _ in ranked[:n]]
