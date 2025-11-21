#!/usr/bin/env bash
# Build Script for crecall Stable Releases
# This script creates production-ready stable builds

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$PROJECT_ROOT/build"
DIST_DIR="$PROJECT_ROOT/dist"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Load version
source "$PROJECT_ROOT/VERSION"

if [ "$CHANNEL" != "stable" ]; then
    echo -e "${RED}Error: VERSION file must have CHANNEL=stable for stable builds${NC}"
    echo "Current channel: $CHANNEL"
    exit 1
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   crecall Stable Build v${FULL_VERSION}${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Clean previous builds
echo -e "\n${YELLOW}Cleaning previous builds...${NC}"
rm -rf "$BUILD_DIR" "$DIST_DIR"
mkdir -p "$BUILD_DIR" "$DIST_DIR"

# Build backend
echo -e "\n${YELLOW}Building backend...${NC}"
cd "$PROJECT_ROOT/backend"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv and install dependencies
source venv/bin/activate

# Install build tools
pip install --upgrade pip build wheel 2>&1 | grep -v "Requirement already satisfied" || true

if [ -f "pyproject.toml" ]; then
    python3 -m build --outdir "$DIST_DIR"
    echo -e "${GREEN}✓ Backend wheel built${NC}"
fi

deactivate

# Build frontend
echo -e "\n${YELLOW}Building frontend...${NC}"
cd "$PROJECT_ROOT/frontend"
if [ -f "package.json" ]; then
    npm ci --quiet
    npm run build
    cp -r dist "$BUILD_DIR/frontend"
    echo -e "${GREEN}✓ Frontend built${NC}"
fi

# Build VS Code extension
echo -e "\n${YELLOW}Building VS Code extension...${NC}"
cd "$PROJECT_ROOT/vscode-extension"
if [ -f "package.json" ]; then
    npm ci --quiet
    npx vsce package --out "$DIST_DIR/crecall-${FULL_VERSION}.vsix"
    echo -e "${GREEN}✓ VS Code extension packaged${NC}"
fi

# Copy CLI binaries
echo -e "\n${YELLOW}Packaging CLI binaries...${NC}"
mkdir -p "$BUILD_DIR/bin"
cp "$PROJECT_ROOT/bin/crecall" "$BUILD_DIR/bin/"
cp "$PROJECT_ROOT/bin/crecall-recover" "$BUILD_DIR/bin/"
chmod +x "$BUILD_DIR/bin/"*
echo -e "${GREEN}✓ CLI binaries packaged${NC}"

# Copy documentation
echo -e "\n${YELLOW}Packaging documentation...${NC}"
mkdir -p "$BUILD_DIR/docs"
cp "$PROJECT_ROOT/README.md" "$BUILD_DIR/docs/"
cp "$PROJECT_ROOT/INSTALL.md" "$BUILD_DIR/docs/"
cp "$PROJECT_ROOT/PATCH_NOTES.md" "$BUILD_DIR/docs/"
cp "$PROJECT_ROOT/SECURITY_PROTOCOLS.md" "$BUILD_DIR/docs/"
cp "$PROJECT_ROOT/BRAND_LICENSE_AGREEMENT.md" "$BUILD_DIR/docs/LICENSE.md"
echo -e "${GREEN}✓ Documentation packaged${NC}"

# Generate checksums
echo -e "\n${YELLOW}Generating checksums...${NC}"
cd "$DIST_DIR"
find . -type f -exec sha256sum {} \; > SHA256SUMS
cd "$PROJECT_ROOT"
echo -e "${GREEN}✓ Checksums generated${NC}"

# Create tarball
echo -e "\n${YELLOW}Creating release tarball...${NC}"
cd "$BUILD_DIR"
tar -czf "$DIST_DIR/crecall-${FULL_VERSION}.tar.gz" .
cd "$PROJECT_ROOT"
echo -e "${GREEN}✓ Tarball created${NC}"

# Build Debian package
if [ -d "$PROJECT_ROOT/debian" ]; then
    echo -e "\n${YELLOW}Building Debian package...${NC}"
    dpkg-buildpackage -us -uc -b
    mv ../crecall_*.deb "$DIST_DIR/" 2>/dev/null || true
    mv ../crecall_*.changes "$DIST_DIR/" 2>/dev/null || true
    mv ../crecall_*.buildinfo "$DIST_DIR/" 2>/dev/null || true
    echo -e "${GREEN}✓ Debian package built${NC}"
fi

# Summary
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Build complete!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "\nArtifacts in: ${DIST_DIR}"
ls -lh "$DIST_DIR"

echo -e "\n${YELLOW}Next steps:${NC}"
echo "  1. Review build artifacts"
echo "  2. Test installation: sudo dpkg -i dist/crecall_*.deb"
echo "  3. Sign release: gpg --detach-sign --armor dist/crecall-${FULL_VERSION}.tar.gz"
echo "  4. Create GitHub release and upload artifacts"
echo "  5. Tag release: git tag v${FULL_VERSION} && git push --tags"
