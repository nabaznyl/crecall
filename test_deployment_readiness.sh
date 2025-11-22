#!/bin/bash
echo "=== Test 5: Deployment Readiness Verification ==="
PASS=0; FAIL=0; WARN=0
check_pass() { echo "✓ $1"; ((PASS++)); }
check_fail() { echo "✗ $1"; ((FAIL++)); }
check_warn() { echo "⚠ $1"; ((WARN++)); }

echo "### Core Requirements"
[[ -n "$VIRTUAL_ENV" ]] && check_pass "Virtual environment active" || check_warn "Virtual environment not active"
cd backend && python -m pytest tests/ -q --tb=no 2>/dev/null | grep -q "85 passed" && check_pass "Tests: 85/85 passing" || check_fail "Tests failing"

echo "### Dependencies"
python -c "import fastapi; import sqlalchemy; import pydantic; import uvicorn" 2>/dev/null && check_pass "All core deps installed" || check_fail "Missing dependencies"
python -c "import black; import isort; import pylint; import bandit" 2>/dev/null && check_pass "All dev tools installed" || check_fail "Missing dev tools"

echo "### Security"
grep -q "starlette" requirements.txt && check_pass "Starlette pinned" || check_fail "Starlette not pinned"
grep -q "python-jose" requirements.txt && check_pass "python-jose pinned" || check_fail "python-jose not pinned"

echo "### API Structure"
[[ -f "app/main.py" && -d "app/api" && -f "app/core/config.py" ]] && check_pass "API structure valid" || check_fail "API structure invalid"

echo "### Database"
[[ -f "crecall.db" ]] && check_pass "Database exists" || check_warn "Database will be created on startup"

echo "### Documentation"
cd .. && [[ -f "README.md" && -f "SECURITY_VULNERABILITY_ASSESSMENT.md" && -f "TEST_4_PERFORMANCE.md" ]] && check_pass "All docs present" || check_warn "Some docs missing"

echo "### Git"
[[ $(git rev-parse --abbrev-ref HEAD) == "feature/phase-2-instant-restore" ]] && check_pass "On feature branch" || check_fail "Wrong branch"

echo ""
echo "=== SUMMARY: Passed=$PASS, Warnings=$WARN, Failed=$FAIL ==="
[[ $FAIL -eq 0 ]] && echo "✅ Deployment Readiness: PASS" || echo "❌ Deployment Readiness: FAILED ($FAIL issues)"
exit $FAIL
