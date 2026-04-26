from __future__ import annotations

import threading
import time
from collections import defaultdict
from typing import Any

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from sqlalchemy import event
from sqlalchemy.engine import Engine

HTTP_DURATION_BUCKETS = (
    0.005,
    0.01,
    0.025,
    0.05,
    0.1,
    0.25,
    0.5,
    1.0,
    2.5,
    5.0,
    10.0,
)

DB_DURATION_BUCKETS = (
    0.001,
    0.005,
    0.01,
    0.025,
    0.05,
    0.1,
    0.25,
    0.5,
    1.0,
    2.5,
    5.0,
)


class MetricsRegistry:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counters: dict[tuple[str, tuple[tuple[str, str], ...]], float] = defaultdict(float)
        self._gauges: dict[tuple[str, tuple[tuple[str, str], ...]], float] = defaultdict(float)
        self._histograms: dict[
            tuple[str, tuple[tuple[str, str], ...]], dict[str, Any]
        ] = {}

    @staticmethod
    def _normalize_labels(labels: dict[str, Any] | None = None) -> tuple[tuple[str, str], ...]:
        if not labels:
            return ()
        return tuple(sorted((key, str(value)) for key, value in labels.items()))

    def set_gauge(self, name: str, value: float, labels: dict[str, Any] | None = None) -> None:
        key = (name, self._normalize_labels(labels))
        with self._lock:
            self._gauges[key] = value

    def increment_counter(
            self,
            name: str,
            value: float = 1.0,
            labels: dict[str, Any] | None = None,
    ) -> None:
        key = (name, self._normalize_labels(labels))
        with self._lock:
            self._counters[key] += value

    def increment_gauge(
            self,
            name: str,
            value: float,
            labels: dict[str, Any] | None = None,
    ) -> None:
        key = (name, self._normalize_labels(labels))
        with self._lock:
            self._gauges[key] += value

    def observe_histogram(
            self,
            name: str,
            value: float,
            buckets: tuple[float, ...],
            labels: dict[str, Any] | None = None,
    ) -> None:
        key = (name, self._normalize_labels(labels))
        with self._lock:
            histogram = self._histograms.setdefault(
                key,
                {
                    "buckets": buckets,
                    "counts": [0 for _ in buckets],
                    "sum": 0.0,
                    "count": 0,
                },
            )
            for index, bucket in enumerate(histogram["buckets"]):
                if value <= bucket:
                    histogram["counts"][index] += 1
            histogram["sum"] += value
            histogram["count"] += 1

    @staticmethod
    def _format_labels(labels: tuple[tuple[str, str], ...], extra: dict[str, str] | None = None) -> str:
        all_labels = list(labels)
        if extra:
            all_labels.extend(sorted(extra.items()))
        if not all_labels:
            return ""
        rendered = ",".join(f'{key}="{value}"' for key, value in all_labels)
        return f"{{{rendered}}}"

    def render(self) -> str:
        lines = [
            "# HELP app_info Static application metadata.",
            "# TYPE app_info gauge",
        ]

        with self._lock:
            for (name, labels), value in sorted(self._gauges.items()):
                lines.append(f"{name}{self._format_labels(labels)} {value}")

            for (name, labels), value in sorted(self._counters.items()):
                lines.append(f"{name}_total{self._format_labels(labels)} {value}")

            for (name, labels), histogram in sorted(self._histograms.items()):
                for bucket, count in zip(histogram["buckets"], histogram["counts"], strict=True):
                    lines.append(
                        f'{name}_bucket{self._format_labels(labels, {"le": str(bucket)})} {count}'
                    )
                lines.append(f'{name}_bucket{self._format_labels(labels, {"le": "+Inf"})} {histogram["count"]}')
                lines.append(f"{name}_sum{self._format_labels(labels)} {histogram['sum']}")
                lines.append(f"{name}_count{self._format_labels(labels)} {histogram['count']}")

        return "\n".join(lines) + "\n"


registry = MetricsRegistry()
registry.set_gauge("app_info", 1, labels={"service": "todo-api"})
registry.set_gauge("app_start_time_seconds", time.time())

metrics_router = APIRouter(include_in_schema=False)


@metrics_router.get("/metrics", response_class=PlainTextResponse)
async def metrics() -> PlainTextResponse:
    return PlainTextResponse(registry.render(), media_type="text/plain; version=0.0.4; charset=utf-8")


def record_http_request(method: str, path: str, status_code: int, duration_seconds: float) -> None:
    labels = {"method": method, "path": path, "status_code": status_code}
    registry.increment_counter("http_requests", labels=labels)
    registry.observe_histogram("http_request_duration_seconds", duration_seconds, HTTP_DURATION_BUCKETS, labels=labels)


def _statement_name(statement: str) -> str:
    token = statement.strip().split(maxsplit=1)
    if not token:
        return "UNKNOWN"
    return token[0].upper()


def setup_database_metrics(engine: Engine) -> None:
    if getattr(engine, "_observability_metrics_registered", False):
        return

    @event.listens_for(engine, "before_cursor_execute")
    def before_cursor_execute(
            conn, cursor, statement, parameters, context, executemany
    ) -> None:
        conn.info.setdefault("query_start_time", []).append(time.perf_counter())
        registry.increment_gauge("db_connections_in_use", 1)

    @event.listens_for(engine, "after_cursor_execute")
    def after_cursor_execute(
            conn, cursor, statement, parameters, context, executemany
    ) -> None:
        start_time = conn.info["query_start_time"].pop()
        registry.increment_gauge("db_connections_in_use", -1)
        duration = time.perf_counter() - start_time
        statement_type = _statement_name(statement)
        labels = {"statement": statement_type}
        registry.increment_counter("db_queries", labels=labels)
        registry.observe_histogram("db_query_duration_seconds", duration, DB_DURATION_BUCKETS, labels=labels)

    @event.listens_for(engine, "handle_error")
    def handle_error(exception_context) -> None:
        registry.increment_counter("db_query_errors")
        registry.increment_gauge("db_connections_in_use", -1)

    engine._observability_metrics_registered = True
