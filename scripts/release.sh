#!/usr/bin/env bash
# Release Automation Script
# Usage: ./scripts/release.sh [stable|nightly] [patch|minor|major]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

CHANNEL=${1:-stable}
BUMP_TYPE=${2:-patch}

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   crecall Release Automation${NC}"
echo -e "${BLUE}   Channel: ${CHANNEL} | Bump: ${BUMP_TYPE}${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Pre-flight checks
echo -e "\n${YELLOW}Running pre-flight checks...${NC}"

# Check git status
if [[ -n $(git status -s) ]]; then
    echo -e "${RED}Error: Working directory has uncommitted changes${NC}"
    git status -s
    exit 1
fi
echo -e "${GREEN}✓ Git working directory clean${NC}"

# Check if on main branch for stable releases
if [ "$CHANNEL" = "stable" ]; then
    CURRENT_BRANCH=$(git branch --show-current)
    if [ "$CURRENT_BRANCH" != "main" ]; then
        echo -e "${RED}Error: Stable releases must be from 'main' branch${NC}"
        echo "Current branch: $CURRENT_BRANCH"
        exit 1
    fi
    echo -e "${GREEN}✓ On main branch${NC}"
fi

# Version bump
echo -e "\n${YELLOW}Bumping version...${NC}"
"$SCRIPT_DIR/version-bump.sh" "$BUMP_TYPE" "$CHANNEL"

source "$PROJECT_ROOT/VERSION"
echo -e "${GREEN}✓ Version bumped to ${FULL_VERSION}${NC}"

# Update PATCH_NOTES.md
echo -e "\n${YELLOW}Please update PATCH_NOTES.md with changes for ${FULL_VERSION}${NC}"
read -p "Press Enter when PATCH_NOTES.md is updated..."

# Update debian/changelog for stable releases
if [ "$CHANNEL" = "stable" ]; then
    echo -e "\n${YELLOW}Please update debian/changelog${NC}"
    read -p "Press Enter when debian/changelog is updated..."
fi

# Run tests (if test suite exists)
if [ -f "$PROJECT_ROOT/backend/pytest.ini" ] || [ -d "$PROJECT_ROOT/backend/tests" ]; then
    echo -e "\n${YELLOW}Running tests...${NC}"
    cd "$PROJECT_ROOT/backend"
    python3 -m pytest -v || {
        echo -e "${RED}Tests failed! Aborting release.${NC}"
        exit 1
    }
    echo -e "${GREEN}✓ Tests passed${NC}"
fi

# Build release
echo -e "\n${YELLOW}Building release...${NC}"
if [ "$CHANNEL" = "stable" ]; then
    "$SCRIPT_DIR/build-stable.sh"
elif [ "$CHANNEL" = "nightly" ]; then
    "$SCRIPT_DIR/build-nightly.sh"
fi
echo -e "${GREEN}✓ Build complete${NC}"

# Commit version bump
echo -e "\n${YELLOW}Committing version bump...${NC}"
cd "$PROJECT_ROOT"
git add -A
git commit -m "Release ${FULL_VERSION}

- Bumped version to ${FULL_VERSION}
- Updated PATCH_NOTES.md
- Updated package metadata
$([ "$CHANNEL" = "stable" ] && echo "- Updated debian/changelog")"

echo -e "${GREEN}✓ Changes committed${NC}"

# Create git tag for stable releases
if [ "$CHANNEL" = "stable" ]; then
    echo -e "\n${YELLOW}Creating git tag...${NC}"
    git tag -a "v${FULL_VERSION}" -m "Release ${FULL_VERSION}"
    echo -e "${GREEN}✓ Tag created: v${FULL_VERSION}${NC}"
fi

# Summary
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Release preparation complete!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "\n${YELLOW}Next steps:${NC}"
if [ "$CHANNEL" = "stable" ]; then
    echo "  1. Push changes: git push origin main"
    echo "  2. Push tag: git push origin v${FULL_VERSION}"
    echo "  3. Create GitHub release with artifacts from dist/"
    echo "  4. Sign tarball: gpg --detach-sign --armor dist/crecall-${FULL_VERSION}.tar.gz"
    echo "  5. Upload to package repositories"
else
    echo "  1. Push changes: git push origin $(git branch --show-current)"
    echo "  2. Upload nightly build to distribution server"
    echo "  3. Update nightly download links"
fi

echo -e "\n${GREEN}Build artifacts:${NC}"
if [ "$CHANNEL" = "stable" ]; then
    ls -lh "$PROJECT_ROOT/dist/" 2>/dev/null || true
else
    ls -lh "$PROJECT_ROOT/dist-nightly/" 2>/dev/null || true
fi
