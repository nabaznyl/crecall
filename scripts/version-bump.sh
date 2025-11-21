#!/usr/bin/env bash
# Version Bump Script for crecall
# Usage: ./scripts/version-bump.sh [patch|minor|major] [stable|nightly|dev]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VERSION_FILE="$PROJECT_ROOT/VERSION"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Load current version
source "$VERSION_FILE"

BUMP_TYPE=${1:-patch}
NEW_CHANNEL=${2:-$CHANNEL}

echo -e "${YELLOW}Current version: ${FULL_VERSION}${NC}"

# Parse current version
IFS='.' read -r MAJOR MINOR PATCH <<< "$VERSION"

# Bump version based on type
case $BUMP_TYPE in
    major)
        MAJOR=$((MAJOR + 1))
        MINOR=0
        PATCH=0
        BUILD_NUMBER=0
        ;;
    minor)
        MINOR=$((MINOR + 1))
        PATCH=0
        BUILD_NUMBER=0
        ;;
    patch)
        PATCH=$((PATCH + 1))
        BUILD_NUMBER=0
        ;;
    build)
        BUILD_NUMBER=$((BUILD_NUMBER + 1))
        ;;
    *)
        echo -e "${RED}Invalid bump type: $BUMP_TYPE${NC}"
        echo "Usage: $0 [major|minor|patch|build] [stable|nightly|dev]"
        exit 1
        ;;
esac

NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"
NEW_FULL_VERSION="${NEW_VERSION}-${NEW_CHANNEL}-${BUILD_NUMBER}"

echo -e "${GREEN}New version: ${NEW_FULL_VERSION}${NC}"

# Update VERSION file
cat > "$VERSION_FILE" << EOF
# crecall Version Information
# This file is the single source of truth for version numbers
# Format: MAJOR.MINOR.PATCH-CHANNEL
# Channels: stable, nightly, dev

VERSION=${NEW_VERSION}
CHANNEL=${NEW_CHANNEL}
BUILD_NUMBER=${BUILD_NUMBER}
FULL_VERSION=\${VERSION}-\${CHANNEL}-\${BUILD_NUMBER}

# Version history:
# ${NEW_FULL_VERSION}: (Add description)
EOF

# Update all version references
echo "Updating version in project files..."

# Backend pyproject.toml
if [ -f "$PROJECT_ROOT/backend/pyproject.toml" ]; then
    sed -i "s/^version = .*/version = \"${NEW_FULL_VERSION}\"/" "$PROJECT_ROOT/backend/pyproject.toml"
    echo "✓ Updated backend/pyproject.toml"
fi

# Backend main.py
if [ -f "$PROJECT_ROOT/backend/app/main.py" ]; then
    sed -i "s/version=\"[^\"]*\"/version=\"${NEW_FULL_VERSION}\"/" "$PROJECT_ROOT/backend/app/main.py"
    echo "✓ Updated backend/app/main.py"
fi

# Frontend package.json
if [ -f "$PROJECT_ROOT/frontend/package.json" ]; then
    sed -i "s/\"version\": \"[^\"]*\"/\"version\": \"${NEW_FULL_VERSION}\"/" "$PROJECT_ROOT/frontend/package.json"
    echo "✓ Updated frontend/package.json"
fi

# VS Code extension package.json
if [ -f "$PROJECT_ROOT/vscode-extension/package.json" ]; then
    sed -i "s/\"version\": \"[^\"]*\"/\"version\": \"${NEW_FULL_VERSION}\"/" "$PROJECT_ROOT/vscode-extension/package.json"
    echo "✓ Updated vscode-extension/package.json"
fi

# CLI binary
if [ -f "$PROJECT_ROOT/bin/crecall" ]; then
    sed -i "s/VERSION=\"[^\"]*\"/VERSION=\"${NEW_FULL_VERSION}\"/" "$PROJECT_ROOT/bin/crecall"
    echo "✓ Updated bin/crecall"
fi

# README.md
if [ -f "$PROJECT_ROOT/README.md" ]; then
    sed -i "s/Version: [0-9]\+\.[0-9]\+\.[0-9]\+-[a-z]\+-[0-9]\+/Version: ${NEW_FULL_VERSION}/" "$PROJECT_ROOT/README.md"
    echo "✓ Updated README.md"
fi

echo -e "${GREEN}Version bump complete!${NC}"
echo "Next steps:"
echo "  1. Update PATCH_NOTES.md with changes"
echo "  2. Update debian/changelog if building package"
echo "  3. Commit changes: git add -A && git commit -m 'Bump version to ${NEW_FULL_VERSION}'"
echo "  4. Tag release: git tag v${NEW_FULL_VERSION}"
