"""Benchmark harness for crecall API operations.

Run with an active server:
    python backend/scripts/benchmark.py --host http://localhost:8000 --iterations 50

Metrics reported:
- Session create latency
- Clip create latency
- Memory create latency
- Retention stats latency
- Aggregate averages and percentiles
"""
import argparse
import statistics
import time
import http.client
import json
import uuid
from urllib.parse import urlparse

ENDPOINTS = {
    "create_session": ("POST", "/api/sessions/"),
    "create_clip": ("POST", "/api/clips/"),
    "create_memory": ("POST", "/api/memories/"),
    "retention_stats": ("GET", "/api/clips/retention/stats"),
}


def request(host: str, method: str, path: str, payload=None):
    parsed = urlparse(host)
    host = parsed.hostname or "localhost"
    conn = http.client.HTTPConnection(host, parsed.port or 80, timeout=10)
    headers = {"Content-Type": "application/json"}
    body = json.dumps(payload).encode("utf-8") if payload else None
    start = time.perf_counter()
    conn.request(method, path, body=body, headers=headers)
    resp = conn.getresponse()
    data = resp.read()
    elapsed = (time.perf_counter() - start) * 1000.0
    conn.close()
    if resp.status >= 300:
        raise RuntimeError(f"{method} {path} failed: {resp.status} {data[:200]}")
    return elapsed, json.loads(data.decode("utf-8")) if data else None


def percentile(values, p):
    if not values:
        return 0.0
    idx = int(round(p/100 * (len(values)-1)))
    return sorted(values)[idx]


def main():
    parser = argparse.ArgumentParser(description="Benchmark core API operations")
    parser.add_argument("--host", required=True, help="Base host, e.g. http://localhost:8000")
    parser.add_argument("--iterations", type=int, default=20)
    args = parser.parse_args()

    timings = {k: [] for k in ENDPOINTS.keys()}

    # Prime session for memory/clip creation
    for i in range(args.iterations):
        # Create session
        sess_payload = {"session_id": f"bench-{uuid.uuid4().hex[:8]}", "status": "active"}
        t, sess = request(args.host, *ENDPOINTS["create_session"], payload=sess_payload)
        timings["create_session"].append(t)
        session_db_id = sess.get("id") if isinstance(sess, dict) else None

        # Create clip
        clip_payload = {"session_id": session_db_id, "content": {"type": "benchmark", "i": i}, "profile": "minimal"}
        t, _ = request(args.host, *ENDPOINTS["create_clip"], payload=clip_payload)
        timings["create_clip"].append(t)

        # Create memory
        mem_payload = {"session_id": session_db_id, "content": f"Benchmark memory {i}", "tags": ["bench"], "importance": 0}
        t, _ = request(args.host, *ENDPOINTS["create_memory"], payload=mem_payload)
        timings["create_memory"].append(t)

        # Retention stats
        t, _ = request(args.host, *ENDPOINTS["retention_stats"])
        timings["retention_stats"].append(t)

    print("Benchmark Results (ms):")
    for name, values in timings.items():
        avg = statistics.mean(values)
        p95 = percentile(values, 95)
        p99 = percentile(values, 99)
        print(f"  {name:16} avg={avg:7.2f} p95={p95:7.2f} p99={p99:7.2f} n={len(values)}")

if __name__ == "__main__":
    main()
