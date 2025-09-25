#!/bin/bash

# Build and upload dhruva-observability package to TestPyPI

echo "🔧 Building dhruva-observability package..."

# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Build the package
python setup.py sdist bdist_wheel

echo "✅ Package built successfully!"

# Check the package
echo "🔍 Checking package..."
twine check dist/*

echo "📦 Package contents:"
ls -la dist/

echo "🚀 Ready to upload to TestPyPI!"
echo "Run: twine upload --repository testpypi dist/*"
