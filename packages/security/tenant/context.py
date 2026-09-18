"""Tenant isolation context manager."""

from contextvars import ContextVar
from typing import Optional
from packages.config import settings

_tenant_id_ctx: ContextVar[Optional[str]] = ContextVar("tenant_id", default=None)


def get_current_tenant_id() -> str:
    tid = _tenant_id_ctx.get()
    if not tid:
        return settings.DEFAULT_TENANT_ID
    return tid


def set_current_tenant_id(tenant_id: str) -> None:
    _tenant_id_ctx.set(tenant_id)
