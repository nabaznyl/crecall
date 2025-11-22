# GitHub Actions & Branch Protection Setup Guide

## 📋 Overview

This guide walks you through:
1. **GitHub Actions CI/CD** - Automated testing, code quality, and security checks
2. **Branch Protection Rules** - Enforce quality standards before merging

---

## Part 1: GitHub Actions CI/CD ✅ (Already Configured)

### What's Already Set Up

Three automated workflows have been created and pushed to your repository:

#### 1. **test-and-coverage.yml** - Test & Coverage Pipeline
```yaml
Triggers on: push to main/develop, pull requests
Python versions: 3.11, 3.12, 3.13
Checks:
  ✓ Run full test suite
  ✓ Generate coverage reports
  ✓ Upload to Codecov
  ✓ Generate coverage badges
```

**What it does:**
- Runs all 85 tests across 3 Python versions
- Generates coverage metrics
- Uploads to Codecov for tracking
- Reports test results

#### 2. **code-quality.yml** - Code Quality & Linting
```yaml
Triggers on: push to main/develop, pull requests
Python version: 3.13
Checks:
  ✓ Black (code formatting)
  ✓ isort (import sorting)
  ✓ flake8 (linting)
  ✓ pylint (static analysis)
```

**What it does:**
- Ensures consistent code formatting
- Checks import organization
- Validates Python style guidelines
- Detects potential bugs

#### 3. **security-checks.yml** - Security Scanning
```yaml
Triggers on: push to main/develop, pull requests, daily at 2 AM UTC
Checks:
  ✓ Bandit (security vulnerability scanner)
  ✓ Safety (dependency vulnerability check)
  ✓ Semgrep (static analysis security tool)
```

**What it does:**
- Scans for common security issues
- Checks for vulnerable dependencies
- Performs pattern-based security analysis
- Runs daily automatic checks

---

## How to Monitor GitHub Actions

### Step 1: View Workflow Results
1. Go to your repository: https://github.com/nabaznyl/crecall
2. Click **"Actions"** tab (top navigation)
3. See all workflow runs

### Step 2: Check Specific Workflow
1. Click on a workflow run (e.g., "Test & Coverage")
2. View detailed logs for each job
3. See pass/fail status per Python version

### Step 3: Interpret Results
- ✅ Green checkmark = All checks passed
- ❌ Red X = One or more checks failed
- ⏳ Yellow dot = Currently running

---

## Part 2: Configure Branch Protection Rules

### ⚠️ IMPORTANT: These Steps Must Be Done on GitHub.com

Branch protection rules **cannot be configured via CLI** - you must use the GitHub web interface.

### Step-by-Step Guide: Configure Branch Protection

#### **Step 1: Go to Repository Settings**
1. Open: https://github.com/nabaznyl/crecall
2. Click **"Settings"** (gear icon, top-right)
3. Left sidebar → Click **"Branches"**

#### **Step 2: Add Branch Protection Rule**
1. Click **"Add rule"** button
2. In "Branch name pattern" field, type: `main`
3. This protects the main branch

#### **Step 3: Enable Required Checks**

Under "Protect matching branches", check the following:

**✅ Require a pull request before merging**
- ☑ Require approvals: Set to **1 approval** minimum
- ☑ Dismiss stale pull request approvals when new commits are pushed
- ☑ Require approval of the most recent reviewable push

**✅ Require status checks to pass before merging**
- ☑ Require branches to be up to date before merging
- Find and select these workflows:
  - `test-and-coverage` (required)
  - `code-quality` (required)
  - `security-checks` (required)

**✅ Require code reviews before merging**
- ☑ Require code reviews before merging: **1 approval**
- ☑ Require review from Code Owners
- ☑ Restrict who can dismiss pull request reviews

**✅ Additional Security**
- ☑ Require passing tests (status checks)
- ☑ Include administrators: NO (admins can bypass)
- ☑ Require branches to be up to date before merging

#### **Step 4: Configure Dismissal**
- ☑ Dismiss stale pull request approvals when new commits are pushed
- ☑ Require review from Code Owners
- ☑ Require last pusher approval: Optional (strict mode)

#### **Step 5: Save**
- Click **"Create"** or **"Save changes"**
- Confirm by clicking **"I understand, update the branch protection rule"**

---

## Visual Workflow: What Happens When You Create a Pull Request

```
Developer creates PR on branch
    ↓
GitHub Actions automatically runs:
    ├─ test-and-coverage.yml     (Tests on Python 3.11, 3.12, 3.13)
    ├─ code-quality.yml           (Linting, formatting checks)
    └─ security-checks.yml        (Security vulnerability scan)
    ↓
All workflows must ✅ PASS
    ↓
Code review required: 1 approval minimum
    ↓
Once approved + all checks pass:
    └─→ "Merge" button becomes enabled
    ↓
PR can be merged to main
    ↓
Automatic deployment (if configured)
```

---

## Branch Protection Rules Summary

### What Gets Protected

