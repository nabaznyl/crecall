#!/usr/bin/env python3
import importlib
import sys

required = [
    'opentelemetry',
    'opentelemetry.sdk',
    'opentelemetry.sdk.trace',
    'opentelemetry.sdk.resources',
    'opentelemetry.propagate',
    'opentelemetry.exporter.otlp',
]

optional = [
    'opentelemetry.instrumentation',
    'opentelemetry.instrumentation.fastapi',
    'opentelemetry.instrumentation.starlette',
    'opentelemetry.instrumentation.requests',
    'opentelemetry.instrumentation.sqlalchemy',
    'opentelemetry.instrumentation.httpx',
    'opentelemetry.exporter.jaeger',
    'opentelemetry.exporter.zipkin',
]

failed_required = []
failed_optional = []

print('Checking required OTEL modules...')
for m in required:
    try:
        importlib.import_module(m)
        print(f"import ok: {m}")
    except Exception as e:
        print(f"import failed: {m} -> {e}")
        failed_required.append((m, str(e)))

print('\nChecking optional OTEL modules (warnings only)...')
for m in optional:
    try:
        importlib.import_module(m)
        print(f"import ok: {m}")
    except Exception as e:
        print(f"optional import missing: {m} -> {e}")
        failed_optional.append((m, str(e)))

if failed_required:
    print('\nERROR: One or more required OTEL modules failed to import:')
    for m, e in failed_required:
        print(f" - {m}: {e}")
    sys.exit(1)

if failed_optional:
    print('\nWARNING: Some optional OTEL modules were not importable:')
    for m, e in failed_optional:
        print(f" - {m}: {e}")
    print('\nThis is a warning only; workflow will continue.')
else:
    print('\nAll OTEL imports OK')
