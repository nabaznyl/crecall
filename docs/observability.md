# Observability & OTEL — Quick HOWTO

This page documents the OpenTelemetry (OTEL) smoke tests and helper scripts used by CI to validate instrumentation and how to run them locally.

Files of interest

- `.github/scripts/otel_smoke.py` — lightweight import-check (required vs optional OTEL modules).
- `.github/scripts/otel_integration_smoke.py` — integration smoke test using an in-memory exporter and `TestClient` to assert spans are produced.
- `backend/requirements-otel.txt` — pinned OTEL packages used by CI import-check and recommended for local validation.
- `./.automation/ci_fetch_artifacts.sh` — helper script to dispatch the `otel-smoke` workflow, poll for completion, download artifacts, and produce a small report. Requires `GITHUB_TOKEN`.

Run import-check locally

1. Create and activate a venv, then install the OTEL pins:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements-otel.txt
python .github/scripts/otel_smoke.py
```

- The script exits non-zero if required OTEL modules are missing.
- Optional instrumentations (FastAPI, SQLAlchemy, requests, httpx, etc.) are reported as warnings only.

Run integration smoke locally

1. Ensure `backend` is importable (run from repo root) and install runtime dependencies used by your app (FastAPI, Starlette, etc.).
2. Run the integration script:

```bash
# from repo root, inside activated venv with app deps installed
python .github/scripts/otel_integration_smoke.py
```

- The integration script configures an in-memory tracer provider and tries to import `backend/app/main.py` (the FastAPI app). It applies `instrument_app(app)` helper and uses `TestClient` to hit `/health`. It fails if no spans are collected.

Fetch CI artifacts (automation)

- The helper `./.automation/ci_fetch_artifacts.sh` will dispatch the `otel-smoke` workflow for the `chore/otel-smoke-split` branch, poll for the run to complete, download artifacts into `ci-artifacts/<run-id>/`, and print concise summaries of the import and integration reports.
- Usage requires a GitHub token with repository access set in environment variable `GITHUB_TOKEN`:

```bash
export GITHUB_TOKEN="ghp_..."  # use token with repo/workflow access for private repos
bash ./.automation/ci_fetch_artifacts.sh
```

Notes and recommendations

- Keep the import-check job fast and lightweight; this helps detect package incompatibilities early.
- The integration job should only install the runtime deps needed for instrumentation verification to avoid inflating matrix durations.
- The integration job posts a short preview comment to PRs using the workflow's `GITHUB_TOKEN`, reducing the need to provide external PATs for routine checks.

If you want help applying these docs to other pages or expanding troubleshooting steps, tell me which areas to expand.