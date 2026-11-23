import json
import logging
from datetime import datetime
from decimal import Decimal


def to_json(obj):
    return json.dumps(obj)


def import_rows(rows):
    ids = []
    for i, row in enumerate(rows):
        if "id" not in row:
            print("bad row", i)
            continue
        ids.append(row["id"])
    return ids
