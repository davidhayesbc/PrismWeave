#!/bin/bash

# PrismWeave CLI Setup Script
# This script helps you set up the CLI quickly

set -e

echo "🎨 PrismWeave CLI Setup"
echo "======================="
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed"
    echo "Please install Node.js 18 or higher from https://nodejs.org/"
    exit 1
fi

echo "✓ Node.js found: $(node --version)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is not installed"
    exit 1
fi

echo "✓ npm found: $(npm --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build the project
echo ""
echo "🔨 Building the project..."
npm run build

# Offer to install globally
echo ""
echo "✓ Build complete!"
echo ""
read -p "Do you want to install the CLI globally? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🌍 Installing globally..."
    npm link
    echo "✓ Global installation complete!"
    echo ""
    echo "You can now use 'prismweave' command from anywhere!"
else
    echo "Skipping global installation."
    echo "You can run commands with: npm start -- <command>"
fi

echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Configure GitHub credentials:"
echo "   prismweave config --set githubToken=your_token"
echo "   prismweave config --set githubRepo=owner/repo"
echo ""
echo "2. Test the connection:"
echo "   prismweave config --test"
echo ""
echo "3. Capture your first URL:"
echo "   prismweave capture https://example.com"
echo ""
echo "For more help, see README.md or run:"
echo "   prismweave --help"
echo "=========================================="
