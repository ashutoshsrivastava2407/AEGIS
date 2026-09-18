"""Structured JSON Logger for AEGIS Platform."""

import logging
import json
import sys
from datetime import datetime, timezone
from typing import Any, Dict
from packages.observability.correlation import get_correlation_id, get_request_id


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_object: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": get_correlation_id(),
            "request_id": get_request_id(),
            "module": record.module,
            "line": record.lineno,
        }

        if record.exc_info:
            log_object["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "extra_fields") and isinstance(record.extra_fields, dict):
            log_object.update(record.extra_fields)

        return json.dumps(log_object)


def setup_logger(name: str = "aegis", level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)

    return logger


logger = setup_logger()
