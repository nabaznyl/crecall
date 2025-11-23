"""OpenTelemetry tracing bootstrap for crecall backend.

This module initializes OTLP exporter when `OTEL_EXPORTER_OTLP_ENDPOINT` is set.
It's safe to import even when OpenTelemetry packages are not installed (no-op).
"""
from __future__ import annotations
import os
import logging

logger = logging.getLogger(__name__)

def init_tracing(service_name: str = "crecall-backend") -> None:
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

        endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
        if not endpoint:
            logger.debug("OTEL_EXPORTER_OTLP_ENDPOINT not set; tracing disabled")
            return

        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)
        span_exporter = OTLPSpanExporter(endpoint=endpoint)
        processor = BatchSpanProcessor(span_exporter)
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        # expose provider for optional instrumentation helpers
        global _tracer_provider
        _tracer_provider = provider
        logger.info("OpenTelemetry tracing initialized", extra={"otel_endpoint": endpoint})
    except Exception as exc:  # pragma: no cover - best-effort
        logger.warning(f"OpenTelemetry not initialized: {exc}")


def instrument_app(app) -> None:
    """Attempt to instrument a FastAPI application with OpenTelemetry instrumentors.

    This is best-effort and will not raise if instrumentations are not installed.
    """
    try:
        # Avoid double-instrumentation: FastAPIInstrumentor logs a warning but
        # we can short-circuit earlier by setting a flag on the app object.
        if getattr(app, "_otel_instrumented", False):
            logger.debug("App already instrumented for OTEL; skipping")
            return
        # FastAPI instrumentor (may be installed with requirements-otel.txt)
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        # Attempt to instrument SQLAlchemy if available
        try:
            from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        except Exception:
            SQLAlchemyInstrumentor = None

        # If a tracer provider was set during init_tracing, prefer using it.
        try:
            provider = globals().get("_tracer_provider")
            if provider is not None:
                FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
            else:
                FastAPIInstrumentor.instrument_app(app)
            # mark the app so future calls are a no-op
            try:
                setattr(app, "_otel_instrumented", True)
            except Exception:
                pass
            logger.info("FastAPI instrumented for OpenTelemetry")
        except TypeError:
            FastAPIInstrumentor.instrument_app(app)
            try:
                setattr(app, "_otel_instrumented", True)
            except Exception:
                pass
            logger.info("FastAPI instrumented for OpenTelemetry (fallback)")

        # Instrument SQLAlchemy if available (best-effort)
        try:
            if SQLAlchemyInstrumentor is not None:
                SQLAlchemyInstrumentor().instrument()
                logger.info("SQLAlchemy instrumentation applied")
        except Exception as exc:  # pragma: no cover - optional
            logger.debug(f"SQLAlchemy instrumentation not applied: {exc}")
    except Exception as exc:  # pragma: no cover - optional
        logger.debug(f"FastAPI instrumentation not applied: {exc}")
