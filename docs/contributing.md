# Contributing to crecall

Thank you for considering contributing to crecall! This guide will help you get started.

## Code of Conduct

Be respectful, constructive, and collaborative. We're building a tool to help people work better—let's model that in our community.

## Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/crecall.git
cd crecall
git remote add upstream https://github.com/nabaznyl/crecall.git
```

### 2. Set Up Development Environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

### 3. Install Pre-commit Hooks

```bash
# From repository root
pip install pre-commit
pre-commit install
```

This will run Black, Ruff, and security checks before every commit.

## Development Workflow

### Branch Strategy

- `main`: Frozen reference (never commit directly)
- `stablemain`: Rolling baseline (merge stable releases here)
- `stable`: Release candidate (tested features)
- `dev`: Integration branch (active development)
- `nightly`: Experimental features (bleeding edge)

### Creating a Feature Branch

```bash
git checkout dev
git pull upstream dev
git checkout -b feature/your-feature-name
```

### Making Changes

1. **Write tests first** (TDD encouraged)
2. **Run tests locally**:
   ```bash
   cd backend
   pytest -v
   ```
3. **Check formatting**:
   ```bash
   black app tests
   ruff check app tests
   ```
4. **Run type checking** (optional but recommended):
   ```bash
   mypy app
   ```

### Commit Guidelines

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add semantic search for memories
fix: resolve race condition in session creation
docs: update installation guide
test: add integrity verification test
chore: bump dependencies
```

### Pull Request Process

1. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Open a PR** against `dev` (not `main` or `stable`)

3. **PR checklist**:
   - [ ] Tests pass locally
   - [ ] New tests added for new features
   - [ ] Code formatted with Black
   - [ ] No Ruff violations
   - [ ] Updated relevant docs
   - [ ] Conventional commit messages
   - [ ] PR description explains "why" not just "what"

4. **Review process**:
   - CI must pass (quality, security scans, coverage)
   - At least one approving review
   - No merge conflicts

## Testing Standards

### Coverage Requirements

- **Minimum**: 80% overall coverage (enforced in CI)
- **New code**: Aim for 90%+ coverage
- **Critical paths**: 100% coverage (auth, data integrity)

### Test Organization

```
backend/tests/
├── test_api_*.py        # API endpoint tests
├── test_service_*.py    # Service layer tests
├── test_repository_*.py # Data layer tests
└── conftest.py          # Shared fixtures
```

### Writing Good Tests

```python
@pytest.mark.asyncio
async def test_clip_integrity_verification(session, signing_key):
    """Test that clip integrity is verified on retrieval."""
    # Arrange
    clip = await create_test_clip(session, content="test")
    
    # Act
    retrieved = await get_clip(clip.id)
    
    # Assert
    assert retrieved.integrity_status == "valid"
```

## Code Style

### Formatting
- **Black**: Auto-format all Python code (line length 88)
- **Ruff**: Linting (replaces flake8, isort, etc.)
- **Pre-commit**: Enforces style on commit

### Type Hints
- Use type hints for all public functions
- Pydantic models for API schemas
- mypy for static type checking (optional)

### Docstrings
```python
async def create_session(external_id: str) -> Session:
    """
    Create a new session with external identifier.
    
    Args:
        external_id: User-facing session identifier
    
    Returns:
        Created session with internal UUID
    
    Raises:
        ValueError: If external_id already exists
    """
    ...
```

## Security

### Reporting Vulnerabilities

**Do not open public issues for security vulnerabilities.**

Email security reports to: [security contact in SECURITY.md]

### Security Checklist

- [ ] No hardcoded secrets
- [ ] Validate all user inputs
- [ ] Use parameterized SQL queries
- [ ] HMAC signatures on sensitive data
- [ ] Dependencies scanned (pip-audit)

## Documentation

### When to Update Docs

- New features → Update relevant guides
- API changes → Update API reference
- Configuration changes → Update CONFIGURATION.md
- Breaking changes → Update CHANGELOG.md

### Documentation Structure

```
docs/
├── index.md              # Landing page
├── installation.md       # Setup guide
├── CONFIGURATION.md      # Settings reference
├── data_model.md         # Entity specs
├── workflows.md          # User journeys
├── DEVELOPMENT.md        # Developer guide
├── quality.md            # Testing standards
└── api/
    ├── rest.md           # API reference
    └── models.md         # Data models
```

## Release Process

Releases are automated via GitHub Actions:

1. Merge to `stable` triggers release workflow
2. Auto-increments tag (v.0.1.x.y format)
3. Builds wheel, sdist, SBOMs
4. Creates GitHub Release with artifacts
5. Publishes documentation (if configured)

## Getting Help

- **Questions**: Open a [GitHub Discussion](https://github.com/nabaznyl/crecall/discussions)
- **Bugs**: Open a [GitHub Issue](https://github.com/nabaznyl/crecall/issues) with reproduction steps
- **Features**: Start with a Discussion to gather feedback

## Recognition

Contributors will be recognized in:
- CHANGELOG.md release notes
- GitHub contributors page
- Annual contributor spotlight (planned)

---

**Thank you for contributing to crecall!** 🎉
