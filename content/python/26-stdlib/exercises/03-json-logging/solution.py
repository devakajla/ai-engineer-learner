import json
import logging
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)


def _encode(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, set):
        return sorted(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def to_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, default=_encode)


def import_rows(rows: list[dict]) -> list[int]:
    ids = []
    for i, row in enumerate(rows):
        if "id" not in row:
            logger.warning("skipping row %s: missing id", i)
            continue
        ids.append(row["id"])
    logger.info("imported %d rows", len(ids))
    return ids
