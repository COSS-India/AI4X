#!/bin/bash

# Upload dhruva-observability package to TestPyPI

echo "🚀 Uploading dhruva-observability to TestPyPI..."

# Check if twine is installed
if ! command -v twine &> /dev/null; then
    echo "❌ twine is not installed. Installing..."
    pip install twine
fi

# Upload to TestPyPI
echo "📤 Uploading package to TestPyPI..."
twine upload --repository testpypi dist/*

echo "✅ Package uploaded successfully!"
echo ""
echo "🔗 TestPyPI URL: https://test.pypi.org/project/dhruva-observability/1.0.3/"
echo ""
echo "📦 Install with:"
echo "pip install -i https://test.pypi.org/simple/ dhruva-observability==1.0.3"
