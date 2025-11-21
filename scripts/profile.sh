#!/usr/bin/env bash
# Performance Profiling Script for crecall
# Measures critical path performance and generates reports

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PROFILE_DIR="$PROJECT_ROOT/profiles"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

mkdir -p "$PROFILE_DIR"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   crecall Performance Profiling${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# ============================================================================
# API Endpoint Benchmarks
# ============================================================================
echo -e "\n${YELLOW}Benchmarking API endpoints...${NC}"

if command -v ab &> /dev/null; then
    # Start backend if not running
    if ! curl -s http://localhost:8000/ > /dev/null 2>&1; then
        echo -e "${YELLOW}Starting backend...${NC}"
        cd "$PROJECT_ROOT/backend"
        uvicorn app.main:app --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &
        BACKEND_PID=$!
        sleep 3
    fi

    # Benchmark root endpoint
    echo -e "\n${BLUE}GET /${NC}"
    ab -n 1000 -c 10 http://localhost:8000/ > "$PROFILE_DIR/bench_root.txt" 2>&1
    grep "Requests per second" "$PROFILE_DIR/bench_root.txt"
    grep "Time per request" "$PROFILE_DIR/bench_root.txt" | head -1

    # Benchmark sessions list
    echo -e "\n${BLUE}GET /api/sessions/${NC}"
    ab -n 500 -c 10 http://localhost:8000/api/sessions/ > "$PROFILE_DIR/bench_sessions.txt" 2>&1
    grep "Requests per second" "$PROFILE_DIR/bench_sessions.txt"
    grep "Time per request" "$PROFILE_DIR/bench_sessions.txt" | head -1

    # Stop backend if we started it
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi

    echo -e "${GREEN}✓ API benchmarks complete${NC}"
else
    echo -e "${YELLOW}! Apache Bench (ab) not installed. Install with: apt install apache2-utils${NC}"
fi

# ============================================================================
# Python Code Profiling
# ============================================================================
echo -e "\n${YELLOW}Profiling Python code...${NC}"

cd "$PROJECT_ROOT/backend"

# Create profiling test script
cat > "$PROFILE_DIR/profile_test.py" << 'EOF'
import cProfile
import pstats
from io import StringIO
from app.db.session import SessionLocal
from app.db.models import Session, Clip, Memory

def profile_database_queries():
    """Profile database query performance"""
    db = SessionLocal()
    
    # Create test data
    for i in range(100):
        session = Session(session_id=f"prof-test-{i}", status="active")
        db.add(session)
    db.commit()
    
    # Query sessions
    sessions = db.query(Session).all()
    
    # Query with filter
    active_sessions = db.query(Session).filter(Session.status == "active").all()
    
    db.close()

if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    
    profile_database_queries()
    
    profiler.disable()
    
    # Generate stats
    s = StringIO()
    stats = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    stats.print_stats(20)
    
    print(s.getvalue())
EOF

if command -v python3 &> /dev/null; then
    python3 "$PROFILE_DIR/profile_test.py" > "$PROFILE_DIR/python_profile.txt" 2>&1 || true
    echo -e "${GREEN}✓ Python profiling complete${NC}"
    echo "Top 10 time-consuming functions:"
    head -20 "$PROFILE_DIR/python_profile.txt" | tail -10
else
    echo -e "${YELLOW}! Python3 not available${NC}"
fi

# ============================================================================
# Memory Usage Analysis
# ============================================================================
echo -e "\n${YELLOW}Analyzing memory usage...${NC}"

cat > "$PROFILE_DIR/memory_profile.py" << 'EOF'
import tracemalloc
import sys

def analyze_memory():
    """Analyze memory usage of core components"""
    tracemalloc.start()
    
    # Import heavy modules
    from app.db.models import Base, Session, Clip, Memory
    from app.api import clips, memories, sessions
    
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    
    print("[ Top 10 memory consumers ]")
    for stat in top_stats[:10]:
        print(f"{stat.size / 1024:.1f} KB - {stat.traceback}")
    
    tracemalloc.stop()

if __name__ == "__main__":
    analyze_memory()
EOF

python3 "$PROFILE_DIR/memory_profile.py" > "$PROFILE_DIR/memory_usage.txt" 2>&1 || true
echo -e "${GREEN}✓ Memory analysis complete${NC}"

# ============================================================================
# Database Query Analysis
# ============================================================================
echo -e "\n${YELLOW}Analyzing database queries...${NC}"

if [ -f "$PROJECT_ROOT/.recall_memory/crecall.db" ]; then
    # Check database size
    DB_SIZE=$(du -h "$PROJECT_ROOT/.recall_memory/crecall.db" | cut -f1)
    echo -e "Database size: ${BLUE}$DB_SIZE${NC}"
    
    # Count records
    sqlite3 "$PROJECT_ROOT/.recall_memory/crecall.db" << EOF > "$PROFILE_DIR/db_stats.txt"
SELECT 'Sessions: ' || COUNT(*) FROM sessions;
SELECT 'Clips: ' || COUNT(*) FROM clips;
SELECT 'Memories: ' || COUNT(*) FROM memories;
.exit
EOF
    cat "$PROFILE_DIR/db_stats.txt"
else
    echo -e "${YELLOW}! No database found${NC}"
fi

# ============================================================================
# Frontend Build Analysis
# ============================================================================
echo -e "\n${YELLOW}Analyzing frontend build...${NC}"

cd "$PROJECT_ROOT/frontend"
if [ -f "package.json" ]; then
    # Measure build time
    echo "Building frontend..."
    START_TIME=$(date +%s)
    npm run build > "$PROFILE_DIR/frontend_build.log" 2>&1 || true
    END_TIME=$(date +%s)
    BUILD_TIME=$((END_TIME - START_TIME))
    
    echo -e "Build time: ${BLUE}${BUILD_TIME}s${NC}"
    
    # Analyze bundle size
    if [ -d "dist" ]; then
        BUNDLE_SIZE=$(du -sh dist | cut -f1)
        echo -e "Bundle size: ${BLUE}$BUNDLE_SIZE${NC}"
        
        echo -e "\nLargest files in bundle:"
        find dist -type f -exec du -h {} + | sort -rh | head -10
    fi
fi

# ============================================================================
# Summary Report
# ============================================================================
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Profiling complete!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "\nProfile reports saved to: ${YELLOW}$PROFILE_DIR/${NC}"
ls -lh "$PROFILE_DIR/"

echo -e "\n${YELLOW}Recommendations:${NC}"
echo "  1. Review API benchmark results in bench_*.txt"
echo "  2. Check Python profiling for slow functions in python_profile.txt"
echo "  3. Analyze memory usage in memory_usage.txt"
echo "  4. Optimize database queries based on db_stats.txt"
echo "  5. Consider code splitting for large frontend bundles"

# ============================================================================
# Optimization Suggestions
# ============================================================================
echo -e "\n${YELLOW}Performance Optimization Checklist:${NC}"
echo "  [ ] Add database indexes on frequently queried fields"
echo "  [ ] Implement query result caching (Redis)"
echo "  [ ] Use connection pooling for database"
echo "  [ ] Optimize ORM queries (use select_related, joins)"
echo "  [ ] Add pagination for large result sets"
echo "  [ ] Implement lazy loading for frontend components"
echo "  [ ] Use CDN for static assets"
echo "  [ ] Enable gzip/brotli compression"
echo "  [ ] Implement API response caching"
echo "  [ ] Use async/await for I/O operations"
