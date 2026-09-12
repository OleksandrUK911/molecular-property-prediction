"""Structured (JSON) logging setup, isolated from FastAPI so it can be
unit-tested / reused independently, per backend/TODO_logging_observability.md."""

import json
import logging
import sys
import time
from collections.abc import Awaitable, Callable

from starlette.requests import Request
from starlette.responses import Response


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra_fields"):
            payload.update(record.extra_fields)
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def configure_logging() -> logging.Logger:
    logger = logging.getLogger("backend")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    logger.handlers = [handler]
    logger.propagate = False
    return logger


request_logger = configure_logging()


def log_with_fields(level: int, message: str, **fields) -> None:
    request_logger.log(level, message, extra={"extra_fields": fields})


async def log_requests_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    """Logs method/path/status/latency for every request. Deliberately
    omits the request body (SMILES) here - it's logged separately per
    prediction in inference call sites, so volume/PII concerns are
    isolated to one place (see backend/TODO_logging_observability.md's
    note on privacy)."""
    start = time.perf_counter()
    response = await call_next(request)
    latency_ms = round((time.perf_counter() - start) * 1000, 1)
    log_with_fields(
        logging.INFO,
        "request",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        latency_ms=latency_ms,
    )
    return response
