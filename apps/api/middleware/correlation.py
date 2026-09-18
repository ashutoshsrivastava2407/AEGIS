"""Correlation & Request ID Tracking Middleware."""

import uuid
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from packages.observability.correlation import set_correlation_id, set_request_id


class CorrelationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        correlation_id = request.headers.get("x-correlation-id") or str(uuid.uuid4())
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())

        set_correlation_id(correlation_id)
        set_request_id(request_id)

        response = await call_next(request)
        response.headers["x-correlation-id"] = correlation_id
        response.headers["x-request-id"] = request_id

        return response
