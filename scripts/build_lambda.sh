#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e
set -o pipefail

# Configuration
PACKAGE_NAME="lambda_bundle.zip"
BUILD_DIR="dist"
ENTRY_POINT="agent" # Change this to your source code directory

# 1. Clean up previous builds
echo "Cleaning up old build artifacts..."
rm -rf $BUILD_DIR
mkdir $BUILD_DIR

# 2. Export dependencies using uv for stepfunctions group only
# This ensures only stepfunctions-related deps are included in the Lambda
echo "Exporting stepfunctions dependencies..."
uv export --format requirements-txt --group stepfunctions --no-hashes --no-emit-project --output-file $BUILD_DIR/requirements.txt

# 3. Install dependencies into the build directory
# We use a standard Python Docker image with the linux/amd64 platform forced.
# This ensures we get x86_64 Linux binaries regardless of your Mac's architecture.
echo "Installing dependencies to $BUILD_DIR using Docker (Linux x86_64)..."
docker run --rm \
  --platform linux/amd64 \
  -v "$(pwd)/$BUILD_DIR":/var/task \
  -w /var/task \
  python:3.12-slim \
  pip install --no-cache-dir -r requirements.txt --target .

# 4. Copy application code into the build directory
echo "Copying source code..."
cp -r $ENTRY_POINT $BUILD_DIR/

# 5. Clean up Python cache files
echo "Cleaning up build artifacts..."
find $BUILD_DIR -type d -name "__pycache__" -exec rm -rf {} +
find $BUILD_DIR -type f -name "*.pyc" -delete
find $BUILD_DIR -type f -name "*.pyo" -delete

# 6. Create the ZIP bundle
echo "Creating $PACKAGE_NAME..."
cd $BUILD_DIR
zip -r $PACKAGE_NAME . -x "requirements*.txt" # Exclude requirements files from zip
cd ..

echo "Build complete: $PACKAGE_NAME"