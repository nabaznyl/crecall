#!/usr/bin/env bash
# Code Quality Check Script
# Run linters and formatters across the codebase

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

MODE=${1:-check}  # check or fix

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   crecall Code Quality Check${NC}"
echo -e "${BLUE}   Mode: ${MODE}${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

ERRORS=0

# ============================================================================
# Python Backend
# ============================================================================
echo -e "\n${YELLOW}Checking Python code...${NC}"

if command -v black &> /dev/null; then
    if [ "$MODE" = "fix" ]; then
        black "$PROJECT_ROOT/backend/app" "$PROJECT_ROOT/backend/migrations" && echo -e "${GREEN}✓ Black formatted${NC}" || { echo -e "${RED}✗ Black failed${NC}"; ERRORS=$((ERRORS+1)); }
    else
        black --check "$PROJECT_ROOT/backend/app" "$PROJECT_ROOT/backend/migrations" && echo -e "${GREEN}✓ Black check passed${NC}" || { echo -e "${YELLOW}! Black formatting needed${NC}"; ERRORS=$((ERRORS+1)); }
    fi
else
    echo -e "${YELLOW}! Black not installed (pip install black)${NC}"
fi

if command -v pylint &> /dev/null; then
    pylint "$PROJECT_ROOT/backend/app" --rcfile="$PROJECT_ROOT/pyproject.toml" 2>/dev/null && echo -e "${GREEN}✓ Pylint passed${NC}" || echo -e "${YELLOW}! Pylint warnings${NC}"
else
    echo -e "${YELLOW}! Pylint not installed (pip install pylint)${NC}"
fi

if command -v mypy &> /dev/null; then
    mypy "$PROJECT_ROOT/backend/app" --config-file="$PROJECT_ROOT/pyproject.toml" && echo -e "${GREEN}✓ Mypy passed${NC}" || echo -e "${YELLOW}! Mypy warnings${NC}"
else
    echo -e "${YELLOW}! Mypy not installed (pip install mypy)${NC}"
fi

# ============================================================================
# Frontend
# ============================================================================
echo -e "\n${YELLOW}Checking Frontend code...${NC}"

if [ -d "$PROJECT_ROOT/frontend/node_modules" ]; then
    cd "$PROJECT_ROOT/frontend"
    
    if [ "$MODE" = "fix" ]; then
        npm run lint:fix 2>&1 | grep -v "warning" && echo -e "${GREEN}✓ ESLint fixed${NC}" || echo -e "${YELLOW}! ESLint warnings${NC}"
        npm run format 2>&1 | grep -v "unchanged" && echo -e "${GREEN}✓ Prettier formatted${NC}" || echo -e "${GREEN}✓ Already formatted${NC}"
    else
        npm run lint 2>&1 | grep -v "warning" && echo -e "${GREEN}✓ ESLint passed${NC}" || { echo -e "${YELLOW}! ESLint warnings${NC}"; ERRORS=$((ERRORS+1)); }
        npm run format:check && echo -e "${GREEN}✓ Prettier check passed${NC}" || { echo -e "${YELLOW}! Prettier formatting needed${NC}"; ERRORS=$((ERRORS+1)); }
    fi
else
    echo -e "${YELLOW}! Frontend dependencies not installed (run: cd frontend && npm install)${NC}"
fi

# ============================================================================
# VS Code Extension
# ============================================================================
echo -e "\n${YELLOW}Checking Extension code...${NC}"

if [ -d "$PROJECT_ROOT/vscode-extension/node_modules" ]; then
    cd "$PROJECT_ROOT/vscode-extension"
    
    if [ "$MODE" = "fix" ]; then
        npm run lint:fix 2>&1 | grep -v "warning" && echo -e "${GREEN}✓ ESLint fixed${NC}" || echo -e "${YELLOW}! ESLint warnings${NC}"
        npm run format 2>&1 | grep -v "unchanged" && echo -e "${GREEN}✓ Prettier formatted${NC}" || echo -e "${GREEN}✓ Already formatted${NC}"
    else
        npm run lint 2>&1 | grep -v "warning" && echo -e "${GREEN}✓ ESLint passed${NC}" || { echo -e "${YELLOW}! ESLint warnings${NC}"; ERRORS=$((ERRORS+1)); }
        npm run format:check && echo -e "${GREEN}✓ Prettier check passed${NC}" || { echo -e "${YELLOW}! Prettier formatting needed${NC}"; ERRORS=$((ERRORS+1)); }
    fi
else
    echo -e "${YELLOW}! Extension dependencies not installed (run: cd vscode-extension && npm install)${NC}"
fi

# ============================================================================
# Summary
# ============================================================================
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}All checks passed!${NC}"
    exit 0
else
    echo -e "${YELLOW}Found $ERRORS issue(s)${NC}"
    if [ "$MODE" = "check" ]; then
        echo -e "\nRun ${BLUE}./scripts/lint.sh fix${NC} to auto-fix formatting issues"
    fi
    exit 1
fi
