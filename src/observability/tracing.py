from __future__ import annotations

from fastapi import FastAPI
from sqlalchemy.engine import Engine

from src.observability.logging import get_logger

logger = get_logger(__name__)


def configure_tracing(service_name: str, endpoint: str | None, app: FastAPI | None = None,
                      engine: Engine | None = None) -> None:
    if not endpoint:
        return

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError:
        logger.warning(
            "Tracing endpoint configured, but OpenTelemetry packages are not installed",
        )
        return

    tracer_provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
    trace.set_tracer_provider(tracer_provider)

    if app is not None:
        FastAPIInstrumentor.instrument_app(app)
    if engine is not None:
        SQLAlchemyInstrumentor().instrument(engine=engine)
