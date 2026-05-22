#!/usr/bin/env bash
# Build the standalone Calgary Social Services app (Mac / Linux)
# Usage: bash build.sh
set -e

echo "==> Installing build tools..."
uv add --dev pyinstaller pyinstaller-hooks-contrib

echo "==> Building..."
uv run pyinstaller Calgary-Services.spec --clean

echo ""
echo "==> Build complete: dist/Calgary-Services/"
echo ""
echo "To distribute:"
echo "  cd dist"
echo "  zip -r Calgary-Services-$(uname -s).zip Calgary-Services/"
echo ""
echo "Recipients: unzip and double-click Calgary-Services (or run ./Calgary-Services in terminal)"
