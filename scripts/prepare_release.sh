#!/bin/bash
# Release Preparation Script
# This script prepares the codebase for a new release

set -e  # Exit on any error

echo "📦 Preparing Pai Note Exporter for release"
echo "==========================================="

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found. Please run this script from the project root."
    exit 1
fi

# Check if we're on main/master branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "master" ] && [ "$CURRENT_BRANCH" != "main" ]; then
    echo "⚠️  Warning: Not on main/master branch. Current branch: $CURRENT_BRANCH"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Error: There are uncommitted changes. Please commit or stash them first."
    git status --short
    exit 1
fi

echo "✅ Repository is clean"

# Run all checks
echo "🔍 Running pre-release checks..."

# Run tests
echo "Running tests..."
if ! pytest --cov=src/pai_note_exporter --cov-report=term-missing --cov-fail-under=80 -q; then
    echo "❌ Tests failed or coverage too low"
    exit 1
fi
echo "✅ Tests passed"

# Run linting
echo "Running linting..."
if ! ruff check src tests; then
    echo "❌ Linting failed"
    exit 1
fi
echo "✅ Linting passed"

# Run type checking
echo "Running type checking..."
if ! mypy src; then
    echo "❌ Type checking failed"
    exit 1
fi
echo "✅ Type checking passed"

# Run security check
echo "Running security check..."
if ! detect-secrets scan --baseline .secrets.baseline; then
    echo "❌ Security check failed"
    exit 1
fi
echo "✅ Security check passed"

# Run pre-commit on all files
echo "Running pre-commit checks..."
if ! pre-commit run --all-files; then
    echo "❌ Pre-commit checks failed"
    exit 1
fi
echo "✅ Pre-commit checks passed"

# Check version in pyproject.toml
CURRENT_VERSION=$(grep '^version =' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
echo "📋 Current version: $CURRENT_VERSION"

read -p "Enter new version (current: $CURRENT_VERSION): " NEW_VERSION

if [ -z "$NEW_VERSION" ]; then
    echo "❌ No version provided"
    exit 1
fi

# Validate version format
if ! echo "$NEW_VERSION" | grep -E '^[0-9]+\.[0-9]+\.[0-9]+$' > /dev/null; then
    echo "❌ Invalid version format. Use semantic versioning (e.g., 1.2.3)"
    exit 1
fi

# Update version in pyproject.toml
echo "Updating version in pyproject.toml..."
sed -i "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml
echo "✅ Version updated to $NEW_VERSION"

# Update CHANGELOG.md
echo "Checking CHANGELOG.md..."
if ! grep -q "$NEW_VERSION" CHANGELOG.md; then
    echo "⚠️  No entry found for version $NEW_VERSION in CHANGELOG.md"
    echo "Please add a changelog entry before proceeding."
    exit 1
fi
echo "✅ CHANGELOG.md contains entry for $NEW_VERSION"

# Build package
echo "Building package..."
rm -rf dist/
python -m build
echo "✅ Package built"

# Test installation
echo "Testing package installation..."
pip install --force-reinstall dist/*.whl
echo "✅ Package installation tested"

# Run a quick smoke test
echo "Running smoke test..."
python -c "import pai_note_exporter; print('✅ Import test passed')"
echo "✅ Smoke test passed"

# Create git tag
echo "Creating git tag..."
git add pyproject.toml
git commit -m "Release version $NEW_VERSION"
git tag -a "v$NEW_VERSION" -m "Release version $NEW_VERSION"
echo "✅ Git tag created: v$NEW_VERSION"

echo ""
echo "🎉 Release preparation complete!"
echo ""
echo "Next steps:"
echo "1. Push the changes: git push origin $CURRENT_BRANCH"
echo "2. Push the tag: git push origin v$NEW_VERSION"
echo "3. Create a GitHub release with the changelog"
echo "4. The CI/CD pipeline will build and publish the package"
echo ""
echo "Files created:"
echo "  - dist/*.whl"
echo "  - dist/*.tar.gz"
echo ""
echo "To undo this release preparation:"
echo "  git reset --hard HEAD~1"
echo "  git tag -d v$NEW_VERSION"
