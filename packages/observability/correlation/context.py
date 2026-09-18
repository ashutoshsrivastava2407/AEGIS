"""Correlation ID and Request ID propagation context."""

import uuid
from contextvars import ContextVar
from typing import Optional

_correlation_id_ctx: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)
_request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def get_correlation_id() -> str:
    cid = _correlation_id_ctx.get()
    if not cid:
        cid = str(uuid.uuid4())
        _correlation_id_ctx.set(cid)
    return cid


def set_correlation_id(cid: str) -> None:
    _correlation_id_ctx.set(cid)


def get_request_id() -> str:
    rid = _request_id_ctx.get()
    if not rid:
        rid = str(uuid.uuid4())
        _request_id_ctx.set(rid)
    return rid


def set_request_id(rid: str) -> None:
    _request_id_ctx.set(rid)
