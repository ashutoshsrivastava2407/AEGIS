"""Standardized AEGIS REST API Request/Response Schemas."""

from typing import Generic, TypeVar, Optional, List, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    status_code: int = 200
    message: str = "Operation executed successfully"
    data: Optional[T] = None
    correlation_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class ErrorDetail(BaseModel):
    code: str
    message: str
    target: Optional[str] = None
    details: Optional[Any] = None


class ErrorResponse(BaseModel):
    success: bool = False
    status_code: int
    error: ErrorDetail
    correlation_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
