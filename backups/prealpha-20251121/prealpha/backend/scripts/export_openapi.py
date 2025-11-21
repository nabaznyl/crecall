"""Export the live OpenAPI schema to a versioned file.

Usage:
    python backend/scripts/export_openapi.py --out backend/openapi.json --host http://localhost:8000

Starts a temporary client request against a running server (recommended) or falls back
 to direct FastAPI import (may omit dynamic routes registered at runtime).
"""
import argparse
import json
import sys
from pathlib import Path
import http.client
from urllib.parse import urlparse


def fetch_from_server(host: str) -> dict:
    parsed = urlparse(host)
    if not parsed.scheme:
        raise ValueError("Host must include scheme, e.g. http://localhost:8000")
    host = parsed.hostname or "localhost"
    conn = http.client.HTTPConnection(host, parsed.port or 80, timeout=5)
    try:
        conn.request("GET", "/openapi.json")
        resp = conn.getresponse()
        if resp.status != 200:
            raise RuntimeError(f"Unexpected status {resp.status}")
        data = resp.read()
        return json.loads(data.decode("utf-8"))
    finally:
        conn.close()


def fetch_direct() -> dict:
    try:
        # Add backend directory to path for direct import
        import sys
        from pathlib import Path
        backend_dir = Path(__file__).parent.parent
        if str(backend_dir) not in sys.path:
            sys.path.insert(0, str(backend_dir))
        from app.main import app  # type: ignore
        return app.openapi()
    except Exception as e:
        raise RuntimeError(f"Direct import failed: {e}")


def main():
    parser = argparse.ArgumentParser(description="Export OpenAPI schema")
    parser.add_argument("--out", default="backend/openapi.json", help="Output file path")
    parser.add_argument("--host", default="", help="Host of running server (optional)")
    args = parser.parse_args()

    if args.host:
        try:
            schema = fetch_from_server(args.host)
        except Exception as e:
            print(f"Server fetch failed ({e}), attempting direct import...")
            schema = fetch_direct()
    else:
        schema = fetch_direct()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(schema, indent=2))
    print(f"OpenAPI schema written to {out_path}")

if __name__ == "__main__":
    main()
