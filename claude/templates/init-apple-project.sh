#!/bin/bash
set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

TEMPLATE_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE_FILE="${TEMPLATE_DIR}/apple-project.md"
TARGET_DIR=".claude"
TARGET_FILE="${TARGET_DIR}/CLAUDE.md"

echo -e "${CYAN}${BOLD}🍎 Apple Project — Claude Code Rules Setup${NC}"
echo ""

# Guard: abort if rules already exist
if [ -f "$TARGET_FILE" ]; then
    echo -e "${RED}✗ ${TARGET_FILE} already exists. Aborting.${NC}"
    echo -e "  Delete it manually if you want to re-initialize."
    exit 1
fi

# Guard: template must exist
if [ ! -f "$TEMPLATE_FILE" ]; then
    echo -e "${RED}✗ Template not found: ${TEMPLATE_FILE}${NC}"
    exit 1
fi

# --- Interactive prompts ---

# Project name
DEFAULT_NAME=$(basename "$(pwd)")
read -rp "$(echo -e "${BOLD}Project name${NC} [${DEFAULT_NAME}]: ")" PROJECT_NAME
PROJECT_NAME="${PROJECT_NAME:-$DEFAULT_NAME}"

# Platform
echo ""
echo -e "${BOLD}Platform:${NC}"
echo "  1) iOS"
echo "  2) macOS"
echo "  3) visionOS"
echo "  4) watchOS"
echo "  5) iOS + macOS (Multiplatform)"
echo "  6) All Apple Platforms"
read -rp "Select [1]: " PLATFORM_CHOICE
case "${PLATFORM_CHOICE:-1}" in
    1) PLATFORM="iOS" ;;
    2) PLATFORM="macOS" ;;
    3) PLATFORM="visionOS" ;;
    4) PLATFORM="watchOS" ;;
    5) PLATFORM="iOS, macOS (Multiplatform)" ;;
    6) PLATFORM="iOS, macOS, watchOS, visionOS (All Platforms)" ;;
    *) echo -e "${RED}Invalid choice${NC}"; exit 1 ;;
esac

# Distribution
echo ""
echo -e "${BOLD}Distribution:${NC}"
echo "  1) App Store"
echo "  2) TestFlight Only"
echo "  3) Enterprise (In-House)"
echo "  4) Ad Hoc / Development Only"
read -rp "Select [1]: " DIST_CHOICE
case "${DIST_CHOICE:-1}" in
    1) DISTRIBUTION="App Store"; IS_APPSTORE=true ;;
    2) DISTRIBUTION="TestFlight Only"; IS_APPSTORE=false ;;
    3) DISTRIBUTION="Enterprise (In-House)"; IS_APPSTORE=false ;;
    4) DISTRIBUTION="Ad Hoc / Development Only"; IS_APPSTORE=false ;;
    *) echo -e "${RED}Invalid choice${NC}"; exit 1 ;;
esac

# UI Framework
echo ""
echo -e "${BOLD}UI Framework:${NC}"
echo "  1) SwiftUI Only"
echo "  2) SwiftUI + UIKit"
echo "  3) UIKit Only"
read -rp "Select [1]: " UI_CHOICE
case "${UI_CHOICE:-1}" in
    1) UI_FRAMEWORK="SwiftUI Only" ;;
    2) UI_FRAMEWORK="SwiftUI + UIKit" ;;
    3) UI_FRAMEWORK="UIKit Only" ;;
    *) echo -e "${RED}Invalid choice${NC}"; exit 1 ;;
esac

# Minimum OS
echo ""
DEFAULT_MIN_OS="17.0"
read -rp "$(echo -e "${BOLD}Minimum OS version${NC} [${DEFAULT_MIN_OS}]: ")" MIN_OS
MIN_OS="${MIN_OS:-$DEFAULT_MIN_OS}"

# Architecture
echo ""
echo -e "${BOLD}Architecture:${NC}"
echo "  1) MVVM"
echo "  2) TCA (The Composable Architecture)"
echo "  3) MV (Observation-based)"
echo "  4) VIPER"
echo "  5) Other (specify)"
read -rp "Select [1]: " ARCH_CHOICE
case "${ARCH_CHOICE:-1}" in
    1) ARCHITECTURE="MVVM" ;;
    2) ARCHITECTURE="TCA (The Composable Architecture)" ;;
    3) ARCHITECTURE="MV (Observation-based)" ;;
    4) ARCHITECTURE="VIPER" ;;
    5) read -rp "Architecture name: " ARCHITECTURE ;;
    *) echo -e "${RED}Invalid choice${NC}"; exit 1 ;;
esac

# --- Generate ---

echo ""
echo -e "${YELLOW}Generating ${TARGET_FILE}...${NC}"

mkdir -p "$TARGET_DIR"

# Read template and replace placeholders
CONTENT=$(cat "$TEMPLATE_FILE")
CONTENT="${CONTENT//\{\{PROJECT_NAME\}\}/$PROJECT_NAME}"
CONTENT="${CONTENT//\{\{PLATFORM\}\}/$PLATFORM}"
CONTENT="${CONTENT//\{\{DISTRIBUTION\}\}/$DISTRIBUTION}"
CONTENT="${CONTENT//\{\{UI_FRAMEWORK\}\}/$UI_FRAMEWORK}"
CONTENT="${CONTENT//\{\{MIN_OS\}\}/$MIN_OS}"
CONTENT="${CONTENT//\{\{ARCHITECTURE\}\}/$ARCHITECTURE}"

# Process conditional App Store blocks
if [ "$IS_APPSTORE" = true ]; then
    # Remove IF_APPSTORE tags, keep content
    CONTENT=$(echo "$CONTENT" | sed '/{{#IF_APPSTORE}}/d' | sed '/{{\/IF_APPSTORE}}/d')
    # Remove entire IF_NOT_APPSTORE block
    CONTENT=$(echo "$CONTENT" | sed '/{{#IF_NOT_APPSTORE}}/,/{{\/IF_NOT_APPSTORE}}/d')
else
    # Remove entire IF_APPSTORE block
    CONTENT=$(echo "$CONTENT" | sed '/{{#IF_APPSTORE}}/,/{{\/IF_APPSTORE}}/d')
    # Remove IF_NOT_APPSTORE tags, keep content
    CONTENT=$(echo "$CONTENT" | sed '/{{#IF_NOT_APPSTORE}}/d' | sed '/{{\/IF_NOT_APPSTORE}}/d')
fi

echo "$CONTENT" > "$TARGET_FILE"

echo -e "${GREEN}${BOLD}✓ Done!${NC} Project rules created at ${TARGET_FILE}"
echo ""
echo -e "${CYAN}Summary:${NC}"
echo -e "  Project:      ${PROJECT_NAME}"
echo -e "  Platform:     ${PLATFORM}"
echo -e "  Distribution: ${DISTRIBUTION}"
echo -e "  UI:           ${UI_FRAMEWORK}"
echo -e "  Min OS:       ${MIN_OS}"
echo -e "  Architecture: ${ARCHITECTURE}"
echo ""
