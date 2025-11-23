# Project TODO & Technical Debt

> **For AI Context:** This file tracks deferred implementation tasks, technical debt, and known issues in the crecall project. Use this to understand what features are incomplete, why certain tests are skipped, and what needs attention before production deployment.

## Security & Integrity

### ⏭️ Implement Clip Integrity Verification on Retrieval
**Status:** Not Implemented (Test Skipped)  
**Priority:** Medium-High (Security Feature)  
**Location:** `backend/app/services/clips.py` or clip retrieval endpoint  
**Test:** `backend/tests/test_api_clips_async.py::test_integrity_flag` (currently marked with `@pytest.mark.skip`)

**Context:**
Clips store workspace state snapshots (clipboard, open files, etc.) and use HMAC signatures to detect tampering. The signing happens during clip creation, but verification is missing during retrieval.

**Description:**
Currently, clips are signed with HMAC integrity signatures when created, but these signatures are **not verified** when clips are retrieved. This means tampered data would be returned without detection.

**Implementation Needed:**
1. When retrieving a clip via GET `/api/clips/{clip_id}`:
   - Extract stored signature from `content["integrity"]`
   - Recalculate expected signature using `app/services/integrity.py::verify_dict()`
   - Compare signatures
   - If mismatch: inject `"integrity_status": "invalid"` into response content
   - If match: return content as-is (remove integrity field or leave it)

**Related Files:**
- `backend/app/services/integrity.py` - HMAC signing/verification utilities (`sign_dict`, `verify_dict`)
- `backend/app/routers/clips.py` - Clip retrieval endpoint (GET route handler)
- `backend/app/services/clips.py` - Clip service layer (business logic)
- `backend/app/db/models.py` - Clip model with JSONB content field
- `backend/tests/test_api_clips_async.py` - Test expecting this behavior (lines 228-259)

**Test Expectations:**
The test creates a clip, manually corrupts the integrity signature in the database, then expects the GET endpoint to return `content.integrity_status == "invalid"`.

**When to Implement:**
Before production deployment or when security hardening is prioritized. This is a defense-in-depth measure against database tampering or SQL injection attacks.

---

## Code Quality

### ⚠️ Fix pytest return value warnings
**Status:** Warning (Non-blocking)  
**Priority:** Low  
**Files:** `backend/tests/test_api_sessions.py`

**Context:**
Some test functions return `False` instead of returning nothing (`None`). This is deprecated behavior in pytest and will become an error in future versions.

**Description:**
Six tests in `test_api_sessions.py` return `False` instead of `None`. Future pytest versions will treat this as an error.

**Affected Tests:**
- `test_list_sessions` (line ~56)
- `test_get_session` (line ~68)
- `test_update_session` (line ~80)
- `test_branch_status` (line ~92)
- `test_rate_limit_admin` (line ~104)
- `test_delete_session` (line ~116)

**Fix:** 
Remove `return False` statements entirely. These appear to be old debugging code or copy-paste errors. Tests should use `assert` statements for validation, not return values.

**Example:**
```python
# BAD (current)
def test_list_sessions(client):
    # ... test code ...
    return False  # ❌ Remove this

# GOOD (fixed)
def test_list_sessions(client):
    # ... test code ...
    # Just end the function, no return needed
```

---

## Configuration

### 📝 Migrate Ruff Configuration to New Format
**Status:** Deprecated Warning  
**Priority:** Low  
**File:** `backend/pyproject.toml`

**Context:**
Ruff v0.9.2 introduced a new configuration structure. The old top-level `[tool.ruff]` settings for linter rules are deprecated in favor of a nested `[tool.ruff.lint]` section.

**Description:**
Ruff shows deprecation warning about top-level linter settings during every run:
```
warning: The top-level linter settings are deprecated in favour of their counterparts in the `lint` section.
Please update the following options in `pyproject.toml`:
  - 'ignore' -> 'lint.ignore'
  - 'select' -> 'lint.select'
```

**Current (Deprecated):**
```toml
[tool.ruff]
line-length = 100
target-version = "py311"
select = ["E", "F", "I", "N", "W", "UP"]
ignore = ["E203", "W503"]
```

**Should Be (New Format):**
```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]
ignore = ["E203", "W503"]
```

**Impact:**
No functional change, just removes the deprecation warning. Future Ruff versions may remove support for the old format entirely.

---

## CI/CD

### ✅ Workflows Consolidated (2025-11-22)
**Context:**
The project originally had three separate GitHub Actions workflows that were causing maintenance overhead and occasional failures due to version mismatches and complexity.

**What Changed:**
Replaced three separate workflows with single unified `ci.yml`:
- ❌ Removed: `code-quality.yml` (Black + Ruff checks)
- ❌ Removed: `security-checks.yml` (Bandit security scanning)
- ❌ Removed: `test-and-coverage.yml` (pytest test suite)
- ✅ Added: `.github/workflows/ci.yml` (all checks in one job)

**New Workflow Structure:**
```yaml
jobs:
  quality:
    - Install dependencies (Black 25.11.0, Ruff 0.9.2, test requirements)
    - Run Black formatting check
    - Run Ruff linting
    - Run pytest test suite
```

**Benefits:**
- Single workflow to maintain
- Faster feedback (no separate job scheduling)
- Consistent tool versions across all checks
- Simpler debugging when failures occur

**Current Status:** 
- ✅ 84 tests passing
- ⏭️ 1 test skipped (`test_integrity_flag` - see Security section above)
- ✅ Black formatting passing
- ✅ Ruff linting passing (with deprecation warning)

**Tool Versions Pinned:**
- Black: 25.11.0 (ensures consistent formatting between CI and local)
- Ruff: 0.9.2 (stable linting rules)
- Python: 3.11.14 (on CI), 3.13.5 (local dev - compatible)

---

## Project Architecture Notes

### Tech Stack
- **Backend:** FastAPI (async Python web framework)
- **Database:** PostgreSQL + SQLAlchemy ORM with asyncpg driver
- **Testing:** pytest with async support (pytest-asyncio)
- **Linting:** Black (formatter) + Ruff (linter)
- **CI:** GitHub Actions

### Key Concepts
- **Sessions:** Workspace states (active/frozen/archived lifecycle)
- **Clips:** Point-in-time snapshots of session state
- **Memories:** User-created knowledge entries with importance ratings
- **Integrity:** HMAC signatures for tamper detection (partially implemented)

---

*Last Updated: 2025-11-22*  
*AI Assistant: Review this file when working on crecall to understand current state and deferred work.*
