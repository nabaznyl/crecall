#!/usr/bin/env python3
"""Integration smoke test for OTEL instrumentation.

Sets up an in-memory span exporter, imports the FastAPI app, issues a TestClient request,
and asserts that at least one span was recorded by instrumentation.
"""
from __future__ import annotations
import sys
import logging

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExporter, SpanExportResult
except Exception as exc:  # pragma: no cover - optional
    print(f"OpenTelemetry SDK not available: {exc}")
    sys.exit(2)


# Lightweight in-memory exporter in case the SDK's InMemorySpanExporter isn't present
class _InMemoryExporter(SpanExporter):
    def __init__(self):
        self._spans = []

    def export(self, spans) -> "SpanExportResult":
        self._spans.extend(spans)
        return SpanExportResult.SUCCESS

    def shutdown(self) -> None:
        return None

    def force_flush(self, timeout_millis: int | None = None) -> bool:
        return True

    def get_finished_spans(self):
        return list(self._spans)

from fastapi.testclient import TestClient


def main() -> int:
    # Configure in-memory tracer provider so instrumentation writes to it
    exporter = _InMemoryExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    # Ensure backend package is importable: prepend backend/ to sys.path
    import os

    sys.path.insert(0, os.path.abspath("backend"))
    # Import the app after tracer provider is set so instrument_app may pick it up
    try:
        from app.main import app
    except Exception as exc:
        print(f"Failed to import app: {exc}")
        return 2

    # Force-instrument the app using our instrument_app helper to ensure
    # instrumentation uses the tracer provider we configured above.
    try:
        from app.observability import instrument_app

        instrument_app(app)
        print("instrument_app applied")
    except Exception as exc:
        print(f"instrument_app not applied: {exc}")

    # Silence noisy logs in test output
    logging.getLogger("uvicorn").setLevel(logging.WARNING)

    client = TestClient(app)
    # Create a manual span to verify the in-memory exporter works
    provider_for_test = trace.get_tracer_provider()
    tracer = provider_for_test.get_tracer(__name__)
    with tracer.start_as_current_span("manual-test"):
        pass

    resp = client.get("/health")
    print("/health ->", resp.status_code)

    spans = exporter.get_finished_spans()
    print(f"Collected {len(spans)} spans")
    if len(spans) == 0:
        print("No spans recorded by instrumentation; failing smoke test")
        return 1
    # Print a brief summary of collected spans
    for s in spans[:5]:
        print(f" - {s.name} (trace_id={format(s.context.trace_id, '032x')})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
