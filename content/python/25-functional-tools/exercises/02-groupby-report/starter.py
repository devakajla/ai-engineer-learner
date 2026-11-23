from itertools import groupby
from operator import itemgetter


def status_report(orders):
    return [(k, len(list(g)), 0) for k, g in groupby(orders, key=itemgetter("status"))]


def top_spenders(orders, n):
    pass
