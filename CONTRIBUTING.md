# Contributing to crecall

Thank you for your interest in contributing to crecall! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Release Process](#release-process)

## Code of Conduct

Be respectful, collaborative, and constructive. We're all here to build something great together.

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 20+
- Git
- Docker (optional, for containerized development)

### Setting Up Development Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/crecall/crecall.git
   cd crecall
   ```

2. **Backend setup:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. **Frontend setup:**
   ```bash
   cd frontend
   npm install
   ```

4. **VS Code extension setup:**
   ```bash
   cd vscode-extension
   npm install
   ```

## Development Workflow

### Branch Strategy

- `main` - Stable releases only
- `develop` - Development branch, merge PRs here
- `feature/*` - Feature branches
- `fix/*` - Bug fix branches
- `release/*` - Release preparation branches

### Making Changes

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following our [coding standards](#coding-standards)

3. Run tests and linting:
   ```bash
   ./scripts/lint.sh check
   cd backend && pytest
   ```

4. Commit your changes:
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

5. Push and create a pull request:
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

Examples:
```
feat: add semantic search for memories
fix: correct clip resume state restoration
docs: update API documentation
test: add integration tests for context assembly
```

## Coding Standards

### Python (Backend)

- **Style Guide:** PEP 8, enforced by Black
- **Line Length:** 100 characters
- **Type Hints:** Use type hints for function signatures
- **Docstrings:** Google-style docstrings for all public functions

```python
def create_clip(session_id: int, name: str, content: dict) -> Clip:
    """
    Create a new clip for a session.

    Args:
        session_id: The ID of the session
        name: Name of the clip
        content: Clip content dictionary

    Returns:
        Created Clip object

    Raises:
        ValueError: If session_id is invalid
    """
    # implementation
```

**Run formatters:**
```bash
cd backend
black app/
isort app/
pylint app/
mypy app/
```

### TypeScript/JavaScript (Frontend & Extension)

- **Style Guide:** ESLint + Prettier
- **Line Length:** 100 characters
- **Naming:** camelCase for variables/functions, PascalCase for components
- **Imports:** Group and sort imports

**Run formatters:**
```bash
cd frontend  # or vscode-extension
npm run lint:fix
npm run format
```

### SQL/Database

- Use Alembic migrations for schema changes
- Never modify database directly in production
- Write reversible migrations

## Testing

### Running Tests

**Backend:**
```bash
cd backend
pytest                          # Run all tests
pytest -v                      # Verbose output
pytest --cov=app              # With coverage
pytest -m "not slow"          # Skip slow tests
pytest tests/test_sessions.py # Specific file
```

**Frontend:**
```bash
cd frontend
npm test
```

### Writing Tests

- **Unit tests** - Test individual functions/methods
- **Integration tests** - Test API endpoints and workflows
- **Coverage target** - Aim for 80%+ coverage on new code

Example test:
```python
def test_create_clip(client, sample_session_data):
    """Test creating a new clip"""
    session_response = client.post("/api/sessions/", json=sample_session_data)
    session_id = session_response.json()["id"]
    
    clip_data = {"session_id": session_id, "name": "test-clip"}
    response = client.post("/api/clips/", json=clip_data)
    
    assert response.status_code == 200
    assert response.json()["name"] == "test-clip"
```

## Submitting Changes

### Pull Request Process

1. **Update documentation** - If you changed APIs or behavior
2. **Add tests** - For new features or bug fixes
3. **Run full test suite** - Ensure nothing broke
4. **Update PATCH_NOTES.md** - Document your changes
5. **Create PR** - Use PR template, link related issues

### PR Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] PATCH_NOTES.md updated
- [ ] No merge conflicts
- [ ] Builds successfully

### After PR Approval

- Squash commits if requested
- Maintainer will merge to `develop`
- Delete feature branch after merge

## Release Process

Maintainers follow this process for releases:

### Stable Release

1. Update VERSION file to stable channel
2. Update PATCH_NOTES.md and debian/changelog
3. Run release automation:
   ```bash
   ./scripts/release.sh stable patch  # or minor, major
   ```
4. Script will:
   - Bump version
   - Run tests
   - Build artifacts
   - Create git tag
   - Generate changelog
5. Push changes and tag:
   ```bash
   git push origin main
   git push origin v0.x.x-stable-x
   ```
6. Create GitHub release with artifacts

### Nightly Build

Automated via GitHub Actions:
- Runs daily at 2 AM UTC
- Builds from `develop` branch
- Version: `0.x.x-nightly-YYYYMMDD+sha`
- Uploads to nightly distribution

## Project Structure

```
crecall/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/      # API routes
│   │   ├── db/       # Database models
│   │   └── services/ # Business logic
│   ├── migrations/   # Alembic migrations
│   └── tests/        # Backend tests
├── frontend/         # React frontend
│   └── src/
├── vscode-extension/ # VS Code extension
│   └── src/
├── bin/              # CLI scripts
├── scripts/          # Build & automation scripts
├── docs/             # Additional documentation
└── .github/
    └── workflows/    # CI/CD pipelines
```

## Getting Help

- **Issues:** Search existing issues or create new one
- **Discussions:** Use GitHub Discussions for questions
- **Documentation:** Check README.md and docs/

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see BRAND_LICENSE_AGREEMENT.md).

---

Thank you for contributing to crecall! 🚀
