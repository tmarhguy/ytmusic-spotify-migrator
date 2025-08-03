#!/bin/bash
# Pre-commit cleanup script - Run before pushing to repository

set -e

echo "Running pre-commit cleanup..."

# Remove any accidentally created .env files
find . -name ".env" -not -path "./.git/*" -delete 2>/dev/null || true

# Remove build artifacts
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
find . -name ".coverage" -delete 2>/dev/null || true

# Remove node_modules if present
find . -name "node_modules" -type d -exec rm -rf {} + 2>/dev/null || true

# Remove common temp files
find . -name ".DS_Store" -delete 2>/dev/null || true
find . -name "*.log" -not -path "./.git/*" -delete 2>/dev/null || true
find . -name "*.tmp" -delete 2>/dev/null || true

# Remove development databases/caches
find . -name ".spotify_cache*" -delete 2>/dev/null || true
find . -name "*.sqlite*" -delete 2>/dev/null || true

echo "Cleanup complete!"
echo ""
echo "Project is ready for commit. Files to be committed:"
git status --porcelain
