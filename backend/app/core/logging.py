"""
app/core/logging.py

Structured (JSON) logging for the Technify VisionAI backend.

Design goals:
- Zero extra runtime dependencies (pure stdlib `logging`) so it can't break
  in constrained/edge deployments.
- JSON-formatted logs in staging/production (easy to ship to ELK / Loki /
  CloudWatch / Supabase log drains), human-readable colored logs in local dev.
- Request-scoped context (request_id, organization_id, user_id, camera_id,
  event_id, ...) automatically attached to every log line via contextvars,
  without having to pass them explicitly at every call site.
- Safe to call `setup_logging()` multiple times (idempotent) — useful for
  tests and for workers/scripts that import app modules directly.
- Exposes `get_logger(__name__)` as the one function the rest of the
  codebase should use.

Usage
-----
    # In app/main.py, before anything else runs:
    from app.core.logging import setup_logging, get_logger
    setup_logging()
    logger = get_logger(__name__)
    logger.info("service_starting", extra={"port": 8000})

    # In a request middleware:
    from app.core.logging import request_id_ctx, org_id_ctx, user_id_ctx
    request_id_ctx.set(str(uuid.uuid4()))

    # Anywhere else in the codebase:
    from app.core.logging import get_logger
    logger = get_logger(__name__)
    logger.warning("camera_offline", extra={"camera_id": camera_id})
"""

from __future__ import annotations

import contextvars
import json
import logging
import logging.config
import sys
import traceback
from datetime import datetime, timezone
from typing import Any, Optional

from app.core.config import settings

# --------------------------------------------------------------------------
# Context variables — set per request / per background task, read by the
# formatter so every log line in that context is automatically tagged.
# --------------------------------------------------------------------------

request_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "request_id", default=None
)
organization_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "organization_id", default=None
)
user_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "user_id", default=None
)
camera_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "camera_id", default=None
)

_CONTEXT_VARS = {
    "request_id": request_id_ctx,
    "organization_id": organization_id_ctx,
    "user_id": user_id_ctx,
    "camera_id": camera_id_ctx,
}

# Standard LogRecord attributes — anything NOT in this set that shows up on
# a record (i.e. passed via `extra={...}`) is treated as custom structured
# data and folded into the JSON output.
_RESERVED_RECORD_ATTRS = {
    "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
    "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
    "created", "msecs", "relativeCreated", "thread", "threadName",
    "processName", "process", "message", "asctime", "taskName",
}


class ContextInjectingFilter(logging.Filter):
    """Attaches active contextvars (request_id, org_id, user_id, ...) to every record."""

    def filter(self, record: logging.LogRecord) -> bool:
        for key, var in _CONTEXT_VARS.items():
            value = var.get()
            if value is not None:
                setattr(record, key, value)
        return True


class JSONFormatter(logging.Formatter):
    """Renders each LogRecord as a single-line JSON object."""

    def __init__(self, service_name: str, environment: str) -> None:
        super().__init__()
        self.service_name = service_name
        self.environment = environment

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "service": self.service_name,
            "environment": self.environment,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        for key in _CONTEXT_VARS:
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value

        # Fold in any extra={...} fields the caller passed.
        for key, value in record.__dict__.items():
            if key not in _RESERVED_RECORD_ATTRS and key not in payload:
                try:
                    json.dumps(value)  # ensure it's serializable
                    payload[key] = value
                except (TypeError, ValueError):
                    payload[key] = repr(value)

        if record.exc_info:
            payload["exception"] = "".join(
                traceback.format_exception(*record.exc_info)
            )

        return json.dumps(payload, default=str)


class ConsoleFormatter(logging.Formatter):
    """Human-friendly formatter for local development."""

    COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[41m",
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, "")
        ts = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
        ctx_bits = []
        for key in _CONTEXT_VARS:
            value = getattr(record, key, None)
            if value:
                ctx_bits.append(f"{key}={value}")
        ctx_str = f" [{' '.join(ctx_bits)}]" if ctx_bits else ""
        base = (
            f"{color}{ts} {record.levelname:<8}{self.RESET} "
            f"{record.name}:{record.lineno}{ctx_str} - {record.getMessage()}"
        )
        if record.exc_info:
            base += "\n" + "".join(traceback.format_exception(*record.exc_info))
        return base


_configured = False


def setup_logging(force: bool = False) -> None:
    """
    Configure the root logger for the whole process.

    Idempotent — safe to call from app.main, from pytest fixtures, or from
    standalone scripts (scripts/seed_db.py, scripts/create_admin.py) without
    creating duplicate handlers.
    """
    global _configured
    if _configured and not force:
        return

    environment = getattr(settings, "ENVIRONMENT", "development")
    log_level = getattr(settings, "LOG_LEVEL", "INFO").upper()
    use_json = environment.lower() in {"production", "staging"}

    formatter: logging.Formatter
    if use_json:
        formatter = JSONFormatter(service_name="technify-visionai-backend", environment=environment)
    else:
        formatter = ConsoleFormatter()

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(ContextInjectingFilter())

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Quiet down noisy third-party loggers unless we're debugging.
    noisy_loggers = ["uvicorn.access", "httpx", "httpcore", "supabase", "postgrest", "gotrue"]
    for name in noisy_loggers:
        logging.getLogger(name).setLevel(
            logging.WARNING if log_level != "DEBUG" else logging.DEBUG
        )

    # Make uvicorn's own loggers use the same handler/formatter so log
    # output is consistent whether it comes from our code or from uvicorn.
    for uvicorn_logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uv_logger = logging.getLogger(uvicorn_logger_name)
        uv_logger.handlers.clear()
        uv_logger.propagate = True

    _configured = True

    logging.getLogger(__name__).info(
        "logging_configured",
        extra={"level": log_level, "format": "json" if use_json else "console"},
    )


def get_logger(name: str) -> logging.Logger:
    """Standard entrypoint the rest of the codebase should use."""
    if not _configured:
        setup_logging()
    return logging.getLogger(name)


def bind_request_context(
    *,
    request_id: Optional[str] = None,
    organization_id: Optional[str] = None,
    user_id: Optional[str] = None,
    camera_id: Optional[str] = None,
) -> None:
    """Convenience helper to set several context vars at once (e.g. in middleware)."""
    if request_id is not None:
        request_id_ctx.set(request_id)
    if organization_id is not None:
        organization_id_ctx.set(organization_id)
    if user_id is not None:
        user_id_ctx.set(user_id)
    if camera_id is not None:
        camera_id_ctx.set(camera_id)


def clear_request_context() -> None:
    """Reset context vars — call at the end of each request/task."""
    request_id_ctx.set(None)
    organization_id_ctx.set(None)
    user_id_ctx.set(None)
    camera_id_ctx.set(None)