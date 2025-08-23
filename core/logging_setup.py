# core/logging_setup.py
import logging

_old_factory = logging.getLogRecordFactory()

def record_factory(*args, **kwargs):
    record = _old_factory(*args, **kwargs)
    # always provide request_id (default = "-")
    if not hasattr(record, "request_id"):
        record.request_id = getattr(logging, "_current_request_id", "-")
    return record

logging.setLogRecordFactory(record_factory)