| Check | What It Does | Status |
|-------|-------------|--------|
| **Pull Request Review** | Requires 1+ approval | ✅ Recommended |
| **Test Suite** | Must pass on Python 3.11, 3.12, 3.13 | ✅ Required |
| **Code Quality** | Black, isort, flake8, pylint checks | ✅ Required |
| **Security Scanning** | Bandit, Safety, Semgrep checks | ✅ Required |
| **Up-to-date Branch** | Must merge latest main before PR | ✅ Recommended |
| **Status Checks** | All required checks must pass | ✅ Required |

### Bypass Options

- **Admins can bypass**: If enabled, repository admins can force merge without passing checks
- **Recommended setting**: Disabled (enforce for everyone)

---

## Troubleshooting: Workflow Failures

### Test Failures
**Problem**: Tests fail in GitHub Actions but pass locally
**Solution**:
1. Check Python version (3.11 vs 3.12 vs 3.13)
2. Install exact requirements: `pip install -r requirements.txt`
3. Run: `python -m pytest backend/tests -v`

### Code Quality Failures
**Problem**: Linting errors reported in Actions
**Solution**:
```bash
# Auto-fix formatting
black backend/

# Auto-fix imports
isort backend/

# View linting issues
flake8 backend/ --max-line-length=120
```

### Security Check Failures
**Problem**: Bandit or Safety reports vulnerabilities
**Solution**:
1. Update dependencies: `pip install --upgrade -r requirements.txt`
2. For false positives: Add to `.bandit` file
3. For dependency issues: Check `safety check` output

---

## Helpful Commands for Local Testing

### Run Tests Locally (Like CI/CD Does)
```bash
cd /home/anonmaly/crecall

# Test on current Python version
python -m pytest backend/tests -v --cov=backend/app

# Format code
black backend/app backend/tests

# Sort imports
isort backend/app backend/tests

# Check linting
flake8 backend/app backend/tests --max-line-length=120
```

### Simulate Full CI/CD Locally
```bash
# Install all dev dependencies
pip install -r requirements.txt
pip install black isort flake8 pylint bandit safety

# Run all checks
python -m pytest backend/tests -v --cov=backend/app
black --check backend/app backend/tests
isort --check-only backend/app backend/tests
flake8 backend/app backend/tests --max-line-length=120
bandit -r backend/app --skip B101
```

---

## Next Steps

### Immediate (Today)
1. ✅ Workflow files pushed to GitHub
2. ⏳ **TODO**: Go to GitHub and enable branch protection on `main` branch
3. ⏳ **TODO**: Select required status checks (test-and-coverage, code-quality, security-checks)

### Short-term (This Week)
- Test by creating a PR with a small change
- Verify workflows run automatically
- Verify branch protection prevents merge until all checks pass

### Medium-term (This Month)
- Set up Codecov for coverage tracking
- Configure GitHub Pages for documentation
- Add deploy workflows (if needed for Phase 2)

---

## Quick Checklist: Branch Protection Setup

- [ ] Go to https://github.com/nabaznyl/crecall/settings/branches
- [ ] Click "Add rule"
- [ ] Enter branch pattern: `main`
- [ ] ✅ Require a pull request before merging (1 approval)
- [ ] ✅ Require status checks: test-and-coverage, code-quality, security-checks
- [ ] ✅ Require branches to be up to date
- [ ] ✅ Require code reviews before merging
- [ ] ✅ Dismiss stale PR approvals
- [ ] Click "Create"
- [ ] Verify: Try creating a PR and watch workflows run

---

## Monitoring & Badges

### Add Status Badges to README

Add this to the top of your README.md to show CI/CD status:

```markdown
[![Test & Coverage](https://github.com/nabaznyl/crecall/actions/workflows/test-and-coverage.yml/badge.svg)](https://github.com/nabaznyl/crecall/actions/workflows/test-and-coverage.yml)
[![Code Quality](https://github.com/nabaznyl/crecall/actions/workflows/code-quality.yml/badge.svg)](https://github.com/nabaznyl/crecall/actions/workflows/code-quality.yml)
[![Security Checks](https://github.com/nabaznyl/crecall/actions/workflows/security-checks.yml/badge.svg)](https://github.com/nabaznyl/crecall/actions/workflows/security-checks.yml)
```

---

## Summary

### ✅ Already Done (Locally)
- GitHub Actions workflows created and pushed
- `.github/workflows/` directory configured
- 3 workflows ready to run

### ⏳ TODO (On GitHub.com)
- Enable branch protection on `main` branch
- Select required workflows as status checks
- Test with a pull request

### 🎯 Benefits
- **Automated Testing**: Tests run on every PR
- **Code Quality**: Standards enforced automatically
- **Security**: Vulnerabilities caught early
- **Confidence**: Only quality code merges to main
- **Team Safety**: Prevents broken code from reaching main

---

**Status**: CI/CD workflows deployed ✅ | Branch protection rules pending (manual setup on GitHub.com)
