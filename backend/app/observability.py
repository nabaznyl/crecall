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
        logger.info("OpenTelemetry tracing initialized", extra={"otel_endpoint": endpoint})
    except Exception as exc:  # pragma: no cover - best-effort
        logger.warning(f"OpenTelemetry not initialized: {exc}")
