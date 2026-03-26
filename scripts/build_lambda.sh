#!/bin/bash

# Configuration
PACKAGE_NAME="lambda_bundle.zip"
BUILD_DIR="dist"
ENTRY_POINT="agent" # Change this to your source code directory

# 1. Clean up previous builds
echo "Cleaning up old build artifacts..."
rm -rf $BUILD_DIR

# 2. Create a clean build directory
mkdir $BUILD_DIR

# 3. Export dependencies using uv
# We export to requirements.txt format to ensure compatibility 
# with the --target flag in pip.
echo "Exporting dependencies..."
uv export --format requirements-txt --output-file $BUILD_DIR/requirements.txt

# 4. Install dependencies into the build directory
# We use pip here because 'uv pip install' supports the --target flag
# for creating standalone deployment folders.
echo "Installing dependencies to $BUILD_DIR..."
uv pip install -r $BUILD_DIR/requirements.txt --target $BUILD_DIR

# 4b. Remove large unnecessary dependencies
# These are only needed for the Temporal workflow option, not the AWS Lambdas.
echo "Removing large unnecessary dependencies from $BUILD_DIR..."
rm -rf $BUILD_DIR/temporalio
rm -rf $BUILD_DIR/grpc
rm -rf $BUILD_DIR/grpc_tools
rm -rf $BUILD_DIR/grpcio*
rm -rf $BUILD_DIR/debugpy # Not needed in production

# 5. Copy application code into the build directory
# Ensure your handler (e.g., lambda_function.py) is in the root of $BUILD_DIR
echo "Copying source code..."
cp -r $ENTRY_POINT/* $BUILD_DIR/

# 6. Clean up __pycache__, .pyc, .pyo etc.
echo "Cleaning up Python cache files..."
find $BUILD_DIR -type d -name "__pycache__" -exec rm -rf {} +
find $BUILD_DIR -type f -name "*.pyc" -delete
find $BUILD_DIR -type f -name "*.pyo" -delete
find $BUILD_DIR -type f -name "*.pyd" -delete # Optional, but can save space

# 6. Create the ZIP bundle
echo "Creating $PACKAGE_NAME..."
cd $BUILD_DIR
zip -r $PACKAGE_NAME .
cd ..

echo "Build complete: $PACKAGE_NAME"