# Quick Reference: GitHub Actions & Branch Protection

## 🎯 What You Have

### GitHub Actions Workflows (Already Deployed)
```
✅ test-and-coverage.yml      → Tests on Python 3.11, 3.12, 3.13
✅ code-quality.yml            → Black, isort, flake8, pylint
✅ security-checks.yml         → Bandit, Safety, Semgrep
```

### Where to View
- **Actions Tab**: https://github.com/nabaznyl/crecall/actions
- **Workflow Files**: `.github/workflows/` in repository

---

## ⚙️ Branch Protection Setup (5 Minutes)

### Quick Steps (on GitHub.com)

1. **Go to Settings**
   ```
   https://github.com/nabaznyl/crecall/settings/branches
   ```

2. **Click "Add rule"**

3. **Branch name: `main`**

4. **Enable these checkboxes:**
   ```
   ☑ Require a pull request before merging
   ☑ Require status checks to pass before merging
   ☑ Require code reviews before merging (1 approval)
   ☑ Require branches to be up to date before merging
   ☑ Dismiss stale pull request approvals
   ```

5. **Select these status checks:**
   ```
   ☑ test-and-coverage
   ☑ code-quality
   ☑ security-checks
   ```

6. **Click "Create"**

---

## 📋 PR Workflow After Setup

```
Create PR
   ↓
Workflows run automatically (2-3 min)
   ├─ Tests pass on all 3 Python versions ✅
   ├─ Code quality checks pass ✅
   └─ Security scan passes ✅
   ↓
Need 1 code review approval
   ↓
All checks pass + approved = Can merge ✅
```

---

## 🔍 Viewing Workflow Results

### In Pull Request
- See "Checks" tab in PR
- Click on specific check for details
- Red = Failed, Green = Passed

### In Actions Tab
- View all workflow runs
- See logs for each job
- Track history

---

## 💾 Local Commands

### Run tests locally (like CI/CD)
```bash
python -m pytest backend/tests -v --cov=backend/app
```

### Auto-fix code formatting
```bash
black backend/app backend/tests
isort backend/app backend/tests
```

### Check for linting issues
```bash
flake8 backend/app --max-line-length=120
```

### Security check locally
```bash
bandit -r backend/app --skip B101
safety check
```

---

## 🚨 If Workflows Fail

### Test Failures
- Check Python version match
- Run `pip install -r requirements.txt`
- Run tests locally first

### Code Quality Failures
- Run `black backend/`
- Run `isort backend/`
- Commit fixes and push

### Security Warnings
- Review Bandit output
- Check Safety report
- Update dependencies if needed

---

## 📚 Full Documentation

See: **GITHUB_ACTIONS_SETUP.md** in repository for:
- Complete setup guide
- Screenshots/examples
- Troubleshooting
- Status badges for README
- Monitoring tips

---

## ✅ Checklist

- [ ] Go to branch settings URL
- [ ] Add rule for "main" branch
- [ ] Enable PR requirement
- [ ] Enable status checks
- [ ] Select all 3 workflows
- [ ] Enable code review requirement
- [ ] Save settings
- [ ] Test with a PR

---

## 🎯 Test It Out

Once branch protection is enabled:

```bash
# Create test branch
git checkout -b test/feature

# Make small change
echo "# Test" >> README.md

# Commit and push
git add README.md
git commit -m "test: CI/CD test"
git push origin test/feature

# Create PR on GitHub
# Watch workflows run in "Checks" tab
# Verify merge is blocked until all pass
```

---

## 📞 Help Resources

- GitHub Docs: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches
- Actions Help: https://docs.github.com/en/actions
- Repository: https://github.com/nabaznyl/crecall

---

**Status**: CI/CD Ready ✅ | Branch Protection: Ready for setup ⏳
