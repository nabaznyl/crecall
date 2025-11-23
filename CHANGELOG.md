# Changelog

All notable changes to crecall will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Consolidated CI/CD workflows into single unified workflow
- Improved documentation with TODO tracking and AI context
- Updated test count references (84 tests passing)

## [0.1.0-dev-7] - 2025-11-22

### Added
- Comprehensive test suite (84 passing tests)
- CI/CD workflow with Black, Ruff, and pytest
- TODO.md for tracking technical debt and future work
- License file (MIT)
- This changelog

### Changed
- Fixed all Ruff linting violations across codebase
- Standardized code formatting with Black 25.11.0
- Updated dependencies to pinned versions

### Fixed
- Code quality issues (E402, E501, E712, E741, F811, F841, I001, N806)
- CI/CD workflow failures due to tool version mismatches
- SQLAlchemy boolean comparison patterns

### Security
- Skipped integrity verification test (feature not yet implemented)

## [0.1.0-dev-6] - Previous

### Added
- Session lifecycle management (active/frozen/archived)
- Clip integrity signing with HMAC
- Memory importance ratings and search
- PostgreSQL migration support
- Professional build infrastructure (stable/nightly/dev channels)
- Crash-safe startup with deterministic background task gating
- Centralized configuration and structured logging

### Changed
- External vs internal identifier pattern implementation
- Async/sync test suite consolidation

---

[Unreleased]: https://github.com/nabaznyl/crecall/compare/v0.1.0-dev-7...HEAD
[0.1.0-dev-7]: https://github.com/nabaznyl/crecall/releases/tag/v0.1.0-dev-7
