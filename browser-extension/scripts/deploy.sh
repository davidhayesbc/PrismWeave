#!/bin/bash
# PrismWeave Browser Extension Deployment Script
# Automates the build and packaging process for deployment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  PrismWeave Extension Deployment Helper   ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo ""

# Get version from package.json
VERSION=$(node -p "require('./package.json').version")
echo -e "${BLUE}📦 Current version: ${GREEN}${VERSION}${NC}"
echo ""

# Step 1: Ask for version bump
echo -e "${YELLOW}Step 1: Version Management${NC}"
echo "Current version: $VERSION"
echo "Do you want to bump the version? (y/n)"
read -r BUMP_VERSION

if [ "$BUMP_VERSION" = "y" ]; then
    echo "Select version bump type:"
    echo "  1) Patch (1.0.0 -> 1.0.1) - Bug fixes"
    echo "  2) Minor (1.0.0 -> 1.1.0) - New features"
    echo "  3) Major (1.0.0 -> 2.0.0) - Breaking changes"
    echo "  4) Custom version"
    read -r VERSION_TYPE

    case $VERSION_TYPE in
        1)
            npm version patch --no-git-tag-version
            ;;
        2)
            npm version minor --no-git-tag-version
            ;;
        3)
            npm version major --no-git-tag-version
            ;;
        4)
            echo "Enter new version (e.g., 1.2.3):"
            read -r NEW_VERSION
            npm version "$NEW_VERSION" --no-git-tag-version
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            exit 1
            ;;
    esac

    # Update version in manifest.json to match package.json
    NEW_VERSION=$(node -p "require('./package.json').version")
    node -e "const fs=require('fs'); const m=JSON.parse(fs.readFileSync('manifest.json')); m.version='$NEW_VERSION'; fs.writeFileSync('manifest.json', JSON.stringify(m, null, 2));"
    
    echo -e "${GREEN}✓ Version updated to: ${NEW_VERSION}${NC}"
    VERSION=$NEW_VERSION
else
    echo -e "${BLUE}Keeping version: ${VERSION}${NC}"
fi

echo ""

# Step 2: Run tests
echo -e "${YELLOW}Step 2: Running tests...${NC}"
if npm test; then
    echo -e "${GREEN}✓ All tests passed${NC}"
else
    echo -e "${RED}✗ Tests failed. Fix errors before deploying.${NC}"
    exit 1
fi

echo ""

# Step 3: Clean build
echo -e "${YELLOW}Step 3: Cleaning previous builds...${NC}"
npm run clean
echo -e "${GREEN}✓ Clean complete${NC}"

echo ""

# Step 4: Production build
echo -e "${YELLOW}Step 4: Building for production...${NC}"
if npm run build:prod; then
    echo -e "${GREEN}✓ Production build complete${NC}"
else
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
fi

echo ""

# Step 5: Package
echo -e "${YELLOW}Step 5: Creating ZIP package...${NC}"

# Create releases directory if it doesn't exist
mkdir -p releases

# Create versioned package name
PACKAGE_NAME="prismweave-extension-v${VERSION}.zip"
PACKAGE_PATH="releases/${PACKAGE_NAME}"

# Remove old package if exists
if [ -f "$PACKAGE_PATH" ]; then
    rm "$PACKAGE_PATH"
    echo "Removed existing package"
fi

# Navigate to dist directory and create zip
cd ../../dist/browser-extension
zip -r "../../browser-extension/$PACKAGE_PATH" ./*
cd ../../browser-extension

echo -e "${GREEN}✓ Package created: ${PACKAGE_PATH}${NC}"

# Get package size
PACKAGE_SIZE=$(du -h "$PACKAGE_PATH" | cut -f1)
echo -e "${BLUE}📊 Package size: ${PACKAGE_SIZE}${NC}"

echo ""

# Step 6: Verify package contents
echo -e "${YELLOW}Step 6: Verifying package contents...${NC}"
echo "Package contains:"
unzip -l "$PACKAGE_PATH" | head -n 20
echo "..."
echo -e "${GREEN}✓ Package verified${NC}"

echo ""

# Step 7: Summary
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           Deployment Package Ready         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Version:${NC}      ${GREEN}${VERSION}${NC}"
echo -e "${BLUE}Package:${NC}     ${GREEN}${PACKAGE_PATH}${NC}"
echo -e "${BLUE}Size:${NC}        ${GREEN}${PACKAGE_SIZE}${NC}"
echo ""

# Step 8: Next steps
echo -e "${YELLOW}Next Steps:${NC}"
echo ""
echo "1. ${BLUE}Test the package locally:${NC}"
echo "   - Chrome: chrome://extensions/ → Load unpacked → Select dist/browser-extension"
echo "   - Edge:   edge://extensions/ → Load unpacked → Select dist/browser-extension"
echo ""
echo "2. ${BLUE}Create GitHub release:${NC}"
echo "   git tag -a v${VERSION} -m 'Release v${VERSION}'"
echo "   git push origin v${VERSION}"
echo "   Then upload ${PACKAGE_PATH} to GitHub releases"
echo ""
echo "3. ${BLUE}Submit to stores:${NC}"
echo "   - Edge Add-ons: https://partner.microsoft.com/dashboard/microsoftedge"
echo "   - Chrome Web Store: https://chrome.google.com/webstore/devconsole"
echo ""
echo "4. ${BLUE}Update documentation:${NC}"
echo "   - Update README.md with new version"
echo "   - Update CHANGELOG.md"
echo "   - Update website download links"
echo ""

# Optional: Commit version changes
echo -e "${YELLOW}Do you want to commit the version changes? (y/n)${NC}"
read -r COMMIT_CHANGES

if [ "$COMMIT_CHANGES" = "y" ]; then
    git add package.json manifest.json
    git commit -m "chore: bump version to ${VERSION}"
    echo -e "${GREEN}✓ Changes committed${NC}"
    echo ""
    echo -e "${BLUE}Don't forget to push:${NC} git push origin main"
fi

echo ""
echo -e "${GREEN}✨ Deployment package ready!${NC}"
echo ""
