#!/bin/bash
set -e

# Configuration
PROJECT_ROOT="$(pwd)"
DIST_DIR="${PROJECT_ROOT}/dist"
LAMBDA_BUNDLE="${DIST_DIR}/lambda_bundle.zip"
LAYER_BUNDLE="${DIST_DIR}/lambda_layer.zip"
CODE_DIR="${PROJECT_ROOT}/agent"

# 1. Prepare dist directory
echo "Cleaning and preparing ${DIST_DIR}..."
mkdir -p "${DIST_DIR}"
rm -f "${LAMBDA_BUNDLE}" "${LAYER_BUNDLE}"

# 2. Package Lambda Code
echo "Packaging Lambda code into ${LAMBDA_BUNDLE}..."
# Use python's built-in zip to ensure file permissions are preserved
# We want 'agent' to be at the root of the ZIP
python3 -m zipfile -c "${LAMBDA_BUNDLE}" agent/

# 3. Package Lambda Layer (Dependencies)
# We use 'uv' to compile and install dependencies for Lambda
if command -v uv &> /dev/null; then
    echo "Compiling dependencies for Lambda using uv..."
    uv pip compile pyproject.toml --python-version 3.11 --python-platform x86_64-manylinux_2_17 --output-file "${DIST_DIR}/requirements.txt"
    
    echo "Installing dependencies into temporary folder..."
    TEMP_LAYER_DIR="${DIST_DIR}/python_layer/python"
    mkdir -p "${TEMP_LAYER_DIR}"
    
    # Install into the python/ folder as required by AWS Lambda Layer structure
    pip install -r "${DIST_DIR}/requirements.txt" --target "${TEMP_LAYER_DIR}" --no-deps
    
    echo "Zipping layer..."
    cd "${DIST_DIR}/python_layer"
    zip -r "${LAYER_BUNDLE}" .
    cd "${PROJECT_ROOT}"
    
    echo "Lambda Layer created at ${LAYER_BUNDLE}"
else
    echo "uv not found. Please install dependencies and create a layer manually or install uv."
fi

echo "Build complete!"
echo "Function Bundle: ${LAMBDA_BUNDLE}"
