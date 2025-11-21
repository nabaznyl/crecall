#!/usr/bin/env bash
# Nightly Build Script for crecall
# Automatically builds nightly versions with date-based versioning

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$PROJECT_ROOT/build-nightly"
DIST_DIR="$PROJECT_ROOT/dist-nightly"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Generate nightly version
DATE_STAMP=$(date +%Y%m%d)
GIT_SHORT_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
source "$PROJECT_ROOT/VERSION"
NIGHTLY_VERSION="${VERSION}-nightly-${DATE_STAMP}+${GIT_SHORT_SHA}"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   crecall Nightly Build${NC}"
echo -e "${BLUE}   ${NIGHTLY_VERSION}${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Clean previous builds
echo -e "\n${YELLOW}Cleaning previous nightly builds...${NC}"
rm -rf "$BUILD_DIR" "$DIST_DIR"
mkdir -p "$BUILD_DIR" "$DIST_DIR"

# Update version strings for nightly
echo -e "\n${YELLOW}Setting nightly version...${NC}"
sed -i.bak "s/version = \".*\"/version = \"${NIGHTLY_VERSION}\"/" "$PROJECT_ROOT/backend/pyproject.toml"
sed -i.bak "s/\"version\": \".*\"/\"version\": \"${NIGHTLY_VERSION}\"/" "$PROJECT_ROOT/frontend/package.json"
sed -i.bak "s/\"version\": \".*\"/\"version\": \"${NIGHTLY_VERSION}\"/" "$PROJECT_ROOT/vscode-extension/package.json"

# Build backend
echo -e "\n${YELLOW}Building backend...${NC}"
cd "$PROJECT_ROOT/backend"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip build wheel 2>&1 | grep -v "Requirement already satisfied" || true
python3 -m build --outdir "$DIST_DIR" 2>&1 | grep -v "warning" || true
deactivate

echo -e "${GREEN}✓ Backend built${NC}"

# Build frontend
echo -e "\n${YELLOW}Building frontend...${NC}"
cd "$PROJECT_ROOT/frontend"
npm ci --quiet 2>/dev/null || npm install --quiet
npm run build 2>&1 | grep -E "(Built|built|Bundle)" || true
cp -r dist "$BUILD_DIR/frontend"
echo -e "${GREEN}✓ Frontend built${NC}"

# Build VS Code extension
echo -e "\n${YELLOW}Building VS Code extension...${NC}"
cd "$PROJECT_ROOT/vscode-extension"
npm ci --quiet 2>/dev/null || npm install --quiet
npx vsce package --out "$DIST_DIR/crecall-${NIGHTLY_VERSION}.vsix" 2>&1 | grep -v "warning" || true
echo -e "${GREEN}✓ Extension packaged${NC}"

# Package CLI
echo -e "\n${YELLOW}Packaging CLI...${NC}"
mkdir -p "$BUILD_DIR/bin"
cp "$PROJECT_ROOT/bin/crecall" "$BUILD_DIR/bin/"
cp "$PROJECT_ROOT/bin/crecall-recover" "$BUILD_DIR/bin/"
chmod +x "$BUILD_DIR/bin/"*
echo -e "${GREEN}✓ CLI packaged${NC}"

# Create nightly tarball
echo -e "\n${YELLOW}Creating nightly tarball...${NC}"
cd "$BUILD_DIR"
tar -czf "$DIST_DIR/crecall-${NIGHTLY_VERSION}.tar.gz" .
cd "$PROJECT_ROOT"
echo -e "${GREEN}✓ Tarball created${NC}"

# Generate checksums
echo -e "\n${YELLOW}Generating checksums...${NC}"
cd "$DIST_DIR"
sha256sum * > SHA256SUMS.txt 2>/dev/null || true
cd "$PROJECT_ROOT"
echo -e "${GREEN}✓ Checksums generated${NC}"

# Restore original versions
echo -e "\n${YELLOW}Restoring version files...${NC}"
mv "$PROJECT_ROOT/backend/pyproject.toml.bak" "$PROJECT_ROOT/backend/pyproject.toml"
mv "$PROJECT_ROOT/frontend/package.json.bak" "$PROJECT_ROOT/frontend/package.json"
mv "$PROJECT_ROOT/vscode-extension/package.json.bak" "$PROJECT_ROOT/vscode-extension/package.json"

# Create build metadata
cat > "$DIST_DIR/BUILD_INFO.txt" << EOF
crecall Nightly Build
Version: ${NIGHTLY_VERSION}
Built: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
Commit: ${GIT_SHORT_SHA}
Branch: $(git branch --show-current 2>/dev/null || echo "unknown")
Builder: $(whoami)@$(hostname)
EOF

# Summary
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Nightly build complete!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "\nArtifacts in: ${DIST_DIR}"
ls -lh "$DIST_DIR" 2>/dev/null || true

echo -e "\n${YELLOW}Build info:${NC}"
cat "$DIST_DIR/BUILD_INFO.txt"
