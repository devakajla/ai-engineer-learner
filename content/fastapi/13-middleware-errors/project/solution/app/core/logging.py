import logging
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")

_base_factory = logging.getLogRecordFactory()


def _record_factory(*args, **kwargs) -> logging.LogRecord:
    """Stamp the current request id on EVERY log record, whichever logger or handler handles it."""
    record = _base_factory(*args, **kwargs)
    record.request_id = request_id_var.get()
    return record


def setup_logging(level: str = "INFO") -> None:
    logging.setLogRecordFactory(_record_factory)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(request_id)s] %(name)s: %(message)s"))
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)
