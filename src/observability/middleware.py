from __future__ import annotations

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from src.observability.context import request_id_var, trace_id_var
from src.observability.logging import get_logger
from src.observability.metrics import record_http_request, registry

logger = get_logger(__name__)


def _extract_trace_id(request: Request) -> str:
    traceparent = request.headers.get("traceparent")
    if traceparent:
        parts = traceparent.split("-")
        if len(parts) >= 4 and parts[1]:
            return parts[1]
    return uuid.uuid4().hex


class ObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        started_at = time.perf_counter()
        current_request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        current_trace_id = _extract_trace_id(request)

        request_id_token = request_id_var.set(current_request_id)
        trace_id_token = trace_id_var.set(current_trace_id)

        registry.increment_gauge("http_requests_in_flight", 1)
        response = None

        try:
            response = await call_next(request)
            return response
        except Exception:
            duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
            logger.exception(
                "Unhandled request exception",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": 500,
                    "duration_ms": duration_ms,
                    "client_ip": request.client.host if request.client else "-",
                },
            )
            record_http_request(request.method, request.url.path, 500, duration_ms / 1000)
            raise
        finally:
            registry.increment_gauge("http_requests_in_flight", -1)

            if response is not None:
                duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
                route = request.scope.get("route")
                route_path = getattr(route, "path", request.url.path)
                response.headers["X-Request-ID"] = current_request_id
                response.headers["X-Trace-ID"] = current_trace_id

                logger.info(
                    "Request completed",
                    extra={
                        "method": request.method,
                        "path": route_path,
                        "status_code": response.status_code,
                        "duration_ms": duration_ms,
                        "client_ip": request.client.host if request.client else "-",
                    },
                )
                record_http_request(request.method, route_path, response.status_code, duration_ms / 1000)

            request_id_var.reset(request_id_token)
            trace_id_var.reset(trace_id_token)
